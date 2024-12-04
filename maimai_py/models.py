from dataclasses import dataclass

from maimai_py.enums import LevelIndex, SongType


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
    left_num: int
    right_num: int


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
