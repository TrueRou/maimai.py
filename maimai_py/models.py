from dataclasses import dataclass

from maimai_py.enums import FCType, FSType, LevelIndex, RateType, SongType
from maimai_py.exceptions import MaimaiPyError


@dataclass
class SongDifficulty:
    type: SongType
    difficulty: LevelIndex
    level: str
    level_value: float
    note_designer: str
    version: int
    tap_num: int
    hold_num: int
    slide_num: int
    touch_num: int
    break_num: int


@dataclass
class SongDifficultyUtage:
    kanji: str
    description: str
    is_buddy: bool
    tap_num: int
    hold_num: int
    slide_num: int
    touch_num: int
    break_num: int


@dataclass
class SongDifficulties:
    standard: list[SongDifficulty]
    dx: list[SongDifficulty]
    utage: list[SongDifficultyUtage]


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    bpm: int
    map: str | None
    version: int
    rights: str | None
    aliases: list[str] | None
    disabled: bool
    difficulties: SongDifficulties

    def levels(self, exclude_remaster: bool = False) -> list[LevelIndex]:
        results = [diff.difficulty for diff in (self.difficulties.standard + self.difficulties.dx)]
        if exclude_remaster and LevelIndex.ReMASTER in results:
            results.remove(LevelIndex.ReMASTER)
        return results


@dataclass
class PlayerIdentifier:
    qq: int | None = None
    username: str | None = None
    friend_code: int | None = None

    def __post_init__(self):
        if self.qq is None and self.username is None and self.friend_code is None:
            raise MaimaiPyError("At least one of qq, username, or friend_code must be provided")

    def as_diving_fish(self):
        """@private"""
        if self.qq:
            return {"qq": str(self.qq)}
        elif self.username:
            return {"username": self.username}
        elif self.friend_code:
            raise MaimaiPyError("Friend code is not applicable for Diving Fish")

    def as_lxns(self):
        """@private"""
        if self.friend_code:
            return str(self.friend_code)
        elif self.qq:
            return f"qq/{str(self.qq)}"
        elif self.username:
            raise MaimaiPyError("Username is not applicable for LXNS")


@dataclass
class PlayerTrophy:
    id: int
    name: str
    color: str


@dataclass
class PlayerIcon:
    id: int
    name: str
    genre: str


@dataclass
class PlayerNamePlate:
    id: int
    name: str


@dataclass
class PlayerFrame:
    id: int
    name: str


@dataclass
class Player:
    name: str
    rating: int


@dataclass
class DivingFishPlayer(Player):
    nickname: str
    plate: str
    additional_rating: int


@dataclass
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


@dataclass
class SongAlias:
    song_id: int
    aliases: list[str]


@dataclass
class Score:
    id: int
    song_name: str
    level: str
    level_index: LevelIndex
    achievements: float | None
    fc: FCType
    fs: FSType
    dx_score: int | None
    dx_rating: float | None
    rate: RateType
    type: SongType

    def compare(self, other: "Score") -> "Score":
        """@private"""
        if other is None:
            return self
        if self.dx_score and other.dx_score:  # larger value is better
            return self if self.dx_score > other.dx_score else other
        if self.achievements and other.achievements and self.achievements != other.achievements:  # larger value is better
            return self if self.achievements > other.achievements else other
        if self.rate and other.rate and self.rate != other.rate:  # smaller value is better
            return self if self.rate.value < other.rate.value else other
        if (self.fc.value if self.fc else 100) != (other.fc.value if self.fc else 100):  # smaller value is better
            return self if (self.fc.value if self.fc else 100) < (other.fc.value if self.fc else 100) else other
        if (self.fs.value if self.fs else 100) != (other.fs.value if self.fs else 100):  # smaller value is better
            return self if (self.fs.value if self.fs else 100) < (other.fs.value if self.fs else 100) else other
        return self  # we consider they are equal


@dataclass
class PlateObject:
    song: Song
    levels: list[LevelIndex]
    score: list[Score] | None
