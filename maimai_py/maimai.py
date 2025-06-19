import asyncio
import hashlib
from collections import defaultdict
from functools import cached_property
from typing import Any, Callable, Generic, Iterator, Literal, Type, TypeVar

from aiocache import BaseCache, SimpleMemoryCache
from httpx import AsyncClient
from maimai_ffi import arcade

from maimai_py.models import *
from maimai_py.providers import *
from maimai_py.utils import UNSET, _UnsetSentinel

PlayerItemType = TypeVar("PlayerItemType", bound=PlayerItem)


class MaimaiItems(Generic[PlayerItemType]):
    _client: "MaimaiClient"
    _namespace: str

    def __init__(self, client: "MaimaiClient", namespace: str) -> None:
        """@private"""
        self._client = client
        self._namespace = namespace

    async def _configure(self, provider: Union[IItemListProvider, _UnsetSentinel] = UNSET) -> "MaimaiItems":
        # Check if the provider is unset, which means we want to access the cache directly.
        if isinstance(provider, _UnsetSentinel):
            if await self._client._cache.get("provider", None, namespace=self._namespace) is not None:
                return self
        # Really assign the unset provider to the default one.
        provider = LXNSProvider() if PlayerItemType in [PlayerIcon, PlayerNamePlate, PlayerFrame] else LocalProvider()
        # Check if the current provider hash is different from the previous one, which means we need to reconfigure the songs.
        current_provider_hash = provider._hash()
        previous_provider_hash = await self._client._cache.get("provider", "", namespace=self._namespace)
        # If different or previous is empty, we need to reconfigure the items.
        if current_provider_hash != previous_provider_hash:
            val: dict[int, Any] = await getattr(provider, f"get_{self._namespace}")(self._client)
            await self._client._cache.set("ids", [key for key in val.keys()], namespace=self._namespace)
            await self._client._cache.multi_set(val.items(), namespace=self._namespace)
            await self._client._cache.set("provider", hash(provider), ttl=self._client._cache_ttl, namespace=self._namespace)
        return self

    async def get_all(self) -> list[PlayerItemType]:
        """All items as list.

        This method will iterate all items in the cache, and yield each item one by one. Unless you really need to iterate all items, you should use `by_id` or `filter` instead.

        Returns:
            A list with all items in the cache, return an empty list if no item is found.
        """
        item_ids: Union[list[int], None] = await self._client._cache.get("ids", namespace=self._namespace)
        assert item_ids is not None, f"Items not found in cache {self._namespace}, please call configure() first."
        return await self._client._cache.multi_get(item_ids, namespace=self._namespace)

    async def get_batch(self, ids: list[int]) -> list[PlayerItemType]:
        """Get items by their IDs.

        Args:
            ids: the IDs of the items.
        Returns:
            A list of items if they exist, otherwise return an empty list.
        """
        return await self._client._cache.multi_get(ids, namespace=self._namespace)

    async def by_id(self, id: int) -> Union[PlayerItemType, None]:
        """Get an item by its ID.

        Args:
            id: the ID of the item.
        Returns:
            the item if it exists, otherwise return None.
        """
        return await self._client._cache.get(id, namespace=self._namespace)

    async def filter(self, **kwargs) -> list[PlayerItemType]:
        """Filter items by their attributes.

        Ensure that the attribute is of the item, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the items by.
        Returns:
            an async generator yielding items that match all the conditions, yields no items if no item is found.
        """
        cond = lambda item: all(getattr(item, key) == value for key, value in kwargs.items() if value is not None)
        return [item for item in await self.get_all() if cond(item)]


class MaimaiSongs:
    _client: "MaimaiClient"

    def __init__(self, client: "MaimaiClient") -> None:
        """@private"""
        self._client = client

    async def _configure(
        self,
        provider: Union[ISongProvider, _UnsetSentinel],
        alias_provider: Union[IAliasProvider, None, _UnsetSentinel],
        curve_provider: Union[ICurveProvider, None, _UnsetSentinel],
    ) -> "MaimaiSongs":
        # Check if all providers are unset, which means we want to access the cache directly.
        if isinstance(provider, _UnsetSentinel) and isinstance(alias_provider, _UnsetSentinel) and isinstance(curve_provider, _UnsetSentinel):
            if await self._client._cache.get("provider", None, namespace="songs") is not None:
                return self
        # Really assign the unset providers to the default ones.
        provider = provider if not isinstance(provider, _UnsetSentinel) else LXNSProvider()
        alias_provider = alias_provider if not isinstance(alias_provider, _UnsetSentinel) else YuzuProvider()
        curve_provider = curve_provider if not isinstance(curve_provider, _UnsetSentinel) else None  # Don't fetch curves if not provided.
        # Check if the current provider hash is different from the previous one, which means we need to reconfigure the songs.
        current_provider_hash = hashlib.md5(
            (provider._hash() + (alias_provider._hash() if alias_provider else "") + (curve_provider._hash() if curve_provider else "")).encode()
        ).hexdigest()
        previous_provider_hash = await self._client._cache.get("provider", "", namespace="songs")
        # If different or previous is empty, we need to reconfigure the songs.
        if current_provider_hash != previous_provider_hash:
            # Get the resources from the providers in parallel.
            songs_task = asyncio.create_task(provider.get_songs(self._client))
            aliases_task = asyncio.create_task(alias_provider.get_aliases(self._client)) if alias_provider else None
            curves_task = asyncio.create_task(curve_provider.get_curves(self._client)) if curve_provider else None
            songs, aliases, curves = await songs_task, (await aliases_task if aliases_task else []), (await curves_task if curves_task else {})

            id_task = asyncio.create_task(self._client._cache.set("ids", [song.id for song in songs], namespace="songs"))
            version_task = asyncio.create_task(
                self._client._cache.set(
                    "versions",
                    {f"{song.id} {diff.type} {diff.level_index}": diff.version for song in songs for diff in song.difficulties._get_children()},
                    namespace="songs",
                )
            )
            track_task = asyncio.create_task(self._client._cache.multi_set(iter((song.title, song.id) for song in songs), namespace="tracks"))
            alias_task = asyncio.create_task(
                self._client._cache.multi_set(iter((entry, alias.song_id) for alias in aliases for entry in alias.aliases), namespace="aliases")
            )
            aliases_dict = {alias.song_id: alias.aliases for alias in aliases}
            curves_dict = {song_id: curve for song_id, curve in curves.items()}

            for song in songs:
                if alias_provider is not None and (aliases := aliases_dict.get(song.id, None)):
                    song.aliases = aliases
                if curve_provider is not None:
                    if curves := curves_dict.get((song.id, SongType.DX), None):
                        diffs = song.difficulties._get_children(SongType.DX)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs) if i < len(curves)]
                    if curves := curves_dict.get((song.id, SongType.STANDARD), None):
                        diffs = song.difficulties._get_children(SongType.STANDARD)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs) if i < len(curves)]
                    if curves := curves_dict.get((song.id, SongType.UTAGE), None):
                        diffs = song.difficulties._get_children(SongType.UTAGE)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs) if i < len(curves)]

            song_task = asyncio.create_task(self._client._cache.multi_set(iter((song.id, song) for song in songs), namespace="songs"))
            provider_task = asyncio.create_task(
                self._client._cache.set("provider", current_provider_hash, ttl=self._client._cache_ttl, namespace="songs")
            )
            await asyncio.gather(id_task, version_task, track_task, alias_task, song_task, provider_task)
        return self

    async def get_all(self) -> list[Song]:
        """All songs as list.

        This method will iterate all songs in the cache, and yield each song one by one. Unless you really need to iterate all songs, you should use `by_id` or `filter` instead.

        Returns:
            A list of all songs in the cache, return an empty list if no song is found.
        """
        song_ids: Union[list[int], None] = await self._client._cache.get("ids", namespace="songs")
        assert song_ids is not None, "Songs not found in cache, please call configure() first."
        return await self._client._cache.multi_get(song_ids, namespace="songs")

    async def get_batch(self, ids: list[int]) -> list[Song]:
        """Get songs by their IDs.

        Args:
            ids: the IDs of the songs.
        Returns:
            A list of songs if they exist, otherwise return an empty list.
        """
        return await self._client._cache.multi_get(ids, namespace="songs")

    async def by_id(self, id: int) -> Union[Song, None]:
        """Get a song by its ID.

        Args:
            id: the ID of the song, always smaller than `10000`, should (`% 10000`) if necessary.
        Returns:
            the song if it exists, otherwise return None.
        """
        return await self._client._cache.get(id, namespace="songs")

    async def by_title(self, title: str) -> Union[Song, None]:
        """Get a song by its title.

        Args:
            title: the title of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        song_id = await self._client._cache.get(title, namespace="tracks")
        song_id = 383 if title == "Link(CoF)" else song_id
        return await self._client._cache.get(song_id, namespace="songs") if song_id else None

    async def by_alias(self, alias: str) -> Union[Song, None]:
        """Get song by one possible alias.

        Args:
            alias: one possible alias of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        if song_id := await self._client._cache.get(alias, namespace="aliases"):
            if song := await self._client._cache.get(song_id, namespace="songs"):
                return song

    async def by_artist(self, artist: str) -> list[Song]:
        """Get songs by their artist, case-sensitive.

        Args:
            artist: the artist of the songs.
        Returns:
            an async generator yielding songs that match the artist.
        """
        return [song for song in await self.get_all() if song.artist == artist]

    async def by_genre(self, genre: Genre) -> list[Song]:
        """Get songs by their genre, case-sensitive.

        Args:
            genre: the genre of the songs.
        Returns:
            an async generator yielding songs that match the genre.
        """
        return [song for song in await self.get_all() if song.genre == genre]

    async def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
        """Get songs by their BPM.

        Args:
            minimum: the minimum (inclusive) BPM of the songs.
            maximum: the maximum (inclusive) BPM of the songs.
        Returns:
            an async generator yielding songs that match the BPM.
        """
        return [song for song in await self.get_all() if minimum <= song.bpm <= maximum]

    async def by_versions(self, versions: Version) -> list[Song]:
        """Get songs by their versions, versions are fuzzy matched version of major maimai version.

        Args:
            versions: the versions of the songs.
        Returns:
            an async generator yielding songs that match the versions.
        """
        cond = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value
        return [song for song in await self.get_all() if cond(song)]

    async def by_keywords(self, keywords: str) -> list[Song]:
        """Get songs by their keywords, keywords are matched with song title, artist and aliases.

        Args:
            keywords: the keywords to match the songs.
        Returns:
            an async generator yielding songs that match the keywords.
        """
        cond = lambda song: keywords.lower() in f"{song.title} + {song.artist} + {''.join(a for a in (song.aliases or []))}".lower()
        return [song for song in await self.get_all() if cond(song)]

    async def filter(self, **kwargs) -> list[Song]:
        """Filter songs by their attributes.

        Ensure that the attribute is of the song, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the songs by.
        Returns:
            an async generator yielding songs that match all the conditions.
        """
        cond = lambda song: all(getattr(song, key) == value for key, value in kwargs.items() if value is not None)
        return [song for song in await self.get_all() if cond(song)]


class MaimaiPlates:
    _client: "MaimaiClient"
    _maimai_songs: MaimaiSongs

    _kind: str  # The kind of the plate, e.g. "将", "神".
    _version: str  # The version of the plate, e.g. "真", "舞".
    _versions: set[Version] = set()  # The matched versions set of the plate.
    _matched_songs: list[Song] = []
    _matched_scores: list[Score] = []

    def __init__(self, client: "MaimaiClient") -> None:
        """@private"""
        self._client = client

    async def _configure(self, plate: str, scores: list[Score]) -> "MaimaiPlates":
        self._maimai_songs = await self._client.songs()
        self._version = plate_aliases.get(plate[0], plate[0])
        self._kind = plate_aliases.get(plate[1:], plate[1:])

        versions = list()  # in case of invalid plate, we will raise an error
        if self._version == "真":
            versions = [plate_to_version["初"], plate_to_version["真"]]
        if self._version in ["霸", "舞"]:
            versions = [ver for ver in plate_to_version.values() if ver.value < 20000]
        if plate_to_version.get(self._version):
            versions = [plate_to_version[self._version]]
        if not versions or self._kind not in ["将", "者", "极", "舞舞", "神"]:
            raise InvalidPlateError(f"Invalid plate: {self._version}{self._kind}")
        versions.append([ver for ver in plate_to_version.values() if ver.value > versions[-1].value][0])
        self._versions = set(versions)

        song_diff_versions: dict[str, int] = await self._client._cache.get("versions", namespace="songs") or {}
        versioned_matched_songs = set()
        for k, v in song_diff_versions.items():
            if any(v >= o.value and v < versions[i + 1].value for i, o in enumerate(versions[:-1])):
                versioned_matched_songs.add(int(k.split(" ")[0]))
        self._matched_songs = await self._client._cache.multi_get(list(versioned_matched_songs), namespace="songs")

        versioned_joined_scores: dict[str, Score] = {}
        for score in scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            if score_version := song_diff_versions.get(score_key, None):
                if any(score_version >= o.value and score_version < versions[i + 1].value for i, o in enumerate(versions[:-1])):
                    if not (score.level_index == LevelIndex.ReMASTER and self.no_remaster):
                        versioned_joined_scores[score_key] = score._join(versioned_joined_scores.get(score_key, None))

        self._matched_scores = list(versioned_joined_scores.values())
        return self

    @cached_property
    def _major_type(self) -> SongType:
        return SongType.DX if any(ver.value > 20000 for ver in self._versions) else SongType.STANDARD

    @cached_property
    def no_remaster(self) -> bool:
        """Whether it is required to play ReMASTER levels in the plate.

        Only 舞 and 霸 plates require ReMASTER levels, others don't.
        """

        return self._version not in ["舞", "霸"]

    def _get_levels(self, song: Song) -> set[LevelIndex]:
        levels = set(diff.level_index for diff in song.difficulties._get_children(self._major_type))
        if self.no_remaster and LevelIndex.ReMASTER in levels:
            levels.remove(LevelIndex.ReMASTER)
        return levels

    async def get_remained(self) -> list[PlateObject]:
        """Get the remained songs and scores of the player on this plate.

        If player has ramained levels on one song, the song and ramained `level_index` will be included in the result, otherwise it won't.

        The distinct scores which NOT met the plate requirement will be included in the result, the finished scores won't.

        Returns:
            A list of `PlateObject` containing the song and the scores.
        """
        # Group scores by song ID to pre-fill the PlateObject.
        grouped = defaultdict(list)
        [grouped[score.id].append(score) for score in self._matched_scores]
        # Create PlateObject for each song with its levels and scores.
        results = {song.id: PlateObject(song=song, levels=self._get_levels(song), scores=grouped.get(song.id, [])) for song in self._matched_songs}

        def extract(score: Score) -> None:
            results[score.id].scores.remove(score)
            if score.level_index in results[score.id].levels:
                results[score.id].levels.remove(score.level_index)

        if self._kind == "者":
            [extract(score) for score in self._matched_scores if score.rate.value <= RateType.A.value]
        elif self._kind == "将":
            [extract(score) for score in self._matched_scores if score.rate.value <= RateType.SSS.value]
        elif self._kind == "极":
            [extract(score) for score in self._matched_scores if score.fc and score.fc.value <= FCType.FC.value]
        elif self._kind == "舞舞":
            [extract(score) for score in self._matched_scores if score.fs and score.fs.value <= FSType.FSD.value]
        elif self._kind == "神":
            [extract(score) for score in self._matched_scores if score.fc and score.fc.value <= FCType.AP.value]

        return [plate for plate in results.values() if len(plate.levels) > 0]

    async def get_cleared(self) -> list[PlateObject]:
        """Get the cleared songs and scores of the player on this plate.

        If player has levels (one or more) that met the requirement on the song, the song and cleared `level_index` will be included in the result, otherwise it won't.

        The distinct scores which met the plate requirement will be included in the result, the unfinished scores won't.

        Returns:
            A list of `PlateObject` containing the song and the scores.
        """
        results = {song.id: PlateObject(song=song, levels=set(), scores=[]) for song in self._matched_songs}

        def insert(score: Score) -> None:
            results[score.id].scores.append(score)
            results[score.id].levels.add(score.level_index)

        if self._kind == "者":
            [insert(score) for score in self._matched_scores if score.rate.value <= RateType.A.value]
        elif self._kind == "将":
            [insert(score) for score in self._matched_scores if score.rate.value <= RateType.SSS.value]
        elif self._kind == "极":
            [insert(score) for score in self._matched_scores if score.fc and score.fc.value <= FCType.FC.value]
        elif self._kind == "舞舞":
            [insert(score) for score in self._matched_scores if score.fs and score.fs.value <= FSType.FSD.value]
        elif self._kind == "神":
            [insert(score) for score in self._matched_scores if score.fc and score.fc.value <= FCType.AP.value]

        return [plate for plate in results.values() if len(plate.levels) > 0]

    async def get_played(self) -> list[PlateObject]:
        """Get the played songs and scores of the player on this plate.

        If player has ever played levels on the song, whether they met or not, the song and played `level_index` will be included in the result.

        All distinct scores will be included in the result.

        Returns:
            A list of `PlateObject` containing the song and the scores.
        """
        results = {song.id: PlateObject(song=song, levels=set(), scores=[]) for song in self._matched_songs}

        for score in self._matched_scores:
            results[score.id].scores.append(score)
            results[score.id].levels.add(score.level_index)

        return [plate for plate in results.values() if len(plate.levels) > 0]

    async def get_all(self) -> list[PlateObject]:
        """Get all songs and scores on this plate, usually used for overall statistics of the plate.

        All songs will be included in the result, with played `level_index`, whether they met or not.

        All distinct scores will be included in the result.

        Returns:
            A list of `PlateObject` containing the song and the scores.
        """
        results = {song.id: PlateObject(song=song, levels=set(), scores=[]) for song in self._matched_songs}

        for score in self._matched_scores:
            results[score.id].scores.append(score)
            results[score.id].levels.add(score.level_index)

        return [plate for plate in results.values()]

    async def count_played(self) -> int:
        """Get the number of played levels on this plate.

        Returns:
            The number of played levels on this plate.
        """
        return len([level for plate in await self.get_played() for level in plate.levels])

    async def count_cleared(self) -> int:
        """Get the number of cleared levels on this plate.

        Returns:
            The number of cleared levels on this plate.
        """
        return len([level for plate in await self.get_cleared() for level in plate.levels])

    async def count_remained(self) -> int:
        """Get the number of remained levels on this plate.

        Returns:
            The number of remained levels on this plate.
        """
        return len([level for plate in await self.get_remained() for level in plate.levels])

    async def count_all(self) -> int:
        """Get the number of all levels on this plate.

        Returns:
            The number of all levels on this plate.
        """
        return sum(len(self._get_levels(plate.song)) for plate in await self.get_all())


class MaimaiScores:
    _client: "MaimaiClient"

    scores: list[Score]
    """All scores of the player."""
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

    def __init__(self, client: "MaimaiClient"):
        self._client = client

    async def configure(self, scores: list[Score]) -> "MaimaiScores":
        """Initialize the scores by the scores list.

        This method will sort the scores by their dx_rating, dx_score and achievements, and split them into b35 and b15 scores.

        Args:
            scores: the scores list to initialize.
        Returns:
            The MaimaiScores object with the scores initialized.
        """
        self.scores = scores
        scores_new: list[Score] = []
        scores_old: list[Score] = []
        await self._client.songs()  # ensure songs are cached

        scores_unique: dict[str, Score] = {}
        for score in self.scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))

        song_diff_versions: dict[str, int] = await self._client._cache.get("versions", namespace="songs") or {}
        for score in scores_unique.values():
            if score_version := song_diff_versions.get(f"{score.id} {score.type} {score.level_index}", None):
                (scores_new if score_version >= current_version.value else scores_old).append(score)

        scores_old.sort(key=lambda score: (score.dx_rating or 0, score.dx_score or 0, score.achievements or 0), reverse=True)
        scores_new.sort(key=lambda score: (score.dx_rating or 0, score.dx_score or 0, score.achievements or 0), reverse=True)
        self.scores_b35 = scores_old[:35]
        self.scores_b15 = scores_new[:15]
        self.rating_b35 = int(sum((score.dx_rating or 0) for score in self.scores_b35))
        self.rating_b15 = int(sum((score.dx_rating or 0) for score in self.scores_b15))
        self.rating = self.rating_b35 + self.rating_b15
        return self

    async def get_distinct(self) -> "MaimaiScores":
        """Get the distinct scores.

        Normally, player has more than one score for the same song and level, this method will return a new `MaimaiScores` object with the highest scores for each song and level.

        This method won't modify the original scores object, it will return a new one.

        Returns:
            A new `MaimaiScores` object with the distinct scores.
        """
        scores_unique = {}
        for score in self.scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))
        new_scores = MaimaiScores(self._client)
        return await new_scores.configure(list(scores_unique.values()))

    def by_song(
        self, song_id: int, song_type: Union[SongType, _UnsetSentinel] = UNSET, level_index: Union[LevelIndex, _UnsetSentinel] = UNSET
    ) -> Iterator[Score]:
        """Get scores of the song on that type and level_index.

        If song_type or level_index is not provided, all scores of the song will be returned.

        Args:
            song_id: the ID of the song to get the scores by.
            song_type: the type of the song to get the scores by, defaults to None.
            level_index: the level index of the song to get the scores by, defaults to None.
        Returns:
            an iterator of scores of the song, return an empty iterator if no score is found.
        """
        return (
            score
            for score in self.scores
            if score.id == song_id and (song_type is UNSET or score.type == song_type) and (level_index is UNSET or score.level_index == level_index)
        )

    def filter(self, **kwargs) -> Iterator[Score]:
        """Filter scores by their attributes.

        Make sure the attribute is of the score, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the scores by.
        Returns:
            an iterator of scores that match all the conditions, yields no items if no score is found.
        """

        return (score for score in self.scores if all(getattr(score, key) == value for key, value in kwargs.items()))


class MaimaiAreas:
    _client: "MaimaiClient"
    _lang: str

    def __init__(self, client: "MaimaiClient") -> None:
        """@private"""
        self._client = client

    async def _configure(self, lang: str, provider: Union[IAreaProvider, _UnsetSentinel]) -> "MaimaiAreas":
        self._lang = lang
        # Check if the provider is unset, which means we want to access the cache directly.
        if isinstance(provider, _UnsetSentinel):
            if await self._client._cache.get("provider", None, namespace=f"areas_{lang}") is not None:
                return self
        # Really assign the unset provider to the default one.
        provider = provider if not isinstance(provider, _UnsetSentinel) else LocalProvider()
        # If different or previous is empty, we need to reconfigure the areas.
        if hash(provider) != await self._client._cache.get("provider", "", namespace=f"areas_{lang}"):
            areas = await provider.get_areas(lang, self._client)
            tasks = [
                asyncio.create_task(self._client._cache.set("ids", [area.id for area in areas.values()], namespace=f"areas_{lang}")),
                asyncio.create_task(self._client._cache.multi_set(iter((k, v) for k, v in areas.items()), namespace=f"areas_{lang}")),
                asyncio.create_task(self._client._cache.set("provider", hash(provider), ttl=self._client._cache_ttl, namespace=f"areas_{lang}")),
            ]
            await asyncio.gather(*tasks)
        return self

    async def get_all(self) -> list[Area]:
        """All areas as list.

        This method will iterate all areas in the cache. Unless you really need to iterate all areas, you should use `by_id` or `by_name` instead.

        Returns:
            A list of all areas in the cache, return an empty list if no area is found.
        """
        area_ids: Union[list[int], None] = await self._client._cache.get("ids", namespace=f"areas_{self._lang}")
        assert area_ids is not None, "Areas not found in cache, please call configure() first."
        return await self._client._cache.multi_get(area_ids, namespace=f"areas_{self._lang}")

    async def get_batch(self, ids: list[str]) -> list[Area]:
        """Get areas by their IDs.

        Args:
            ids: the IDs of the areas.
        Returns:
            A list of areas if they exist, otherwise return an empty list.
        """
        return await self._client._cache.multi_get(ids, namespace=f"areas_{self._lang}")

    async def by_id(self, id: str) -> Union[Area, None]:
        """Get an area by its ID.

        Args:
            id: the ID of the area.
        Returns:
            the area if it exists, otherwise return None.
        """
        return await self._client._cache.get(id, namespace=f"areas_{self._lang}")

    async def by_name(self, name: str) -> Union[Area, None]:
        """Get an area by its name, language-sensitive.

        Args:
            name: the name of the area.
        Returns:
            the area if it exists, otherwise return None.
        """
        return next((area for area in await self.get_all() if area.name == name), None)


class MaimaiClient:
    """The main client of maimai.py."""

    _client: AsyncClient
    _cache: BaseCache
    _cache_ttl: int

    def __init__(
        self,
        timeout: float = 20.0,
        cache: Union[BaseCache, _UnsetSentinel] = UNSET,
        cache_ttl: int = 60 * 60 * 24,
        **kwargs,
    ) -> None:
        """Initialize the maimai.py client.

        Args:
            timeout: the timeout of the requests, defaults to 20.0.
            cache: the cache to use, defaults to `aiocache.SimpleMemoryCache()`.
            cache_ttl: the TTL of the cache, defaults to 60 * 60 * 24.
            kwargs: other arguments to pass to the `httpx.AsyncClient`.
        """
        self._client = AsyncClient(timeout=timeout, **kwargs)
        self._cache = SimpleMemoryCache() if isinstance(cache, _UnsetSentinel) else cache
        self._cache_ttl = cache_ttl

    async def songs(
        self,
        provider: Union[ISongProvider, _UnsetSentinel] = UNSET,
        alias_provider: Union[IAliasProvider, None, _UnsetSentinel] = UNSET,
        curve_provider: Union[ICurveProvider, None, _UnsetSentinel] = UNSET,
    ) -> MaimaiSongs:
        """Fetch all maimai songs from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Available alias providers: `YuzuProvider`, `LXNSProvider`.

        Available curve providers: `DivingFishProvider`.

        Args:
            provider: override the data source to fetch the player from, defaults to `LXNSProvider`.
            alias_provider: override the data source to fetch the song aliases from, defaults to `YuzuProvider`.
            curve_provider: override the data source to fetch the song curves from, defaults to `None`.
        Returns:
            A wrapper of the song list, for easier access and filtering.
        Raises:
            httpx.HTTPError: Request failed due to network issues.
        """
        songs = MaimaiSongs(self)
        return await songs._configure(provider, alias_provider, curve_provider)

    async def players(
        self,
        identifier: PlayerIdentifier,
        provider: IPlayerProvider = LXNSProvider(),
    ) -> Player:
        """Fetch player data from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `ArcadeProvider`.

        Possible returns: `DivingFishPlayer`, `LXNSPlayer`, `ArcadePlayer`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(username="turou")`.
            provider: the data source to fetch the player from, defaults to `LXNSProvider`.
        Returns:
            The player object of the player, with all the data fetched. Depending on the provider, it may contain different objects that derived from `Player`.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        return await provider.get_player(identifier, self)

    async def scores(
        self,
        identifier: PlayerIdentifier,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiScores:
        """Fetch player's ALL scores from the provider.

        All scores of the player will be fetched, if you want to fetch only the best scores (for better performance), use `maimai.bests()` instead.

        For WechatProvider, PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.
        Also, PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

        For ArcadeProvider, PlayerIdentifier must have the `credentials` attribute, which is the player's encrypted userId, can be detrived from `maimai.aime()`.
        Credentials can be reused, since it won't expire, also, userId is encrypted, can't be used in any other cases outside the maimai.py

        For more information about the PlayerIdentifier of providers, please refer to the documentation of each provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            The scores object of the player, with all the data fetched.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerNetworkError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            TitleServerBlockedError: Only for ArcadeProvider, maimai title server blocked the request, possibly due to ip filtered.
            ArcadeIdentifierError: Only for ArcadeProvider, maimai user id is invalid, or the user is not found.
        """
        scores = await provider.get_scores_all(identifier, self)

        maimai_scores = MaimaiScores(self)
        return await maimai_scores.configure(scores)

    async def bests(
        self,
        identifier: PlayerIdentifier,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiScores:
        """Fetch player's B50 scores from the provider.

        Though MaimaiScores is used, this method will only return the best 50 scores. if you want all scores, please use `maimai.scores()` method instead.

        For WechatProvider, PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.
        Also, PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

        For ArcadeProvider, PlayerIdentifier must have the `credentials` attribute, which is the player's encrypted userId, can be detrived from `maimai.aime()`.
        Credentials can be reused, since it won't expire, also, userId is encrypted, can't be used in any other cases outside the maimai.py

        For more information about the PlayerIdentifier of providers, please refer to the documentation of each provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            The scores object of the player, with all the data fetched.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerNetworkError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            TitleServerBlockedError: Only for ArcadeProvider, maimai title server blocked the request, possibly due to ip filtered.
            ArcadeIdentifierError: Only for ArcadeProvider, maimai user id is invalid, or the user is not found.
        """
        scores = await provider.get_scores_best(identifier, self)

        maimai_scores = MaimaiScores(self)
        return await maimai_scores.configure(scores)

    async def minfo(
        self,
        song: Union[Song, int, str],
        identifier: PlayerIdentifier,
        provider: IScoreProvider = LXNSProvider(),
    ) -> tuple[Union[Song, None], list[Score]]:
        """Fetch player's scores on the specific song.

        This method will return all scores of the player on the song.

        For more information about the PlayerIdentifier of providers, please refer to the documentation of each provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`, `ArcadeProvider`.

        Args:
            song: the song to fetch the scores from, can be a `Song` object, or a song_id (int), or keywords (str).
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            A tuple of the song and the scores of the player on the song. If the song is not found, the song will be None and scores will be an empty list.
            If the song is found, the song will be a `Song` object and scores will be a list of `Score` objects.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerNetworkError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            TitleServerBlockedError: Only for ArcadeProvider, maimai title server blocked the request, possibly due to ip filtered.
            ArcadeIdentifierError: Only for ArcadeProvider, maimai user id is invalid, or the user is not found.
        """
        maimai_songs = await self.songs()
        if isinstance(song, str):
            search_result = await maimai_songs.by_keywords(song)
            song = search_result[0] if len(search_result) > 0 else song
        if isinstance(song, int):
            search_result = await maimai_songs.by_id(song)
            song = search_result if search_result is not None else song
        if isinstance(song, Song):
            scores = await provider.get_scores_one(identifier, song, self)
            return song, scores
        return None, []

    async def regions(self, identifier: PlayerIdentifier, provider: IRegionProvider = ArcadeProvider()) -> list[PlayerRegion]:
        """Get the player's regions that they have played.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(credentials="encrypted_user_id")`.
            provider: the data source to fetch the player from, defaults to `ArcadeProvider`.
        Returns:
            The list of regions that the player has played.
        Raises:
            TitleServerNetworkError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            TitleServerBlockedError: Only for ArcadeProvider, maimai title server blocked the request, possibly due to ip filtered.
            ArcadeIdentifierError: Only for ArcadeProvider, maimai user id is invalid, or the user is not found.
        """
        return await provider.get_regions(identifier, self)

    async def updates(
        self,
        identifier: PlayerIdentifier,
        scores: list[Score],
        provider: IScoreUpdateProvider = LXNSProvider(),
    ) -> None:
        """Update player's scores to the provider.

        This method is used to update the player's scores to the provider, usually used for updating scores fetched from other providers.

        For more information about the PlayerIdentifier of providers, please refer to the documentation of each provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Args:
            identifier: the identifier of the player to update, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            scores: the scores to update, usually the scores fetched from other providers.
            provider: the data source to update the player scores to, defaults to `LXNSProvider`.
        Returns:
            Nothing, failures will raise exceptions.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found, or the import token / password is invalid.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        """
        await provider.update_scores(identifier, scores, self)

    async def plates(
        self,
        identifier: PlayerIdentifier,
        plate: str,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiPlates:
        """Get the plate achievement of the given player and plate.

        Available providers: `DivingFishProvider`, `LXNSProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            plate: the name of the plate, e.g. "樱将", "真舞舞".
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            A wrapper of the plate achievement, with plate information, and matched player scores.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidPlateError: Provided version or plate is invalid.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerNetworkError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            TitleServerBlockedError: Only for ArcadeProvider, maimai title server blocked the request, possibly due to ip filtered.
            ArcadeIdentifierError: Only for ArcadeProvider, maimai user id is invalid, or the user is not found.
        """
        # songs = await MaimaiSongs._get_or_fetch(self._client)
        scores = await provider.get_scores_all(identifier, self)
        maimai_plates = MaimaiPlates(self)
        return await maimai_plates._configure(plate, scores)

    async def wechat(self) -> str:
        """Get the wechat oauth url from the Wahlap Wechat OffiAccount.

        Access the url in user's wechat client, then redirect the user to the URL with your mitmproxy enabled.

        Your mitmproxy should intercept the response from tgk-wcaime.wahlap.com, which should contains t, r, code, and state parameters in the URL.

        Then call `maimai.identifiers(provider=WechatProvider, code=...)` with the parameters from the intercepted response.

        Returns:
            The URL to get the identifier.
        Raises:
            httpx.HTTPError: Request failed due to network issues.
        """
        resp = await self._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
        return resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")

    async def identifiers(
        self,
        code: Union[str, dict[str, str]],
        provider: Union[IPlayerIdentifierProvider, _UnsetSentinel] = UNSET,
    ) -> PlayerIdentifier:
        """Get the player identifier from the provider.

        Player identifier is the encrypted userId, can't be used in any other cases outside the maimai.py.

        Available providers: `WechatProvider`, `ArcadeProvider`.

        Args:
            code: the code to get the player identifier, can be a string or a dictionary with `r`, `t`, `code`, and `state` keys.
            provider: override the default provider, defaults to `ArcadeProvider`.
        Returns:
            The player identifier of the player.
        Raises:
            InvalidWechatTokenError: Wechat token is expired, please re-authorize.
            AimeServerError: Maimai Aime server error, may be invalid QR code or QR code has expired.
            httpx.HTTPError: Request failed due to network issues.
        """
        if isinstance(provider, _UnsetSentinel):
            provider = ArcadeProvider()
        return await provider.get_identifier(code, self)

    async def items(self, item: Type[PlayerItemType], provider: Union[IItemListProvider, _UnsetSentinel] = UNSET) -> MaimaiItems[PlayerItemType]:
        """Fetch maimai player items from the cache default provider.

        Available items: `PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`.

        Args:
            item: the item type to fetch, e.g. `PlayerIcon`.
            provider: override the default item list provider, defaults to `LXNSProvider` and `LocalProvider`.
        Returns:
            A wrapper of the item list, for easier access and filtering.
        Raises:
            FileNotFoundError: The item file is not found.
            httpx.HTTPError: Request failed due to network issues.
        """

        maimai_items = MaimaiItems[PlayerItemType](self, item._namespace())
        return await maimai_items._configure(provider)

    async def areas(self, lang: Literal["ja", "zh"] = "ja", provider: IAreaProvider = LocalProvider()) -> MaimaiAreas:
        """Fetch maimai areas from the provider.

        Available providers: `LocalProvider`.

        Args:
            lang: the language of the area to fetch, available languages: `ja`, `zh`.
            provider: override the default area provider, defaults to `ArcadeProvider`.
        Returns:
            A wrapper of the area list, for easier access and filtering.
        Raises:
            FileNotFoundError: The area file is not found.
        """

        maimai_areas = MaimaiAreas(self)
        return await maimai_areas._configure(lang, provider)
