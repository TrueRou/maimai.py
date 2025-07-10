from dataclasses import dataclass
from datetime import datetime
from typing import Any, MutableMapping, Optional, Sequence, Union

from maimai_py.enums import *
from maimai_py.exceptions import *
from maimai_py.utils import UNSET, _UnsetSentinel


@dataclass
class Song:
    __slots__ = ("id", "title", "artist", "genre", "bpm", "map", "version", "rights", "aliases", "disabled", "difficulties")

    id: int
    title: str
    artist: str
    genre: Genre
    bpm: int
    map: Optional[str]
    version: int
    rights: Optional[str]
    aliases: Optional[list[str]]
    disabled: bool
    difficulties: "SongDifficulties"

    def get_difficulty(self, type: SongType, level_index: LevelIndex) -> Optional["SongDifficulty"]:
        """Get the exact difficulty of this song by type and level index.

        Args:
            type: The type of the song (DX, STANDARD, UTAGE).
            level_index: The level index of the difficulty.
        Returns:
            The difficulty object if found, otherwise None.
        """
        if type == SongType.DX:
            return next((diff for diff in self.difficulties.dx if diff.level_index == level_index), None)
        if type == SongType.STANDARD:
            return next((diff for diff in self.difficulties.standard if diff.level_index == level_index), None)
        if type == SongType.UTAGE:
            return next(iter(self.difficulties.utage), None)

    def get_difficulties(self, song_type: Union[SongType, _UnsetSentinel] = UNSET) -> Sequence["SongDifficulty"]:
        """Get all difficulties of the song, optionally filtered by type.

        Args:
            song_type: The type of the song (DX, STANDARD, UTAGE). If UNSET, returns all types.
        Returns:
            A sequence of difficulties matching the specified type.
        """
        if isinstance(song_type, _UnsetSentinel):
            return self.difficulties.standard + self.difficulties.dx + self.difficulties.utage
        if song_type == SongType.DX:
            return self.difficulties.dx
        if song_type == SongType.STANDARD:
            return self.difficulties.standard
        if song_type == SongType.UTAGE:
            return self.difficulties.utage

    def get_divingfish_id(self, type: SongType, level_index: LevelIndex) -> int:
        """Get the Diving Fish ID for a specific difficulty of this song.

        Args:
            type: The type of the song (DX, STANDARD, UTAGE).
            level_index: The level index of the difficulty.
        Returns:
            The Diving Fish ID for the specified difficulty.
        """
        difficulty = self.get_difficulty(type, level_index)
        if difficulty is None:
            raise ValueError(f"No difficulty found for type {type} and level index {level_index}")
        if difficulty.type == SongType.DX:
            return self.id + 10000
        if difficulty.type == SongType.UTAGE:
            return self.id + 100000
        return self.id

    def get_divingfish_ids(self, song_type: Union[SongType, _UnsetSentinel] = UNSET) -> set[int]:
        """Get a set of Diving Fish IDs for all difficulties of this song.

        Args:
            song_type: The type of the song (DX, STANDARD, UTAGE). If UNSET, returns IDs for all types.
        Returns:
            A set of Diving Fish IDs for the specified type or all types if UNSET.
        """
        ids = set()
        for difficulty in self.get_difficulties(song_type):
            ids.add(self.get_divingfish_id(difficulty.type, difficulty.level_index))
        return ids


@dataclass
class SongDifficulties:
    __slots__ = ("standard", "dx", "utage")

    standard: list["SongDifficulty"]
    dx: list["SongDifficulty"]
    utage: list["SongDifficultyUtage"]


@dataclass
class CurveObject:
    __slots__ = ("sample_size", "fit_level_value", "avg_achievements", "stdev_achievements", "avg_dx_score", "rate_sample_size", "fc_sample_size")

    sample_size: int
    fit_level_value: float
    avg_achievements: float
    stdev_achievements: float
    avg_dx_score: float
    rate_sample_size: dict[RateType, int]
    fc_sample_size: dict[FCType, int]


@dataclass
class SongDifficulty:
    __slots__ = (
        "id",
        "type",
        "level",
        "level_value",
        "level_index",
        "note_designer",
        "version",
        "tap_num",
        "hold_num",
        "slide_num",
        "touch_num",
        "break_num",
        "curve",
    )

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
    curve: Optional[CurveObject]


@dataclass
class SongDifficultyUtage(SongDifficulty):
    __slots__ = ("kanji", "description", "is_buddy")

    kanji: str
    description: str
    is_buddy: bool


@dataclass
class PlayerIdentifier:
    qq: Optional[int] = None
    username: Optional[str] = None
    friend_code: Optional[int] = None
    credentials: Union[str, MutableMapping[str, Any], None] = None

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


@dataclass
class PlayerItem:
    @staticmethod
    def _namespace() -> str:
        raise NotImplementedError


@dataclass
class PlayerTrophy(PlayerItem):
    __slots__ = ("id", "name", "color")

    id: int
    name: str
    color: str

    @staticmethod
    def _namespace():
        return "trophies"


@dataclass
class PlayerIcon(PlayerItem):
    __slots__ = ("id", "name", "description", "genre")

    id: int
    name: str
    description: Optional[str]
    genre: Optional[str]

    @staticmethod
    def _namespace():
        return "icons"


@dataclass
class PlayerNamePlate(PlayerItem):
    __slots__ = ("id", "name", "description", "genre")

    id: int
    name: str
    description: Optional[str]
    genre: Optional[str]

    @staticmethod
    def _namespace():
        return "nameplates"


@dataclass
class PlayerFrame(PlayerItem):
    __slots__ = ("id", "name", "description", "genre")

    id: int
    name: str
    description: Optional[str]
    genre: Optional[str]

    @staticmethod
    def _namespace():
        return "frames"


@dataclass
class PlayerPartner(PlayerItem):
    __slots__ = ("id", "name")

    id: int
    name: str

    @staticmethod
    def _namespace():
        return "partners"


@dataclass
class PlayerChara(PlayerItem):
    __slots__ = ("id", "name")

    id: int
    name: str

    @staticmethod
    def _namespace():
        return "charas"


@dataclass
class PlayerRegion:
    __slots__ = ("region_id", "region_name", "play_count", "created_at")

    region_id: int
    region_name: str
    play_count: int
    created_at: datetime


@dataclass
class Player:
    __slots__ = ("identifier", "name", "rating")

    name: str
    rating: int


@dataclass
class DivingFishPlayer(Player):
    __slots__ = ("nickname", "plate", "additional_rating")

    nickname: str
    plate: str
    additional_rating: int


@dataclass
class LXNSPlayer(Player):
    __slots__ = ("friend_code", "course_rank", "class_rank", "star", "frame", "icon", "trophy", "name_plate", "upload_time")

    friend_code: int
    course_rank: int
    class_rank: int
    star: int
    frame: Optional[PlayerFrame]
    icon: Optional[PlayerIcon]
    trophy: Optional[PlayerTrophy]
    name_plate: Optional[PlayerNamePlate]
    upload_time: str


@dataclass
class ArcadePlayer(Player):
    __slots__ = ("is_login", "icon", "trophy", "name_plate")

    is_login: bool
    icon: Optional[PlayerIcon]
    trophy: Optional[PlayerTrophy]
    name_plate: Optional[PlayerNamePlate]


@dataclass
class AreaCharacter:
    __slots__ = ("id", "name", "illustrator", "description1", "description2", "team", "props")

    name: str
    illustrator: str
    description1: str
    description2: str
    team: str
    props: dict[str, str]


@dataclass
class AreaSong:
    __slots__ = ("id", "title", "artist", "description", "illustrator", "movie")

    id: Optional[int]
    title: str
    artist: str
    description: str
    illustrator: Optional[str]
    movie: Optional[str]


@dataclass
class Area:
    __slots__ = ("id", "name", "comment", "description", "video_id", "characters", "songs")

    id: str
    name: str
    comment: str
    description: str
    video_id: str
    characters: list[AreaCharacter]
    songs: list[AreaSong]


@dataclass
class Score:
    __slots__ = ("id", "level", "level_index", "achievements", "fc", "fs", "dx_score", "dx_rating", "play_count", "rate", "type", "song")

    id: int
    level: str
    level_index: LevelIndex
    achievements: Optional[float]
    fc: Optional[FCType]
    fs: Optional[FSType]
    dx_score: Optional[int]
    dx_rating: Optional[float]
    play_count: Optional[int]
    rate: RateType
    type: SongType

    def _compare(self, other: Optional["Score"]) -> "Score":
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

    def _join(self, other: Optional["Score"]) -> "Score":
        if other is not None:
            if self.level_index != other.level_index or self.type != other.type:
                raise ValueError("Cannot join scores with different level indexes or types")
            self.achievements = max(self.achievements or 0, other.achievements or 0)
            if self.fc != other.fc:
                self_fc = self.fc.value if self.fc is not None else 100
                other_fc = other.fc.value if other.fc is not None else 100
                selected_value = min(self_fc, other_fc)
                self.fc = FCType(selected_value) if selected_value != 100 else None
            if self.fs != other.fs:
                self_fs = self.fs.value if self.fs is not None else -1
                other_fs = other.fs.value if other.fs is not None else -1
                selected_value = max(self_fs, other_fs)
                self.fs = FSType(selected_value) if selected_value != -1 else None
            if self.rate != other.rate:
                selected_value = min(self.rate.value, other.rate.value)
                self.rate = RateType(selected_value)
        return self


@dataclass
class ScoreExtend(Score):
    __slots__ = ["title", "level_value", "level_dx_score"]

    title: str
    level_value: float
    level_dx_score: int


@dataclass
class PlateObject:
    __slots__ = ("song", "levels", "scores")

    song: Song
    levels: set[LevelIndex]
    scores: list[ScoreExtend]


@dataclass
class PlayerSong:
    __slots__ = ["song", "scores"]

    song: Song
    scores: list[ScoreExtend]


@dataclass
class PlayerBests:
    __slots__ = ["rating", "rating_b35", "rating_b15", "scores_b35", "scores_b15"]

    rating: int
    rating_b35: int
    rating_b15: int
    scores_b35: list[ScoreExtend]
    scores_b15: list[ScoreExtend]

    @property
    def scores(self) -> list[ScoreExtend]:
        """Get all scores, including both B35 and B15."""
        return self.scores_b35 + self.scores_b15
