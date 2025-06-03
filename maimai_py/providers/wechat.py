import asyncio
import functools
import hashlib
import operator
import random
from typing import TYPE_CHECKING

from httpx import Cookies

from maimai_py.enums import *
from maimai_py.exceptions import InvalidPlayerIdentifierError
from maimai_py.models import *
from maimai_py.providers.base import IScoreProvider
from maimai_py.utils import ScoreCoefficient, wmdx_html2json

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class WechatProvider(IScoreProvider):
    """The provider that fetches data from the Wahlap Wechat OffiAccount.

    PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.

    PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

    Wahlap Wechat OffiAccount: https://maimai.wahlap.com/maimai-mobile/
    """

    def _hash(self) -> str:
        return hashlib.md5(b"wechat").hexdigest()

    @staticmethod
    async def _deser_score(score: dict, songs: "MaimaiSongs") -> Score | None:
        if song := await songs.by_title(score["title"]):
            is_utage = (len(song.difficulties.dx) + len(song.difficulties.standard)) == 0
            song_type = SongType.STANDARD if score["type"] == "SD" else SongType.DX if score["type"] == "DX" and not is_utage else SongType.UTAGE
            level_index = LevelIndex(score["level_index"])
            if diff := song.get_difficulty(song_type, level_index):
                rating = ScoreCoefficient(score["achievements"]).ra(diff.level_value)
                return Score(
                    id=song.id,
                    level=score["level"],
                    level_index=level_index,
                    achievements=score["achievements"],
                    fc=FCType[score["fc"].upper()] if score["fc"] else None,
                    fs=FSType[score["fs"].upper().replace("FDX", "FSD")] if score["fs"] else None,
                    dx_score=score["dxScore"],
                    dx_rating=rating,
                    rate=RateType[score["rate"].upper()],
                    type=song_type,
                )

    async def _crawl_scores_diff(self, client: "MaimaiClient", diff: int, cookies: Cookies, songs: "MaimaiSongs") -> list[Score]:
        await asyncio.sleep(random.randint(0, 300) / 1000)  # sleep for a random amount of time between 0 and 300ms
        resp1 = await client._client.get(f"https://maimai.wahlap.com/maimai-mobile/record/musicGenre/search/?genre=99&diff={diff}", cookies=cookies)
        # body = re.search(r"<html.*?>([\s\S]*?)</html>", resp1.text).group(1).replace(r"\s+", " ")
        wm_json = wmdx_html2json(resp1.text)
        return [json for score in wm_json if (json := await WechatProvider._deser_score(score, songs))]

    async def _crawl_scores(self, client: "MaimaiClient", cookies: Cookies, songs: "MaimaiSongs") -> Sequence[Score]:
        tasks = [self._crawl_scores_diff(client, diff, cookies, songs) for diff in [0, 1, 2, 3, 4]]
        results = await asyncio.gather(*tasks)
        return functools.reduce(operator.concat, results, [])

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()
        if not identifier.credentials or not isinstance(identifier.credentials, Cookies):
            raise InvalidPlayerIdentifierError("Wahlap wechat cookies are required to fetch scores")
        scores = await self._crawl_scores(client, identifier.credentials, maimai_songs)
        return list(scores)
