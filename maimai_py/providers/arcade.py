import hashlib
from datetime import datetime
from typing import TYPE_CHECKING

from maimai_ffi import arcade

from maimai_py.models import *
from maimai_py.utils import ScoreCoefficient

from .base import IPlayerIdentifierProvider, IPlayerProvider, IRegionProvider, IScoreProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class ArcadeProvider(IPlayerProvider, IScoreProvider, IRegionProvider, IPlayerIdentifierProvider):
    """The provider that fetches data from the wahlap maimai arcade.

    This part of the maimai.py is not open-source, we distribute the compiled version of this part of the code as maimai_ffi.

    Feel free to ask us to solve if your platform or architecture is not supported.

    maimai.ffi: https://pypi.org/project/maimai-ffi
    """

    _http_proxy: Optional[str] = None

    def __init__(self, http_proxy: Optional[str] = None):
        self._http_proxy = http_proxy

    def _hash(self) -> str:
        return hashlib.md5(b"arcade").hexdigest()

    @staticmethod
    async def _deser_score(score: dict, songs: "MaimaiSongs") -> Optional[Score]:
        song_type = SongType._from_id(score["musicId"])
        level_index = LevelIndex(score["level"]) if song_type != SongType.UTAGE else None
        achievement = float(score["achievement"]) / 10000
        if song := await songs.by_id(score["musicId"] % 10000):
            if level_index and (diff := song.get_difficulty(song_type, level_index)):
                fs_type = FSType(score["syncStatus"]) if 0 < score["syncStatus"] < 5 else None
                fs_type = FSType.SYNC if score["syncStatus"] == 5 else fs_type
                return Score(
                    id=song.id,
                    level=diff.level,
                    level_index=diff.level_index,
                    achievements=achievement,
                    fc=FCType(4 - score["comboStatus"]) if score["comboStatus"] != 0 else None,
                    fs=fs_type,
                    dx_score=score["deluxscoreMax"],
                    dx_rating=ScoreCoefficient(achievement).ra(diff.level_value),
                    play_count=score["playCount"],
                    rate=RateType._from_achievement(achievement),
                    type=song_type,
                )

    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> ArcadePlayer:
        maimai_icons = await client.items(PlayerIcon)
        maimai_trophies = await client.items(PlayerTrophy)
        maimai_nameplates = await client.items(PlayerNamePlate)
        if identifier.credentials and isinstance(identifier.credentials, str):
            resp_dict = await arcade.get_user_preview(identifier.credentials.encode(), http_proxy=self._http_proxy)
            return ArcadePlayer(
                name=resp_dict["userName"],
                rating=resp_dict["playerRating"],
                is_login=resp_dict["isLogin"],
                name_plate=await maimai_nameplates.by_id(resp_dict["nameplateId"]),
                icon=await maimai_icons.by_id(resp_dict["iconId"]),
                trophy=await maimai_trophies.by_id(resp_dict["trophyId"]),
            )
        raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        maimai_songs = await client.songs()
        if identifier.credentials and isinstance(identifier.credentials, str):
            resp_list = await arcade.get_user_scores(identifier.credentials.encode(), http_proxy=self._http_proxy)
            return [s for score in resp_list if (s := await ArcadeProvider._deser_score(score, maimai_songs))]
        raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")

    async def get_regions(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[PlayerRegion]:
        if identifier.credentials and isinstance(identifier.credentials, str):
            resp_dict = await arcade.get_user_region(identifier.credentials.encode(), http_proxy=self._http_proxy)
            return [
                PlayerRegion(
                    region_id=region["regionId"],
                    region_name=region["regionName"],
                    play_count=region["playCount"],
                    created_at=datetime.strptime(region["created"], "%Y-%m-%d %H:%M:%S"),
                )
                for region in resp_dict["userRegionList"]
            ]
        raise InvalidPlayerIdentifierError("Player identifier credentials should be provided.")

    async def get_identifier(self, code: Union[str, dict[str, str]], client: "MaimaiClient") -> PlayerIdentifier:
        resp_bytes: bytes = await arcade.get_uid_encrypted(str(code), http_proxy=self._http_proxy)
        return PlayerIdentifier(credentials=resp_bytes.decode())
