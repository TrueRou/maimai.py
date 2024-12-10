import asyncio
import functools
import operator
import random
import re
from typing import TYPE_CHECKING

from httpx import AsyncClient, Cookies
from maimai_py import caches
from maimai_py import enums
from maimai_py.enums import FCType, FSType, LevelIndex, RateType, SongType
from maimai_py.exceptions import InvalidPlayerIdentifierError
from maimai_py.models import PlayerIdentifier, Score
from maimai_py.providers.base import IPlayerProvider, IScoreProvider
from maimai_py.utils import page_parser
from maimai_py.utils.coefficient import ScoreCoefficient

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class WechatProvider(IPlayerProvider, IScoreProvider):
    """The provider that fetches data from the Wahlap Wechat OffiAccount.

    PlayerIdentifier must have the `wechat_cookies` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.

    PlayerIdentifier should not be cached or stored in the database here, as the cookies may expire at any time.

    Wahlap Wechat OffiAccount: https://maimai.wahlap.com/maimai-mobile/
    """

    def _parse_score(score: dict, songs: MaimaiSongs) -> Score | None:
        if song := songs.by_title(score["title"]):
            is_utage = (len(song.difficulties.dx) + len(song.difficulties.standard)) == 0
            song_type = SongType.UTAGE if is_utage else enums.divingfish_to_type[score["type"]]
            level_index = LevelIndex(score["level_index"])
            if diff := song.get_diff(song_type, level_index):
                rating = ScoreCoefficient(score["achievements"]).ra(diff.level_value)
                return Score(
                    id=song.id,
                    song_name=score["title"],
                    level=score["level"],
                    level_index=level_index,
                    achievements=score["achievements"],
                    fc=FCType[score["fc"].upper()] if score["fc"] else None,
                    fs=FSType[score["fs"].upper()] if score["fs"] else None,
                    dx_score=score["dxScore"],
                    dx_rating=rating,
                    rate=RateType[score["rate"].upper()],
                    type=song_type,
                )

    async def _crawl_scores_diff(self, client: AsyncClient, diff: int, cookies: Cookies, songs: MaimaiSongs) -> list[Score]:
        await asyncio.sleep(random.randint(0, 100) / 1000)  # sleep for a random amount of time between 0 and 100ms
        resp1 = await client.get(f"https://maimai.wahlap.com/maimai-mobile/record/musicGenre/search/?genre=99&diff={diff}", cookies=cookies)
        body = re.search(r"<html.*?>([\s\S]*?)</html>", resp1.text).group(1).replace(r"\s+", " ")
        wm_json = page_parser.wmdx_html2json(body)
        return [parsed for score in wm_json if (parsed := self._parse_score(score, songs))]

    async def _crawl_scores(self, client: AsyncClient, cookies: Cookies, songs: MaimaiSongs) -> list[Score]:
        tasks = [self._crawl_scores_diff(client, diff, cookies, songs) for diff in [0, 1, 2, 3, 4]]
        results = await asyncio.gather(*tasks)
        return functools.reduce(operator.concat, results, [])

    async def get_player(self, identifier, client):
        return await super().get_player(identifier, client)

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        if not identifier.wechat_cookies:
            raise InvalidPlayerIdentifierError("Wahlap wechat cookies are required to fetch scores")
        songs = caches.cached_songs if caches.cached_songs else await client.songs()
        return await self._crawl_scores(client._client, identifier.wechat_cookies, songs)

    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient"):
        # Wahlap wechat doesn't represent best scores, we have no way to access them directly
        # Return (None, None) will call the main client to handle this, which will then fetch all scores instead
        return None, None
