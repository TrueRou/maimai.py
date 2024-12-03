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
    disabled: bool
    difficulties: SongDifficulties
