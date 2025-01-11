from datetime import datetime
from httpx import AsyncClient
from maimai_ffi import arcade

from maimai_py.enums import *
from maimai_py.models import *
from maimai_py.utils import ScoreCoefficient
from maimai_py.providers import IPlayerProvider, IRegionProvider, IScoreProvider
from maimai_py.exceptions import InvalidPlayerIdentifierError


class ArcadeProvider(IPlayerProvider, IScoreProvider, IRegionProvider):
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
        if not identifier.credentials:
            raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")
        resp: ArcadeResponse = await arcade.get_user_preview(identifier.credentials.encode())
        ArcadeResponse._throw_error(resp)
        return ArcadePlayer(
            name=resp.data["userName"],
            rating=resp.data["playerRating"],
            is_login=resp.data["isLogin"],
            name_plate=resp.data["nameplateId"],
            icon=resp.data["iconId"],
            trophy=resp.data["trophyId"],
        )

    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        if not identifier.credentials:
            raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")
        resp: ArcadeResponse = await arcade.get_user_scores(identifier.credentials.encode())
        ArcadeResponse._throw_error(resp)
        msongs: MaimaiSongs = await MaimaiSongs._get_or_fetch()
        return [ArcadeProvider._deser_score(score, msongs) for score in resp.data]

    async def get_regions(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[PlayerRegion]:
        if not identifier.credentials:
            raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")
        resp: ArcadeResponse = await arcade.get_user_region(identifier.credentials.encode())
        ArcadeResponse._throw_error(resp)
        return [
            PlayerRegion(
                region_id=region["regionId"],
                region_name=region["regionName"],
                play_count=region["playCount"],
                created_at=datetime.strptime(region["created"], "%Y-%m-%d %H:%M:%S"),
            )
            for region in resp.data["userRegionList"]
        ]
