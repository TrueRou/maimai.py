import httpx
from typing import AsyncGenerator, Literal, Type
from httpx import AsyncClient
from aiocache import SimpleMemoryCache, BaseCache

from maimai_ffi import arcade
from maimai_py.enums import *
from maimai_py.models import *
from maimai_py.providers import *
from maimai_py.caches import default_caches
from maimai_py.exceptions import WechatTokenExpiredError
from maimai_py.utils.sentinel import UNSET, _UnsetSentinel

CachedType = TypeVar("CachedType", bound=CachedModel)


class MaimaiItems(Generic[CachedType]):
    _cached_items: dict[int, CachedType]

    def __init__(self, items: dict[int, CachedType]) -> None:
        """@private"""
        self._cached_items = items

    @property
    def values(self) -> Iterator[CachedType]:
        """All items as list."""
        return iter(self._cached_items.values())

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
    _client: AsyncClient
    _cache: BaseCache

    def __init__(self, client: AsyncClient, cache: BaseCache) -> None:
        """@private"""
        self._client = client
        self._cache = cache

    async def configure(self, provider: ISongProvider, alias_provider: IAliasProvider | None, curve_provider: ICurveProvider | None) -> "MaimaiSongs":
        current_provider_hash = hash(hash(provider) + hash(alias_provider) + hash(curve_provider))
        previous_provider_hash = await self._cache.get("provider_songs", "")
        if current_provider_hash != previous_provider_hash:
            songs = await provider.get_songs(self._client)
            aliases = await alias_provider.get_aliases(self._client) if alias_provider else []
            curves = await curve_provider.get_curves(self._client) if curve_provider else {}
            await self._cache.set("song_ids", [song.id for song in songs])
            await self._cache.multi_set(iter((f"alias_{entry}", alias.song_id) for alias in aliases for entry in alias.aliases))
            aliases_dict = {alias.song_id: alias.aliases for alias in aliases}
            curves_dict = {song_id: curve for song_id, curve in curves.items()}

            for song in songs:
                if alias_provider is not None and (aliases := aliases_dict.get(song.id, None)):
                    song.aliases = aliases
                if curve_provider is not None:
                    if curves := curves_dict.get((song.id, SongType.DX), None):
                        diffs = song.difficulties._get_children(SongType.DX)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs)]
                    if curves := curves_dict.get((song.id, SongType.STANDARD), None):
                        diffs = song.difficulties._get_children(SongType.STANDARD)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs)]
                    if curves := curves_dict.get((song.id, SongType.UTAGE), None):
                        diffs = song.difficulties._get_children(SongType.UTAGE)
                        [diff.__setattr__("curve", curves[i]) for i, diff in enumerate(diffs)]

            await self._cache.multi_set(iter((f"song_{song.id}", song) for song in songs))
            await self._cache.set("provider_songs", current_provider_hash, ttl=60 * 60 * 24)
        return self

    async def iter_songs(self) -> AsyncGenerator[Song]:
        """All songs as async generator."""
        song_ids: list[int] | None = await self._cache.get("song_ids")
        assert song_ids is not None, "Songs not found in cache, please call configure() first."
        for song_id in song_ids:
            if song := await self._cache.get(f"song_{song_id}"):
                yield song

    async def by_id(self, id: int) -> Song | None:
        """Get a song by its ID.

        Args:
            id: the ID of the song, always smaller than `10000`, should (`% 10000`) if necessary.
        Returns:
            the song if it exists, otherwise return None.
        """
        return await self._cache.get(f"song_{id}")

    async def by_title(self, title: str) -> Song | None:
        """Get a song by its title.

        Args:
            title: the title of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        if title == "Link(CoF)":
            return await self.by_id(383)
        return await anext((song async for song in self.iter_songs() if song.title == title), None)

    async def by_alias(self, alias: str) -> Song | None:
        """Get song by one possible alias.

        Args:
            alias: one possible alias of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        if song_id := await self._cache.get(f"alias_{alias}"):
            if song := await self._cache.get(f"song_{song_id}"):
                return song

    async def by_artist(self, artist: str) -> list[Song]:
        """Get songs by their artist, case-sensitive.

        Args:
            artist: the artist of the songs.
        Returns:
            the list of songs that match the artist, return an empty list if no song is found.
        """
        return [song async for song in self.iter_songs() if song.artist == artist]

    async def by_genre(self, genre: Genre) -> list[Song]:
        """Get songs by their genre, case-sensitive.

        Args:
            genre: the genre of the songs.
        Returns:
            the list of songs that match the genre, return an empty list if no song is found.
        """

        return [song async for song in self.iter_songs() if song.genre == genre]

    async def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
        """Get songs by their BPM.

        Args:
            minimum: the minimum (inclusive) BPM of the songs.
            maximum: the maximum (inclusive) BPM of the songs.
        Returns:
            the list of songs that match the BPM range, return an empty list if no song is found.
        """
        return [song async for song in self.iter_songs() if minimum <= song.bpm <= maximum]

    async def by_versions(self, versions: Version) -> list[Song]:
        """Get songs by their versions, versions are fuzzy matched version of major maimai version.

        Args:
            versions: the versions of the songs.
        Returns:
            the list of songs that match the versions, return an empty list if no song is found.
        """

        versions_func: Callable[[Song], bool] = lambda song: versions.value <= song.version < all_versions[all_versions.index(versions) + 1].value
        return [song async for song in self.iter_songs() if versions_func(song)]

    async def by_keywords(self, keywords: str) -> list[Song]:
        """Get songs by their keywords, keywords are matched with song title, artist and aliases.

        Args:
            keywords: the keywords to match the songs.
        Returns:
            the list of songs that match the keywords, return an empty list if no song is found.
        """
        keywords_func: Callable[[Song], bool] = (
            lambda song: keywords.lower() in f"{song.title} + {song.artist} + {''.join(a for a in (song.aliases or []))}".lower()
        )
        return [song async for song in self.iter_songs() if keywords_func(song)]

    async def filter(self, **kwargs) -> list[Song]:
        """Filter songs by their attributes.

        Ensure that the attribute is of the song, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the songs by.
        Returns:
            the list of songs that match all the conditions, return an empty list if no song is found.
        """
        if "id" in kwargs and kwargs["id"] is not None:
            # if id is provided, ignore other attributes, as id is unique
            return [item] if (item := await self.by_id(kwargs["id"])) else []
        filter_func: Callable[[Song], bool] = lambda song: all(getattr(song, key) == value for key, value in kwargs.items() if value is not None)
        return [song async for song in self.iter_songs() if filter_func(song)]


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
        versions = []  # in case of invalid plate, we will raise an error
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
                if difficulty := song.get_difficulty(score.type, score.level_index):
                    score_version = difficulty.version
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
    def all(self) -> Iterator[PlateObject]:
        """Get all songs on this plate, usually used for statistics of the plate.

        All songs will be included in the result, with all levels, whether they met or not.

        No scores will be included in the result, use played, cleared, remained to get the scores.
        """

        return iter(PlateObject(song=song, levels=song._get_level_indexes(self.major_type, self.no_remaster), scores=[]) for song in self.songs)

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
    _client: AsyncClient
    _cache: BaseCache

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

    def __init__(self, client: AsyncClient, cache: BaseCache, scores: list[Score]):
        self._client = client
        self._cache = cache
        self.scores = scores

    async def configure(self):
        # scores have to be distinct to calculate the bests
        maimai_songs: MaimaiSongs = MaimaiSongs(self._client, self._cache)
        scores_new: list[Score] = []
        scores_old: list[Score] = []
        for score in self.as_distinct.scores:
            if score_song := await maimai_songs.by_id(score.id):
                if score_diff := score_song.get_difficulty(score.type, score.level_index):
                    (scores_new if score_diff.version >= current_version.value else scores_old).append(score)
        scores_old.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
        scores_new.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
        self.scores_b35 = scores_old[:35]
        self.scores_b15 = scores_new[:15]
        self.rating_b35 = int(sum((score.dx_rating or 0) for score in self.scores_b35))
        self.rating_b15 = int(sum((score.dx_rating or 0) for score in self.scores_b15))
        self.rating = self.rating_b35 + self.rating_b15

    @property
    def as_distinct(self) -> "MaimaiScores":
        """Get the distinct scores.

        Normally, player has more than one score for the same song and level, this method will return a new `MaimaiScores` object with the highest scores for each song and level.

        This method won't modify the original scores object, it will return a new one.
        """
        scores_unique = {}
        for score in self.scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))
        return MaimaiScores(self._client, self._cache, list(scores_unique.values()))

    def by_song(
        self, song_id: int, song_type: SongType | _UnsetSentinel = UNSET, level_index: LevelIndex | _UnsetSentinel = UNSET
    ) -> Iterator[Score]:
        """Get scores of the song on that type and level_index.

        If song_type or level_index is not provided, all scores of the song will be returned.

        Args:
            song_id: the ID of the song to get the scores by.
            song_type: the type of the song to get the scores by, defaults to None.
            level_index: the level index of the song to get the scores by, defaults to None.
        Returns:
            the list of scores of the song, return an empty list if no score is found.
        """
        for score in self.scores:
            if score.id != song_id:
                continue
            if song_type is not UNSET and score.type != song_type:
                continue
            if level_index is not UNSET and score.level_index != level_index:
                continue
            yield score

    def filter(self, **kwargs) -> list[Score]:
        """Filter scores by their attributes.

        Make sure the attribute is of the score, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the scores by.
        Returns:
            the list of scores that match all the conditions, return an empty list if no score is found.
        """
        return [score for score in self.scores if all(getattr(score, key) == value for key, value in kwargs.items())]


class MaimaiAreas:
    lang: str
    """The language of the areas."""

    _area_id_dict: dict[str, Area]  # area_id: area

    def __init__(self, lang: str, areas: dict[str, Area]) -> None:
        """@private"""
        self.lang = lang
        self._area_id_dict = areas

    @property
    def values(self) -> Iterator[Area]:
        """All areas as list."""
        return iter(self._area_id_dict.values())

    def by_id(self, id: str) -> Area | None:
        """Get an area by its ID.

        Args:
            id: the ID of the area.
        Returns:
            the area if it exists, otherwise return None.
        """
        return self._area_id_dict.get(id, None)

    def by_name(self, name: str) -> Area | None:
        """Get an area by its name, language-sensitive.

        Args:
            name: the name of the area.
        Returns:
            the area if it exists, otherwise return None.
        """
        return next((area for area in self.values if area.name == name), None)


class MaimaiClient:
    """The main client of maimai.py."""

    default_caches._caches_provider["songs"] = LXNSProvider()
    default_caches._caches_provider["aliases"] = YuzuProvider()
    default_caches._caches_provider["curves"] = DivingFishProvider()
    default_caches._caches_provider["icons"] = LXNSProvider()
    default_caches._caches_provider["nameplates"] = LXNSProvider()
    default_caches._caches_provider["frames"] = LXNSProvider()
    default_caches._caches_provider["trophies"] = LocalProvider()
    default_caches._caches_provider["charas"] = LocalProvider()
    default_caches._caches_provider["partners"] = LocalProvider()

    _client: AsyncClient
    _cache: BaseCache

    def __init__(self, timeout: float = 20.0, cache: BaseCache | _UnsetSentinel = UNSET, **kwargs) -> None:
        """Initialize the maimai.py client.

        Args:
            timeout: the timeout of the requests, defaults to 20.0.
        """
        self._client = httpx.AsyncClient(timeout=timeout, **kwargs)
        self._cache = SimpleMemoryCache() if isinstance(cache, _UnsetSentinel) else cache

    async def songs(
        self,
        provider: ISongProvider | _UnsetSentinel = UNSET,
        alias_provider: IAliasProvider | None | _UnsetSentinel = UNSET,
        curve_provider: ICurveProvider | None | _UnsetSentinel = UNSET,
    ) -> MaimaiSongs:
        """Fetch all maimai songs from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Available alias providers: `YuzuProvider`, `LXNSProvider`.

        Available curve providers: `DivingFishProvider`.

        Args:
            flush: whether to flush the cache, defaults to False.
            provider: override the data source to fetch the player from, defaults to `LXNSProvider`.
            alias_provider: override the data source to fetch the song aliases from, defaults to `YuzuProvider`.
            curve_provider: override the data source to fetch the song curves from, defaults to `DivingFishProvider`.
        Returns:
            A wrapper of the song list, for easier access and filtering.
        Raises:
            httpx.HTTPError: Request failed due to network issues.
        """
        songs = MaimaiSongs(self._client, self._cache)
        if isinstance(provider, _UnsetSentinel):
            provider = LXNSProvider()
        if isinstance(alias_provider, _UnsetSentinel):
            alias_provider = YuzuProvider()
        if isinstance(curve_provider, _UnsetSentinel):
            curve_provider = DivingFishProvider()
        return await songs.configure(provider, alias_provider, curve_provider)

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
        return await provider.get_player(identifier, self._client)

    async def scores(
        self,
        identifier: PlayerIdentifier,
        kind: ScoreKind = ScoreKind.BEST,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiScores:
        """Fetch player's scores from the provider.

        For WechatProvider, PlayerIdentifier must have the `credentials` attribute, we suggest you to use the `maimai.wechat()` method to get the identifier.
        Also, PlayerIdentifier should not be cached or stored in the database, as the cookies may expire at any time.

        For ArcadeProvider, PlayerIdentifier must have the `credentials` attribute, which is the player's encrypted userId, can be detrived from `maimai.qrcode()`.
        Credentials can be reused, since it won't expire, also, userId is encrypted, can't be used in any other cases outside the maimai.py

        Available providers: `DivingFishProvider`, `LXNSProvider`, `WechatProvider`, `ArcadeProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            kind: the kind of scores list to fetch, defaults to `ScoreKind.BEST`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            The scores object of the player, with all the data fetched.
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            httpx.HTTPError: Request failed due to network issues.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        # MaimaiScores should always cache b35 and b15 scores, in ScoreKind.ALL cases, we can calc the b50 scores from all scores.
        # But there is one exception, LXNSProvider's ALL scores are incomplete, which doesn't contain dx_rating and achievements, leading to sorting difficulties.
        # In this case, we should always fetch the b35 and b15 scores for LXNSProvider.
        # await MaimaiSongs._get_or_fetch(self._client)  # Cache the songs first, as we need to use it for scores' property.
        b35, b15, all, songs = None, None, None, None
        if kind == ScoreKind.BEST or isinstance(provider, LXNSProvider):
            b35, b15 = await provider.get_scores_best(identifier, self._client)
        # For some cases, the provider doesn't support fetching b35 and b15 scores, we should fetch all scores instead.
        if kind == ScoreKind.ALL or (b35 == None and b15 == None):
            # songs = await MaimaiSongs._get_or_fetch(self._client)
            all = await provider.get_scores_all(identifier, self._client)
        return MaimaiScores(b35, b15, all, songs)

    async def regions(self, identifier: PlayerIdentifier, provider: IRegionProvider = ArcadeProvider()) -> list[PlayerRegion]:
        """Get the player's regions that they have played.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(credentials="encrypted_user_id")`.
            provider: the data source to fetch the player from, defaults to `ArcadeProvider`.
        Returns:
            The list of regions that the player has played.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        return await provider.get_regions(identifier, self._client)

    async def updates(
        self,
        identifier: PlayerIdentifier,
        scores: list[Score],
        provider: IScoreProvider = LXNSProvider(),
    ) -> None:
        """Update player's scores to the provider.

        For Diving Fish, the player identifier should be the player's username and password, or import token, e.g.:

        `PlayerIdentifier(username="turou", credentials="password")` or `PlayerIdentifier(credentials="my_diving_fish_import_token")`.

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
        await provider.update_scores(identifier, scores, self._client)

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
        """
        # songs = await MaimaiSongs._get_or_fetch(self._client)
        scores = await provider.get_scores_all(identifier, self._client)
        return MaimaiPlates(scores, plate[0], plate[1:], None)

    async def wechat(self, r=None, t=None, code=None, state=None) -> PlayerIdentifier | str:
        """Get the player identifier from the Wahlap Wechat OffiAccount.

        Call the method with no parameters to get the URL, then redirect the user to the URL with your mitmproxy enabled.

        Your mitmproxy should intercept the response from tgk-wcaime.wahlap.com, then call the method with the parameters from the intercepted response.

        With the parameters from specific user's response, the method will return the user's player identifier.

        Never cache or store the player identifier, as the cookies may expire at any time.

        Args:
            r: the r parameter from the request, defaults to None.
            t: the t parameter from the request, defaults to None.
            code: the code parameter from the request, defaults to None.
            state: the state parameter from the request, defaults to None.
        Returns:
            The player identifier if all parameters are provided, otherwise return the URL to get the identifier.
        Raises:
            WechatTokenExpiredError: Wechat token is expired, please re-authorize.
            httpx.HTTPError: Request failed due to network issues.
        """
        if not all([r, t, code, state]):
            resp = await self._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
            return resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")
        params = {"r": r, "t": t, "code": code, "state": state}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
            "Host": "tgk-wcaime.wahlap.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        resp = await self._client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=params, headers=headers, timeout=5)
        if resp.status_code == 302 and resp.next_request:
            resp_next = await self._client.get(resp.next_request.url, headers=headers)
            return PlayerIdentifier(credentials=resp_next.cookies)
        else:
            raise WechatTokenExpiredError("Wechat token is expired")

    async def qrcode(self, qrcode: str, http_proxy: str | None = None) -> PlayerIdentifier:
        """Get the player identifier from the Wahlap QR code.

        Player identifier is the encrypted userId, can't be used in any other cases outside the maimai.py.

        Args:
            qrcode: the QR code of the player, should begin with SGWCMAID.
            http_proxy: the http proxy to use for the request, defaults to None.
        Returns:
            The player identifier of the player.
        Raises:
            AimeServerError: Maimai Aime server error, may be invalid QR code or QR code has expired.
            TitleServerError: Maimai title server related errors, possibly network problems.
        """
        resp: ArcadeResponse = await arcade.get_uid_encrypted(qrcode, http_proxy=http_proxy)
        ArcadeResponse._raise_for_error(resp)
        if resp.data and isinstance(resp.data, bytes):
            return PlayerIdentifier(credentials=resp.data.decode())
        else:
            raise ArcadeError("Invalid QR code or QR code has expired")

    async def items(self, item: Type[CachedType], flush=False, provider: IItemListProvider | _UnsetSentinel = UNSET) -> MaimaiItems[CachedType]:
        """Fetch maimai player items from the cache default provider.

        Available items: `PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`.

        Args:
            item: the item type to fetch, e.g. `PlayerIcon`.
            flush: whether to flush the cache, defaults to False.
            provider: override the default item list provider, defaults to `LXNSProvider` and `LocalProvider`.
        Returns:
            A wrapper of the item list, for easier access and filtering.
        Raises:
            FileNotFoundError: The item file is not found.
            httpx.HTTPError: Request failed due to network issues.
        """
        if provider and provider is not UNSET:
            default_caches._caches_provider[item._cache_key()] = provider
        items = await default_caches.get_or_fetch(item._cache_key(), self._client, flush=flush)
        return MaimaiItems[CachedType](items)

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

        return MaimaiAreas(lang, await provider.get_areas(lang, self._client))

    async def flush(self) -> None:
        """Flush the caches of the client, this will perform a full re-fetch of all the data.

        Notice that only items ("songs", "aliases", "curves", "icons", "plates", "frames", "trophy", "chara", "partner") will be cached, this will only affect those items.
        """
        await default_caches.flush(self._client)
