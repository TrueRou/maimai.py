import asyncio
import functools
import hashlib
import operator
import random
from typing import TYPE_CHECKING

from httpx import Cookies, RequestError
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from maimai_py.models import *
from maimai_py.utils import HTMLScore, ScoreCoefficient, wmdx_html2score
from maimai_py.utils.page_parser import wmdx_html2player, wmdx_html2players, wmdx_html2record

from .base import IPlayerIdentifierProvider, IPlayerProvider, IRecordProvider, IScoreProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class WechatProvider(IScoreProvider, IPlayerProvider, IPlayerIdentifierProvider, IRecordProvider):
    """The provider that fetches data from the Wahlap Wechat OffiAccount.

    PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.

    PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

    Wahlap Wechat OffiAccount: https://maimai.wahlap.com/maimai-mobile/
    """

    def _hash(self) -> str:
        return hashlib.md5(b"wechat").hexdigest()

    @staticmethod
    def _ensure_cookies(identifier: PlayerIdentifier) -> Cookies:
        if isinstance(identifier.credentials, dict):
            return Cookies(identifier.credentials)
        if isinstance(identifier.credentials, Cookies):
            return identifier.credentials
        raise InvalidPlayerIdentifierError("Wahlap wechat cookies are required to fetch data")

    @staticmethod
    async def _deser_score(score: HTMLScore, songs: "MaimaiSongs") -> Optional[Score]:
        if song := await songs.by_title(score.title):
            is_utage = (len(song.difficulties.dx) + len(song.difficulties.standard)) == 0
            song_type = (
                SongType.STANDARD
                if score.type == "SD"
                else SongType.DX
                if score.type == "DX" and not is_utage
                else SongType.UTAGE
            )
            level_index = LevelIndex(score.level_index)
            if diff := song.get_difficulty(song_type, level_index):
                rating = ScoreCoefficient(score.achievements).ra(diff.level_value)
                return Score(
                    id=song.id,
                    level=diff.level,
                    level_index=level_index,
                    achievements=score.achievements,
                    fc=FCType[score.fc.upper()] if score.fc else None,
                    fs=FSType[score.fs.upper().replace("FDX", "FSD")] if score.fs else None,
                    dx_score=score.dx_score,
                    dx_rating=rating,
                    play_count=None,
                    play_time=score.play_time,
                    rate=RateType[score.rate.upper()],
                    type=song_type,
                )

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def _crawl_scores_diff(
        self, client: "MaimaiClient", diff: int, cookies: Cookies, maimai_songs: "MaimaiSongs"
    ) -> list[Score]:
        await asyncio.sleep(random.randint(0, 300) / 1000)  # sleep for a random amount of time between 0 and 300ms
        resp1 = await client._client.get(
            f"https://maimai.wahlap.com/maimai-mobile/record/musicGenre/search/?genre=99&diff={diff}", cookies=cookies
        )
        if resp1.status_code == 302:
            raise InvalidPlayerIdentifierError(
                "Failed to fetch scores, possibly due to invalid cookies or maintenance."
            )
        scores = wmdx_html2score(str(resp1.text))
        return [r for score in scores if (r := await WechatProvider._deser_score(score, maimai_songs))]

    async def _crawl_scores(
        self, client: "MaimaiClient", cookies: Cookies, maimai_songs: "MaimaiSongs"
    ) -> Sequence[Score]:
        tasks = [
            asyncio.create_task(self._crawl_scores_diff(client, diff, cookies, maimai_songs))
            for diff in [0, 1, 2, 3, 4]
        ]
        results = await asyncio.gather(*tasks)
        return functools.reduce(operator.concat, results, [])

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()  # Ensure songs are loaded in cache
        scores = await self._crawl_scores(client, self._ensure_cookies(identifier), maimai_songs)
        return list(scores)

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> WechatPlayer:
        trophies = await client.items(PlayerTrophy)
        resp = await client._client.get(
            "https://maimai.wahlap.com/maimai-mobile/friend/userFriendCode/", cookies=self._ensure_cookies(identifier)
        )
        if resp.status_code == 302:
            raise InvalidPlayerIdentifierError(
                "Failed to fetch player information, possibly due to invalid cookies or maintenance."
            )
        player = wmdx_html2player(str(resp.text))
        return WechatPlayer(
            name=player.name,
            rating=player.rating,
            friend_code=player.friend_code,
            star=player.star,
            trophy=trophy[0] if (trophy := await trophies.filter(name=player.trophy_text)) else None,
            token=None,
        )

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_identifier(self, code: Union[str, dict[str, str]], client: "MaimaiClient") -> PlayerIdentifier:
        wechat_ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)"

        if isinstance(code, dict) and all([code.get("r"), code.get("t"), code.get("code"), code.get("state")]):
            headers = {
                "Host": "tgk-wcaime.wahlap.com",
                "Upgrade-Insecure-Requests": "1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            resp = await client._client.get(
                "https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx",
                headers={"User-Agent": wechat_ua, **headers},
                params=code,
            )
            if resp.status_code == 302 and resp.next_request:
                resp_next = await client._client.get(resp.next_request.url, headers={"User-Agent": wechat_ua})
                print(resp_next)
                return PlayerIdentifier(credentials=dict(resp_next.cookies))
            else:
                raise InvalidWechatTokenError("Invalid or expired Wechat token")
        raise InvalidWechatTokenError(
            "Invalid Wechat token format, expected a dict with 'r', 't', 'code', and 'state' keys"
        )

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_friends(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[WechatPlayer]:
        trophies = await client.items(PlayerTrophy)
        cookies = self._ensure_cookies(identifier)
        # Prefetch the first page of friends, in order to get the total number of friends
        resp = await client._client.get("https://maimai.wahlap.com/maimai-mobile/friend/", cookies=cookies)
        if resp.status_code == 302:
            raise InvalidPlayerIdentifierError(
                "Failed to fetch friends, possibly due to invalid cookies or maintenance."
            )
        friend_num, players = wmdx_html2players(str(resp.text))
        # Fetch all friends by iterating through pages, 10 friends per page
        for page in range(2, (friend_num // 10) + 2):
            resp = await client._client.get(
                f"https://maimai.wahlap.com/maimai-mobile/friend/pages/?idx={page}", cookies=cookies
            )
            players.extend(wmdx_html2players(str(resp.text))[1])
        return [
            WechatPlayer(
                name=player.name,
                rating=player.rating,
                friend_code=player.friend_code,
                star=player.star,
                token=player.token,
                trophy=trophy[0] if (trophy := await trophies.filter(name=player.trophy_text)) else None,
            )
            for player in players
        ]

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def set_rival_on(self, identifier: PlayerIdentifier, rival: WechatPlayer, client: "MaimaiClient") -> None:
        resp = await client._client.post(
            "https://maimai.wahlap.com/maimai-mobile/friend/rivalOn/",
            cookies=self._ensure_cookies(identifier),
            data={"idx": rival.friend_code, "token": rival.token},
        )
        resp.raise_for_status()

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def set_rival_off(self, identifier: PlayerIdentifier, rival: WechatPlayer, client: "MaimaiClient") -> None:
        resp = await client._client.post(
            "https://maimai.wahlap.com/maimai-mobile/friend/rivalOff/",
            cookies=self._ensure_cookies(identifier),
            data={"idx": rival.friend_code, "token": rival.token},
        )
        resp.raise_for_status()

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_records(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()  # Ensure songs are loaded in cache
        resp = await client._client.get(
            "https://maimai.wahlap.com/maimai-mobile/record/", cookies=self._ensure_cookies(identifier)
        )
        if resp.status_code == 302:
            raise InvalidPlayerIdentifierError(
                "Failed to fetch records, possibly due to invalid cookies or maintenance."
            )
        scores = wmdx_html2record(str(resp.text))
        return [r for score in scores if (r := await WechatProvider._deser_score(score, maimai_songs))]
