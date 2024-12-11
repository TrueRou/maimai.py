from dataclasses import dataclass
from typing import TYPE_CHECKING

from httpx import AsyncClient, Cookies

from maimai_py.enums import FCType, FSType, LevelIndex, RateType, SongType
from maimai_py.exceptions import InvalidPlayerIdentifierError, InvalidPlayerIdentifierError

if TYPE_CHECKING:
    from maimai_py.providers.lxns import LXNSProvider


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

    def get_levels(self, exclude_remaster: bool = False) -> list[LevelIndex]:
        """Get the level indexes of the song.

        Args:
            exclude_remaster: whether to exclude the ReMASTER level index.
        Returns:
            the level indexes of the song.
        """
        results = [diff.difficulty for diff in (self.difficulties.standard + self.difficulties.dx)]
        if exclude_remaster and LevelIndex.ReMASTER in results:
            results.remove(LevelIndex.ReMASTER)
        return results

    def get_diff(self, type: SongType, level_index: LevelIndex) -> SongDifficulty | None:
        """Get the difficulty of the song by its type and level index.

        Args:
            type: the type of the difficulty, e.g. `SongType.DX`.
            level_index: the index of the level, e.g. `LevelIndex.MASTER`.
        Returns:
            the difficulty if it exists, otherwise return None.
        """
        if type == SongType.DX:
            return next((diff for diff in self.difficulties.dx if diff.difficulty == level_index), None)
        if type == SongType.STANDARD:
            return next((diff for diff in self.difficulties.standard if diff.difficulty == level_index), None)
        return None


@dataclass
class PlayerIdentifier:
    qq: int | None = None
    username: str | None = None
    friend_code: int | None = None
    wechat_cookies: Cookies | None = None
    credentials: str | None = None

    def __post_init__(self):
        if self.qq is None and self.username is None and self.friend_code is None and self.wechat_cookies is None:
            raise InvalidPlayerIdentifierError("At least one of the following must be provided: qq, username, friend_code, wechat_cookies")

    def as_diving_fish(self):
        """@private"""
        if self.qq:
            return {"qq": str(self.qq)}
        elif self.username:
            return {"username": self.username}
        elif self.friend_code:
            raise InvalidPlayerIdentifierError("Friend code is not applicable for Diving Fish")

    def as_lxns(self):
        """@private"""
        if self.friend_code:
            return str(self.friend_code)
        elif self.qq:
            return f"qq/{str(self.qq)}"
        elif self.username:
            raise InvalidPlayerIdentifierError("Username is not applicable for LXNS")

    async def ensure_friend_code(self, client: AsyncClient, provider: "LXNSProvider"):
        """@private"""
        if self.friend_code is None:
            resp = await client.get(provider.base_url + f"api/v0/maimai/player/qq/{self.qq}", headers=provider.headers)
            if not resp.json()["success"]:
                raise InvalidPlayerIdentifierError(resp.json()["message"])
            self.friend_code = resp.json()["data"]["friend_code"]


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
