from typing import TYPE_CHECKING
from httpx import AsyncClient
from maimai_ffi import arcade
from maimai_py import caches
from maimai_py.enums import FCType, FSType, LevelIndex, RateType, SongType
from maimai_py.exceptions import InvalidPlayerIdentifierError
from maimai_py.models import ArcadeResponse, PlayerIdentifier, Score
from maimai_py.providers.base import IPlayerProvider, IScoreProvider

from maimai_py.providers.lxns import LXNSProvider
from maimai_py.utils.coefficient import ScoreCoefficient

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiSongs


class ArcadeProvider(IPlayerProvider, IScoreProvider):
    """The provider that fetches data from the wahlap maimai arcade.

    This part of the maimai.py is not open-source, we distribute the compiled version of this part of the code as maimai_ffi.

    Feel free to ask us to solve if your platform or architecture is not supported.

    maimai.ffi: https://pypi.org/project/maimai-ffi
    """

    def _deser_score(score: dict, songs: "MaimaiSongs") -> Score | None:
        song_type = SongType._from_id(score["musicId"])
        level_index = LevelIndex(score["level"]) if song_type != SongType.UTAGE else None
        achievement = float(score["achievement"]) / 10000
        if song := songs.by_id(score["musicId"] % 10000):
            if diff := song._get_difficulty(song_type, level_index):
                return Score(
                    id=song.id,
                    song_name=song.title,
                    level=diff.level,
                    level_index=diff.level_index,
                    achievements=achievement,
                    fc=FCType(4 - score["comboStatus"]) if score["comboStatus"] != 0 else None,
                    fs=FSType(score["syncStatus"]) if score["syncStatus"] not in [0, 5] else FSType.SYNC if score["comboStatus"] == 5 else None,
                    dx_score=score["deluxscoreMax"],
                    dx_rating=ScoreCoefficient(achievement).ra(diff.level_value),
                    rate=RateType._from_achievement(achievement),
                    type=song_type,
                )

    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient):
        return await super().get_player(identifier, client)

    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        if not identifier.credentials:
            raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")
        resp: ArcadeResponse = await arcade.get_user_scores(identifier.credentials.encode())
        ArcadeResponse._throw_error(resp)
        if not caches.cached_songs:
            # This breaks the abstraction of the provider, but we have no choice
            caches.cached_songs = await LXNSProvider().get_songs(client)
        return [ArcadeProvider._deser_score(score, caches.cached_songs) for score in resp.data]

    async def get_scores_best(self, identifier: PlayerIdentifier, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        # Return (None, None) will call the main client to handle this, which will then fetch all scores instead
        return None, None
