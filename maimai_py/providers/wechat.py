import asyncio
import functools
import hashlib
import operator
import random
from typing import TYPE_CHECKING

from httpx import Cookies

from maimai_py.models import *
from maimai_py.models import PlayerIdentifier
from maimai_py.utils import HTMLScore, ScoreCoefficient, wmdx_html2json

from .base import IPlayerIdentifierProvider, IScoreProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class WechatProvider(IScoreProvider, IPlayerIdentifierProvider):
    """The provider that fetches data from the Wahlap Wechat OffiAccount.

    PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.

    PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

    Wahlap Wechat OffiAccount: https://maimai.wahlap.com/maimai-mobile/
    """

    def _hash(self) -> str:
        return hashlib.md5(b"wechat").hexdigest()

    @staticmethod
    async def _deser_score(score: HTMLScore, songs: "MaimaiSongs") -> Optional[Score]:
        if song := await songs.by_title(score.title):
            is_utage = (len(song.difficulties.dx) + len(song.difficulties.standard)) == 0
            song_type = SongType.STANDARD if score.type == "SD" else SongType.DX if score.type == "DX" and not is_utage else SongType.UTAGE
            level_index = LevelIndex(score.level_index)
            if diff := song.get_difficulty(song_type, level_index):
                rating = ScoreCoefficient(score.achievements).ra(diff.level_value)
                return Score(
                    id=song.id,
                    level=score.level,
                    level_index=level_index,
                    achievements=score.achievements,
                    fc=FCType[score.fc.upper()] if score.fc else None,
                    fs=FSType[score.fs.upper().replace("FDX", "FSD")] if score.fs else None,
                    dx_score=score.dx_score,
                    dx_rating=rating,
                    play_count=None,
                    rate=RateType[score.rate.upper()],
                    type=song_type,
                )

    async def _crawl_scores_diff(self, client: "MaimaiClient", diff: int, cookies: Cookies, maimai_songs: "MaimaiSongs") -> list[Score]:
        await asyncio.sleep(random.randint(0, 300) / 1000)  # sleep for a random amount of time between 0 and 300ms
        resp1 = await client._client.get(f"https://maimai.wahlap.com/maimai-mobile/record/musicGenre/search/?genre=99&diff={diff}", cookies=cookies)
        scores: list[HTMLScore] = wmdx_html2json(str(resp1.text))
        return [r for score in scores if (r := await WechatProvider._deser_score(score, maimai_songs))]

    async def _crawl_scores(self, client: "MaimaiClient", cookies: Cookies, maimai_songs: "MaimaiSongs") -> Sequence[Score]:
        tasks = [asyncio.create_task(self._crawl_scores_diff(client, diff, cookies, maimai_songs)) for diff in [0, 1, 2, 3, 4]]
        results = await asyncio.gather(*tasks)
        return functools.reduce(operator.concat, results, [])

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()  # Ensure songs are loaded in cache
        if not identifier.credentials or not isinstance(identifier.credentials, Cookies):
            raise InvalidPlayerIdentifierError("Wahlap wechat cookies are required to fetch scores")
        scores = await self._crawl_scores(client, identifier.credentials, maimai_songs)
        return list(scores)

    async def get_identifier(self, code: Union[str, dict[str, str]], client: "MaimaiClient") -> PlayerIdentifier:
        if isinstance(code, dict) and all([code.get("r"), code.get("t"), code.get("code"), code.get("state")]):
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
                "Host": "tgk-wcaime.wahlap.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            }
            resp = await client._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=code, headers=headers)
            if resp.status_code == 302 and resp.next_request:
                resp_next = await client._client.get(resp.next_request.url, headers=headers)
                return PlayerIdentifier(credentials=resp_next.cookies)
            else:
                raise InvalidWechatTokenError("Invalid or expired Wechat token")
        raise InvalidWechatTokenError("Invalid Wechat token format, expected a dict with 'r', 't', 'code', and 'state' keys")
