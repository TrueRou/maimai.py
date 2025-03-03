from abc import abstractmethod
import asyncio
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Generic, TypeVar
from httpx import Cookies

from maimai_py.enums import *
from maimai_py.caches import default_caches
from maimai_py.exceptions import InvalidPlateError, InvalidPlayerIdentifierError, AimeServerError, ArcadeError, TitleServerError
from maimai_py.utils.sentinel import UNSET


@dataclass
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

    def get_difficulty(self, type: SongType, level_index: LevelIndex) -> "SongDifficulty":
        if type == SongType.DX:
            return next((diff for diff in self.difficulties.dx if diff.level_index == level_index), None)
        if type == SongType.STANDARD:
            return next((diff for diff in self.difficulties.standard if diff.level_index == level_index), None)
        if type == SongType.UTAGE:
            return next(iter(self.difficulties.utage), None)


@dataclass
class SongDifficulties:
    standard: list["SongDifficulty"]
    dx: list["SongDifficulty"]
    utage: list["SongDifficultyUtage"]

    def _get_children(self, song_type: SongType = UNSET) -> list["SongDifficulty"]:
        if song_type == UNSET:
            return self.standard + self.dx + self.utage
        return self.dx if song_type == SongType.DX else self.standard if song_type == SongType.STANDARD else self.utage


@dataclass
class CurveObject:
    sample_size: int
    fit_level_value: float
    avg_achievements: float
    stdev_achievements: float
    avg_dx_score: float
    rate_sample_size: dict[RateType, int]
    fc_sample_size: dict[FCType, int]


@dataclass
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


@dataclass
class SongDifficultyUtage(SongDifficulty):
    kanji: str
    description: str
    is_buddy: bool


@dataclass
class SongAlias:
    """@private"""

    song_id: int
    aliases: list[str]


@dataclass
class PlayerIdentifier:
    qq: int | None = None
    username: str | None = None
    friend_code: int | None = None
    credentials: str | Cookies | None = None

    def __post_init__(self):
        if self.qq is None and self.username is None and self.friend_code is None and self.credentials is None:
            raise InvalidPlayerIdentifierError("At least one of the following must be provided: qq, username, friend_code, credentials")

    def _as_diving_fish(self):
        if self.qq:
            return {"qq": str(self.qq)}
        elif self.username:
            return {"username": self.username}
        elif self.friend_code:
            raise InvalidPlayerIdentifierError("Friend code is not applicable for Diving Fish")

    def _as_lxns(self):
        if self.friend_code:
            return str(self.friend_code)
        elif self.qq:
            return f"qq/{str(self.qq)}"
        elif self.username:
            raise InvalidPlayerIdentifierError("Username is not applicable for LXNS")


@dataclass
class ArcadeResponse:
    """@private"""

    errno: int | None = None
    errmsg: str | None = None
    data: dict[str, Any] | bytes | list[Any] | None = None

    def _throw_error(resp: "ArcadeResponse"):
        if resp.errno and resp.errno != 0:
            if resp.errno > 1000:
                raise ArcadeError(resp.errmsg)
            elif resp.errno > 100:
                raise TitleServerError(resp.errmsg)
            elif resp.errno > 0:
                raise AimeServerError(resp.errmsg)


@dataclass
class CachedModel:
    @abstractmethod
    def _cache_key() -> str:
        pass


@dataclass
class PlayerTrophy(CachedModel):
    id: int
    name: str
    color: str

    def _cache_key():
        return "trophies"


@dataclass
class PlayerIcon(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    def _cache_key():
        return "icons"


@dataclass
class PlayerNamePlate(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    def _cache_key():
        return "nameplates"


@dataclass
class PlayerFrame(CachedModel):
    id: int
    name: str
    description: str | None = None
    genre: str | None = None

    def _cache_key():
        return "frames"


@dataclass
class PlayerPartner(CachedModel):
    id: int
    name: str

    def _cache_key():
        return "partners"


@dataclass
class PlayerChara(CachedModel):
    id: int
    name: str

    def _cache_key():
        return "charas"


@dataclass
class PlayerRegion:
    region_id: int
    region_name: str
    play_count: int
    created_at: datetime


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
class ArcadePlayer(Player):
    is_login: bool
    name_plate: PlayerNamePlate | None
    icon: PlayerIcon | None
    trophy: PlayerFrame | None


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

    def _compare(self, other: "Score") -> "Score":
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

    @property
    def song(self) -> Song:
        songs: MaimaiSongs = default_caches._caches["msongs"]
        assert songs is not None and isinstance(songs, MaimaiSongs)
        return songs.by_id(self.id)

    @property
    def difficulty(self) -> SongDifficulty:
        return self.song.get_difficulty(self.type, self.level_index)


@dataclass
class PlateObject:
    song: Song
    levels: list[LevelIndex]
    scores: list[Score] | None


CachedType = TypeVar("T", bound=CachedModel)


class MaimaiItems(Generic[CachedType]):
    _cached_items: dict[int, CachedType]

    def __init__(self, items: dict[int, CachedType]) -> None:
        """@private"""
        self._cached_items = items

    @property
    def values(self) -> list[CachedType]:
        """All items as list."""
        return self._cached_items.values()

    def by_id(self, id: int) -> CachedType | None:
        """Get an item by its ID.

        Args:
            id: the ID of the item.
        Returns:
            the item if it exists, otherwise return None.
        """
        return self._cached_items.get(id, None)

    def filter(self, **kwargs) -> list[CachedType]:
        """Filter items by their attributes.

        Ensure that the attribute is of the item, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the items by.
        Returns:
            the list of items that match all the conditions, return an empty list if no item is found.
        """
        return [item for item in self.values if all(getattr(item, key) == value for key, value in kwargs.items() if value is not None)]


class MaimaiSongs:
    _cached_songs: list[Song]
    _cached_aliases: list[SongAlias]
    _cached_curves: dict[str, list[CurveObject | None]]

    _song_id_dict: dict[int, Song]  # song_id: song
    _alias_entry_dict: dict[str, Song]  # alias_entry: song
    _keywords_dict: dict[str, Song]  # keywords: song

    def __init__(self, songs: list[Song], aliases: list[SongAlias] | None, curves: dict[str, list[CurveObject | None]]) -> None:
        """@private"""
        self._cached_songs = songs
        self._cached_aliases = aliases
        self._cached_curves = curves
        self._song_id_dict = {}
        self._alias_entry_dict = {}
        self._keywords_dict = {}
        self._flush()

    def _flush(self) -> None:
        self._song_id_dict = {song.id: song for song in self._cached_songs}
        self._keywords_dict = {}
        for alias in self._cached_aliases or []:
            if song := self._song_id_dict.get(alias.song_id):
                song.aliases = alias.aliases
                for alias_entry in alias.aliases:
                    self._alias_entry_dict[alias_entry] = song
        for idx, curve_list in (self._cached_curves or {}).items():
            song_type: SongType = SongType._from_id(int(idx))
            song_id = int(idx) % 10000
            if song := self._song_id_dict.get(song_id):
                diffs = song.difficulties._get_children(song_type)
                if len(diffs) < len(curve_list):
                    # ignore the extra curves, diving fish may return more curves than the song has, which is a bug
                    curve_list = curve_list[: len(diffs)]
                [diffs[i].__setattr__("curve", curve) for i, curve in enumerate(curve_list)]
        for song in self._cached_songs:
            keywords = song.title.lower() + song.artist.lower() + "".join(alias.lower() for alias in (song.aliases or []))
            self._keywords_dict[keywords] = song

    @staticmethod
    async def _get_or_fetch(flush=False) -> "MaimaiSongs":
        if "msongs" not in default_caches._caches or flush:
            tasks = [
                default_caches.get_or_fetch("songs", flush=flush),
                default_caches.get_or_fetch("aliases", flush=flush),
                default_caches.get_or_fetch("curves", flush=flush),
            ]
            songs, aliases, curves = await asyncio.gather(*tasks)
            default_caches._caches["msongs"] = MaimaiSongs(songs, aliases, curves)
        return default_caches._caches["msongs"]

    @property
    def songs(self) -> list[Song]:
        """All songs as list."""
        return self._song_id_dict.values()

    def by_id(self, id: int) -> Song | None:
        """Get a song by its ID.

        Args:
            id: the ID of the song, always smaller than `10000`, should (`% 10000`) if necessary.
        Returns:
            the song if it exists, otherwise return None.
        """
        return self._song_id_dict.get(id, None)

    def by_title(self, title: str) -> Song | None:
        """Get a song by its title.

        Args:
            title: the title of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        if title == "Link(CoF)":
            return self.by_id(383)
        return next((song for song in self.songs if song.title == title), None)

    def by_alias(self, alias: str) -> Song | None:
        """Get song by one possible alias.

        Args:
            alias: one possible alias of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        return self._alias_entry_dict.get(alias, None)

    def by_artist(self, artist: str) -> list[Song]:
        """Get songs by their artist, case-sensitive.

        Args:
            artist: the artist of the songs.
        Returns:
            the list of songs that match the artist, return an empty list if no song is found.
        """
        return [song for song in self.songs if song.artist == artist]

    def by_genre(self, genre: Genre) -> list[Song]:
        """Get songs by their genre, case-sensitive.

        Args:
            genre: the genre of the songs.
        Returns:
            the list of songs that match the genre, return an empty list if no song is found.
        """

        return [song for song in self.songs if song.genre == genre]

    def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
        """Get songs by their BPM.

        Args:
            minimum: the minimum (inclusive) BPM of the songs.
            maximum: the maximum (inclusive) BPM of the songs.
        Returns:
            the list of songs that match the BPM range, return an empty list if no song is found.
        """
        return [song for song in self.songs if minimum <= song.bpm <= maximum]

    def by_versions(self, versions: Version) -> list[Song]:
        """Get songs by their versions, versions are fuzzy matched version of major maimai version.

        Args:
            versions: the versions of the songs.
        Returns:
            the list of songs that match the versions, return an empty list if no song is found.
        """

        versions_func: Callable[[Song], bool] = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value
        return list(filter(versions_func, self.songs))

    def by_keywords(self, keywords: str) -> list[Song]:
        """Get songs by their keywords, keywords are matched with song title, artist and aliases.

        Args:
            keywords: the keywords to match the songs.
        Returns:
            the list of songs that match the keywords, return an empty list if no song is found.
        """
        return [v for k, v in self._keywords_dict.items() if keywords.lower() in k]

    def filter(self, **kwargs) -> list[Song]:
        """Filter songs by their attributes.

        Ensure that the attribute is of the song, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the songs by.
        Returns:
            the list of songs that match all the conditions, return an empty list if no song is found.
        """
        if "id" in kwargs and kwargs["id"] is not None:
            # if id is provided, ignore other attributes, as id is unique
            return [item] if (item := self.by_id(kwargs["id"])) else []
        return [song for song in self.songs if all(getattr(song, key) == value for key, value in kwargs.items() if value is not None)]


class MaimaiPlates:
    scores: list[Score]
    """The scores that match the plate version and kind."""
    songs: list[Song]
    """The songs that match the plate version and kind."""
    version: str
    """The version of the plate, e.g. "真", "舞"."""
    kind: str
    """The kind of the plate, e.g. "将", "神"."""

    _versions: list[Version] = []

    def __init__(self, scores: list[Score], version_str: str, kind: str, songs: MaimaiSongs) -> None:
        """@private"""
        self.scores = []
        self.songs = []
        self.version = plate_aliases.get(version_str, version_str)
        self.kind = plate_aliases.get(kind, kind)
        if self.version == "真":
            versions = [plate_to_version["初"], plate_to_version["真"]]
        if self.version in ["霸", "舞"]:
            versions = [ver for ver in plate_to_version.values() if ver.value < 20000]
        if plate_to_version.get(self.version):
            versions = [plate_to_version[self.version]]
        if not versions or self.kind not in ["将", "者", "极", "舞舞", "神"]:
            raise InvalidPlateError(f"Invalid plate: {self.version}{self.kind}")
        versions.append([ver for ver in plate_to_version.values() if ver.value > versions[-1].value][0])
        self._versions = versions

        scores_unique = {}
        for score in scores:
            if song := songs.by_id(score.id):
                score_key = f"{score.id} {score.type} {score.level_index}"
                score_version = song.get_difficulty(score.type, score.level_index).version
                if score.level_index == LevelIndex.ReMASTER and self.no_remaster:
                    continue  # skip ReMASTER levels if not required, e.g. in 霸 and 舞 plates
                if any(score_version >= o.value and score_version < versions[i + 1].value for i, o in enumerate(versions[:-1])):
                    scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))

        for song in songs.songs:
            diffs = song.difficulties._get_children()
            if any(diff.version >= o.value and diff.version < versions[i + 1].value for i, o in enumerate(versions[:-1]) for diff in diffs):
                self.songs.append(song)

        self.scores = list(scores_unique.values())

    @cached_property
    def no_remaster(self) -> bool:
        """Whether it is required to play ReMASTER levels in the plate.

        Only 舞 and 霸 plates require ReMASTER levels, others don't.
        """

        return self.version not in ["舞", "霸"]

    @cached_property
    def major_type(self) -> SongType:
        """The major song type of the plate, usually for identifying the levels.

        Only 舞 and 霸 plates require ReMASTER levels, others don't.
        """
        return SongType.DX if any(ver.value > 20000 for ver in self._versions) else SongType.STANDARD

    @cached_property
    def remained(self) -> list[PlateObject]:
        """Get the remained songs and scores of the player on this plate.

        If player has ramained levels on one song, the song and ramained `level_index` will be included in the result, otherwise it won't.

        The distinct scores which NOT met the plate requirement will be included in the result, the finished scores won't.
        """
        scores_dict: dict[int, list[Score]] = {}
        [scores_dict.setdefault(score.id, []).append(score) for score in self.scores]
        results = {
            song.id: PlateObject(song=song, levels=song._get_level_indexes(self.major_type, self.no_remaster), scores=scores_dict.get(song.id, []))
            for song in self.songs
        }

        def extract(score: Score) -> None:
            results[score.id].scores.remove(score)
            if score.level_index in results[score.id].levels:
                results[score.id].levels.remove(score.level_index)

        if self.kind == "者":
            [extract(score) for score in self.scores if score.rate.value <= RateType.A.value]
        elif self.kind == "将":
            [extract(score) for score in self.scores if score.rate.value <= RateType.SSS.value]
        elif self.kind == "极":
            [extract(score) for score in self.scores if score.fc and score.fc.value <= FCType.FC.value]
        elif self.kind == "舞舞":
            [extract(score) for score in self.scores if score.fs and score.fs.value <= FSType.FSD.value]
        elif self.kind == "神":
            [extract(score) for score in self.scores if score.fc and score.fc.value <= FCType.AP.value]

        return [plate for plate in results.values() if plate.levels != []]

    @cached_property
    def cleared(self) -> list[PlateObject]:
        """Get the cleared songs and scores of the player on this plate.

        If player has levels (one or more) that met the requirement on the song, the song and cleared `level_index` will be included in the result, otherwise it won't.

        The distinct scores which met the plate requirement will be included in the result, the unfinished scores won't.
        """
        results = {song.id: PlateObject(song=song, levels=[], scores=[]) for song in self.songs}

        def insert(score: Score) -> None:
            results[score.id].scores.append(score)
            results[score.id].levels.append(score.level_index)

        if self.kind == "者":
            [insert(score) for score in self.scores if score.rate.value <= RateType.A.value]
        elif self.kind == "将":
            [insert(score) for score in self.scores if score.rate.value <= RateType.SSS.value]
        elif self.kind == "极":
            [insert(score) for score in self.scores if score.fc and score.fc.value <= FCType.FC.value]
        elif self.kind == "舞舞":
            [insert(score) for score in self.scores if score.fs and score.fs.value <= FSType.FSD.value]
        elif self.kind == "神":
            [insert(score) for score in self.scores if score.fc and score.fc.value <= FCType.AP.value]

        return [plate for plate in results.values() if plate.levels != []]

    @cached_property
    def played(self) -> list[PlateObject]:
        """Get the played songs and scores of the player on this plate.

        If player has ever played levels on the song, whether they met or not, the song and played `level_index` will be included in the result.

        All distinct scores will be included in the result.
        """
        results = {song.id: PlateObject(song=song, levels=[], scores=[]) for song in self.songs}
        for score in self.scores:
            results[score.id].scores.append(score)
            results[score.id].levels.append(score.level_index)
        return [plate for plate in results.values() if plate.levels != []]

    @cached_property
    def all(self) -> list[PlateObject]:
        """Get all songs on this plate, usually used for statistics of the plate.

        All songs will be included in the result, with all levels, whether they met or not.

        No scores will be included in the result, use played, cleared, remained to get the scores.
        """
        results = {
            song.id: PlateObject(song=song, levels=song._get_level_indexes(self.major_type, self.no_remaster), scores=[]) for song in self.songs
        }
        return results.values()

    @cached_property
    def played_num(self) -> int:
        """Get the number of played levels on this plate."""
        return len([level for plate in self.played for level in plate.levels])

    @cached_property
    def cleared_num(self) -> int:
        """Get the number of cleared levels on this plate."""
        return len([level for plate in self.cleared for level in plate.levels])

    @cached_property
    def remained_num(self) -> int:
        """Get the number of remained levels on this plate."""
        return len([level for plate in self.remained for level in plate.levels])

    @cached_property
    def all_num(self) -> int:
        """Get the number of all levels on this plate.

        This is the total number of levels on the plate, should equal to `cleared_num + remained_num`.
        """
        return len([level for plate in self.all for level in plate.levels])


class MaimaiScores:
    scores: list[Score]
    """All scores of the player when `ScoreKind.ALL`, otherwise only the b50 scores."""
    scores_b35: list[Score]
    """The b35 scores of the player."""
    scores_b15: list[Score]
    """The b15 scores of the player."""
    rating: int
    """The total rating of the player."""
    rating_b35: int
    """The b35 rating of the player."""
    rating_b15: int
    """The b15 rating of the player."""

    @staticmethod
    def _get_distinct_scores(scores: list[Score]) -> list[Score]:
        scores_unique = {}
        for score in scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))
        return list(scores_unique.values())

    def __init__(self, b35: list[Score] = None, b15: list[Score] = None, all: list[Score] = None, songs: MaimaiSongs = None):
        self.scores = all or (b35 + b15 if b35 and b15 else None) or []
        # if b35 and b15 are not provided, try to calculate them from all scores
        if (not b35 or not b15) and all:
            distinct_scores = MaimaiScores._get_distinct_scores(all)  # scores have to be distinct to calculate the bests
            scores_new: list[Score] = []
            scores_old: list[Score] = []
            for score in distinct_scores:
                if song := songs.by_id(score.id):
                    (scores_new if song.version >= current_version.value else scores_old).append(score)
            scores_old.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
            scores_new.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
            b35 = scores_old[:35]
            b15 = scores_new[:15]
        self.scores_b35 = b35
        self.scores_b15 = b15
        self.rating_b35 = sum(score.dx_rating for score in b35)
        self.rating_b15 = sum(score.dx_rating for score in b15)
        self.rating = self.rating_b35 + self.rating_b15

    @property
    def as_distinct(self) -> "MaimaiScores":
        """Get the distinct scores.

        Normally, player has more than one score for the same song and level, this method will return a new `MaimaiScores` object with the highest scores for each song and level.

        This method won't modify the original scores object, it will return a new one.

        If ScoreKind is BEST, this won't make any difference, because the scores are already the best ones.
        """
        distinct_scores = MaimaiScores._get_distinct_scores(self.scores)
        songs: MaimaiSongs = default_caches._caches["msongs"]
        assert songs is not None and isinstance(songs, MaimaiSongs)
        return MaimaiScores(b35=self.scores_b35, b15=self.scores_b15, all=distinct_scores, songs=songs)

    def by_song(self, song_id: int, song_type: SongType = None, level_index: LevelIndex = None) -> list[Score]:
        """Get scores of the song on that type and level_index.

        If song_type or level_index is not provided, all scores of the song will be returned.

        Args:
            song_id: the ID of the song to get the scores by.
            song_type: the type of the song to get the scores by, defaults to None.
            level_index: the level index of the song to get the scores by, defaults to None.
        Returns:
            the list of scores of the song, return an empty list if no score is found.
        """
        scores = [score for score in self.scores if score.id == song_id]
        if song_type:
            scores = [score for score in scores if score.type == song_type]
        if level_index:
            scores = [score for score in scores if score.level_index == level_index]
        return scores

    def filter(self, **kwargs) -> list[Score]:
        """Filter scores by their attributes.

        Make sure the attribute is of the score, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the scores by.
        Returns:
            the list of scores that match all the conditions, return an empty list if no score is found.
        """
        return [score for score in self.scores if all(getattr(score, key) == value for key, value in kwargs.items())]
