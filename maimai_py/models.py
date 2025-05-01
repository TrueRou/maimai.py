import asyncio
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Generic, Iterator, Sequence, TypeVar
from httpx import AsyncClient, Cookies
from dogpile.cache.region import CacheRegion
from dogpile.cache.api import NoValue

from maimai_py.enums import *
from maimai_py.caches import default_caches
from maimai_py.exceptions import InvalidPlateError, InvalidPlayerIdentifierError, AimeServerError, ArcadeError, TitleServerError
from maimai_py.utils.sentinel import UNSET, _UnsetSentinel

default_cache: CacheRegion | None = None


@dataclass(slots=True)
class Song:
    id: int
    title: str
    artist: str
    genre: Genre
    bpm: int
    map: str | None
    version: int
    rights: str | None
    aliases: list[str] | None
    disabled: bool
    difficulties: "SongDifficulties"

    def _get_level_indexes(self, song_type: SongType, exclude_remaster: bool = False) -> list[LevelIndex]:
        """@private"""
        results = [diff.level_index for diff in self.difficulties._get_children(song_type)]
        if exclude_remaster and LevelIndex.ReMASTER in results:
            results.remove(LevelIndex.ReMASTER)
        return results

    def get_difficulty(self, type: SongType, level_index: LevelIndex | None) -> "SongDifficulty | None":
        if type == SongType.DX:
            return next((diff for diff in self.difficulties.dx if diff.level_index == level_index), None)
        if type == SongType.STANDARD:
            return next((diff for diff in self.difficulties.standard if diff.level_index == level_index), None)
        if type == SongType.UTAGE:
            return next(iter(self.difficulties.utage), None)


@dataclass(slots=True)
class SongDifficulties:
    standard: list["SongDifficulty"]
    dx: list["SongDifficulty"]
    utage: list["SongDifficultyUtage"]

    def _get_children(self, song_type: SongType | _UnsetSentinel = UNSET) -> Sequence["SongDifficulty"]:
        if song_type == UNSET:
            return self.standard + self.dx + self.utage
        return self.dx if song_type == SongType.DX else self.standard if song_type == SongType.STANDARD else self.utage


@dataclass(slots=True)
class CurveObject:
    sample_size: int
    fit_level_value: float
    avg_achievements: float
    stdev_achievements: float
    avg_dx_score: float
    rate_sample_size: dict[RateType, int]
    fc_sample_size: dict[FCType, int]


@dataclass(slots=True)
class SongDifficulty:
    type: SongType
    level: str
    level_value: float
    level_index: LevelIndex
    note_designer: str
    version: int
    tap_num: int
    hold_num: int
    slide_num: int
    touch_num: int
    break_num: int
    curve: CurveObject | None


@dataclass(slots=True)
class SongDifficultyUtage(SongDifficulty):
    kanji: str
    description: str
    is_buddy: bool


@dataclass(slots=True)
class SongAlias:
    """@private"""

    song_id: int
    aliases: list[str]


@dataclass(slots=True)
class PlayerIdentifier:
    qq: int | None = None
    username: str | None = None
    friend_code: int | None = None
    credentials: str | Cookies | None = None

    def __post_init__(self):
        if self.qq is None and self.username is None and self.friend_code is None and self.credentials is None:
            raise InvalidPlayerIdentifierError("At least one of the following must be provided: qq, username, friend_code, credentials")

    def _as_diving_fish(self) -> dict[str, Any]:
        if self.qq:
            return {"qq": str(self.qq)}
        elif self.username:
            return {"username": self.username}
        elif self.friend_code:
            raise InvalidPlayerIdentifierError("Friend code is not applicable for Diving Fish")
        else:
            raise InvalidPlayerIdentifierError("No valid identifier provided")

    def _as_lxns(self) -> str:
        if self.friend_code:
            return str(self.friend_code)
        elif self.qq:
            return f"qq/{str(self.qq)}"
        elif self.username:
            raise InvalidPlayerIdentifierError("Username is not applicable for LXNS")
        else:
            raise InvalidPlayerIdentifierError("No valid identifier provided")


@dataclass(slots=True)
class ArcadeResponse:
    """@private"""

    errno: int | None = None
    errmsg: str | None = None
    data: dict[str, Any] | bytes | list[Any] | None = None

    @staticmethod
    def _raise_for_error(resp: "ArcadeResponse") -> None:
        if resp.errno and resp.errno != 0:
            if resp.errno > 1000:
                raise ArcadeError(resp.errmsg)
            elif resp.errno > 100:
                raise TitleServerError(resp.errmsg)
            elif resp.errno > 0:
                raise AimeServerError(resp.errmsg)


@dataclass(slots=True)
class CachedModel:
    @staticmethod
    def _cache_key() -> str:
        raise NotImplementedError


@dataclass(slots=True)
class PlayerTrophy(CachedModel):
    id: int
    name: str
    color: str

    @staticmethod
    def _cache_key():
        return "trophies"


@dataclass(slots=True)
class PlayerIcon(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    @staticmethod
    def _cache_key():
        return "icons"


@dataclass(slots=True)
class PlayerNamePlate(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    @staticmethod
    def _cache_key():
        return "nameplates"


@dataclass(slots=True)
class PlayerFrame(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    @staticmethod
    def _cache_key():
        return "frames"


@dataclass(slots=True)
class PlayerPartner(CachedModel):
    id: int
    name: str

    @staticmethod
    def _cache_key():
        return "partners"


@dataclass(slots=True)
class PlayerChara(CachedModel):
    id: int
    name: str

    @staticmethod
    def _cache_key():
        return "charas"


@dataclass(slots=True)
class PlayerRegion:
    region_id: int
    region_name: str
    play_count: int
    created_at: datetime


@dataclass(slots=True)
class Player:
    name: str
    rating: int


@dataclass(slots=True)
class DivingFishPlayer(Player):
    nickname: str
    plate: str
    additional_rating: int


@dataclass(slots=True)
class LXNSPlayer(Player):
    friend_code: int
    trophy: PlayerTrophy
    course_rank: int
    class_rank: int
    star: int
    icon: PlayerIcon | None
    name_plate: PlayerNamePlate | None
    frame: PlayerFrame | None
    upload_time: str


@dataclass(slots=True)
class ArcadePlayer(Player):
    is_login: bool
    name_plate: PlayerNamePlate | None
    icon: PlayerIcon | None
    trophy: PlayerFrame | None


@dataclass(slots=True)
class AreaCharacter:
    name: str
    illustrator: str
    description1: str
    description2: str
    team: str
    props: dict[str, str]


@dataclass(slots=True)
class AreaSong:
    id: int
    title: str
    artist: str
    description: str
    illustrator: str | None
    movie: str | None


@dataclass(slots=True)
class Area:
    id: str
    name: str
    comment: str
    description: str
    video_id: str
    characters: list[AreaCharacter]
    songs: list[AreaSong]


@dataclass(slots=True)
class Score:
    id: int
    song_name: str
    level: str
    level_index: LevelIndex
    achievements: float | None
    fc: FCType | None
    fs: FSType | None
    dx_score: int | None
    dx_rating: float | None
    rate: RateType
    type: SongType

    def _compare(self, other: "Score | None") -> "Score":
        if other is None:
            return self
        if self.dx_score != other.dx_score:  # larger value is better
            return self if (self.dx_score or 0) > (other.dx_score or 0) else other
        if self.achievements != other.achievements:  # larger value is better
            return self if (self.achievements or 0) > (other.achievements or 0) else other
        if self.rate != other.rate:  # smaller value is better
            self_rate = self.rate.value if self.rate is not None else 100
            other_rate = other.rate.value if other.rate is not None else 100
            return self if self_rate < other_rate else other
        if self.fc != other.fc:  # smaller value is better
            self_fc = self.fc.value if self.fc is not None else 100
            other_fc = other.fc.value if other.fc is not None else 100
            return self if self_fc < other_fc else other
        if self.fs != other.fs:  # bigger value is better
            self_fs = self.fs.value if self.fs is not None else -1
            other_fs = other.fs.value if other.fs is not None else -1
            return self if self_fs > other_fs else other
        return self  # we consider they are equal

    # @property
    # def song(self) -> Song | None:
    #     songs: MaimaiSongs = default_caches._caches["msongs"]
    #     assert songs is not None and isinstance(songs, MaimaiSongs)
    #     return songs.by_id(self.id)

    # @property
    # def difficulty(self) -> SongDifficulty | None:
    #     if self.song:
    #         return self.song.get_difficulty(self.type, self.level_index)


@dataclass(slots=True)
class PlateObject:
    song: Song
    levels: list[LevelIndex]
    scores: list[Score]
