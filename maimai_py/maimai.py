import asyncio
from functools import cached_property
from httpx import AsyncClient, AsyncHTTPTransport
from maimai_py import caches, enums
from maimai_py.enums import FCType, FSType, LevelIndex, RateType, ScoreKind
from maimai_py.exceptions import InvalidPlateError
from maimai_py.models import DivingFishPlayer, LXNSPlayer, PlateObject, PlayerIdentifier, Score, Song, SongAlias
from maimai_py.providers import IAliasProvider, IPlayerProvider, ISongProvider, LXNSProvider, YuzuProvider
from maimai_py.providers.base import IScoreProvider


class MaimaiSongs:
    _song_id_dict: dict[int, Song]  # song_id: song
    _alias_entry_dict: dict[str, int]  # alias_entry: song_id

    def __init__(self, songs: list[Song], aliases: list[SongAlias] | None) -> None:
        """@private"""
        self._song_id_dict = {song.id: song for song in songs}
        self._alias_entry_dict = {}
        for alias in aliases:
            target_song = self._song_id_dict.get(alias.song_id)
            if target_song:
                target_song.aliases = alias.aliases
            for alias_entry in alias.aliases:
                self._alias_entry_dict[alias_entry] = alias.song_id

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
        return next((song for song in self.songs if song.title == title), None)

    def by_alias(self, alias: str) -> Song | None:
        """Get song by one possible alias.

        Args:
            alias: one possible alias of the song.
        Returns:
            the song if it exists, otherwise return None.
        """
        song_id = self._alias_entry_dict.get(alias, 0)
        return self.by_id(song_id)

    def by_artist(self, artist: str) -> list[Song]:
        """Get songs by their artist, case-sensitive.

        Args:
            artist: the artist of the songs.
        Returns:
            the list of songs that match the artist, return an empty list if no song is found.
        """
        return [song for song in self.songs if song.artist == artist]

    def by_genre(self, genre: str) -> list[Song]:
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

    def filter(self, **kwargs) -> list[Song]:
        """Filter songs by their attributes.

        Ensure that the attribute is of the song, and the value is of the same type. All conditions are connected by AND.

        Args:
            kwargs: the attributes to filter the songs by.
        Returns:
            the list of songs that match all the conditions, return an empty list if no song is found.
        """
        return [song for song in self.songs if all(getattr(song, key) == value for key, value in kwargs.items())]


class MaimaiPlates:
    scores: list[Score] = []
    """The scores that match the plate version and kind."""
    songs: list[Song] = []
    """The songs that match the plate version and kind."""
    version: str
    """The version of the plate, e.g. "真", "舞"."""
    kind: str
    """The kind of the plate, e.g. "将", "神"."""

    def __init__(self, scores: list[Score], version_str: str, kind: str, songs: MaimaiSongs) -> None:
        """@private"""
        version_str = enums.plate_aliases.get(version_str, version_str)
        kind = enums.plate_aliases.get(kind, kind)
        if version_str == "真":
            versions = [enums.plate_to_version["初"], enums.plate_to_version["真"]]
        if version_str in ["霸", "舞"]:
            versions = [ver for ver in enums.plate_to_version.values() if ver < 20000]
        if enums.plate_to_version.get(version_str):
            versions = [enums.plate_to_version[version_str]]
        if not versions or kind not in ["将", "者", "极", "舞舞", "神"]:
            raise InvalidPlateError(f"Invalid plate: {version_str}{kind}")

        self.version = version_str
        self.kind = kind
        scores_unique = {}

        # There is no plate that requires the player to play both a certain beatmap's DX and SD
        for score in scores:
            song = songs.by_id(score.id)
            score_key = f"{score.id} {score.type} {score.level_index}"
            if song.difficulties.standard != []:
                if any(song.difficulties.standard[0].version % ver <= 100 for ver in versions):
                    scores_unique[score_key] = score.compare(scores_unique.get(score_key, None))
            if song.difficulties.dx != []:
                if any(song.difficulties.dx[0].version % ver <= 100 for ver in versions):
                    scores_unique[score_key] = score.compare(scores_unique.get(score_key, None))
        # There is no plate that requires the player to play both a certain beatmap's DX and SD
        for song in songs.songs:
            if song.difficulties.standard != []:
                if any(song.difficulties.standard[0].version % ver <= 100 for ver in versions):
                    self.songs.append(song)
            if song.difficulties.dx != []:
                if any(song.difficulties.dx[0].version % ver <= 100 for ver in versions):
                    self.songs.append(song)

        self.scores = list(scores_unique.values())

    @cached_property
    def no_remaster(self) -> bool:
        """Whether it is required to play ReMASTER levels in the plate.

        Only 舞 and 霸 plates require ReMASTER levels, others don't.
        """
        return self.version not in ["舞", "霸"]

    @cached_property
    def remained(self) -> list[PlateObject]:
        """Get the remained song of the player on this plate.

        If player has ramained levels on one song, the song and ramained `levels_index` will be included in the result, otherwise it won't.

        The distinct scores which NOT met the plate requirement will be included in the result, the finished scores won't.
        """
        scores: dict[int, list[Score]] = {}
        [scores.setdefault(score.id, []).append(score) for score in self.scores]
        results = {song.id: PlateObject(song=song, levels=song.get_levels(self.no_remaster), score=scores.get(song.id, [])) for song in self.songs}

        def extract(score: Score) -> None:
            if self.no_remaster and score.level_index == LevelIndex.ReMASTER:
                return  # skip ReMASTER scores if the plate is not 舞 or 霸
            results[score.id].score.remove(score)
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
        """Get the cleared song of the player on this plate.

        If player has levels (one or more) that met the requirement on the song, the song and cleared `level_index` will be included in the result, otherwise it won't.

        The distinct scores which met the plate requirement will be included in the result, the unfinished scores won't.
        """
        results = {song.id: PlateObject(song=song, levels=[], score=[]) for song in self.songs}

        def insert(score: Score) -> None:
            if self.no_remaster and score.level_index == LevelIndex.ReMASTER:
                return  # skip ReMASTER scores if the plate is not 舞 or 霸
            results[score.id].score.append(score)
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
        """Get the played song of the player on this plate.

        If player has ever played levels on the song, whether they met or not, the song and played `levels_index` will be included in the result.

        All distinct scores will be included in the result.
        """
        results = {song.id: PlateObject(song=song, levels=[], score=[]) for song in self.songs}
        for score in self.scores:
            if self.no_remaster and score.level_index == LevelIndex.ReMASTER:
                continue  # skip ReMASTER scores if the plate is not 舞 or 霸
            results[score.id].score.append(score)
            results[score.id].levels.append(score.level_index)
        return [plate for plate in results.values() if plate.levels != []]

    @cached_property
    def all(self) -> list[PlateObject]:
        """Get all songs on this plate, usually used for statistics of the plate.

        All songs will be included in the result, with all levels, whether they met or not.

        No scores will be included in the result, use played, cleared, remained to get the scores.
        """
        results = {song.id: PlateObject(song=song, levels=song.get_levels(self.no_remaster), score=[]) for song in self.songs}
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
            scores_unique[score_key] = score.compare(scores_unique.get(score_key, None))
        return list(scores_unique.values())

    def __init__(self, b35: list[Score] = None, b15: list[Score] = None, all: list[Score] = None):
        self.scores = all or b35 + b15
        # if b35 and b15 are not provided, try to calculate them from all scores
        if (not b35 or not b15) and all:
            distinct_scores = MaimaiScores._get_distinct_scores(all)  # scores have to be distinct to calculate the bests
            songs = caches.cached_songs if caches.cached_songs else asyncio.run(MaimaiClient().songs())  # in most cases, the songs are already cached
            scores_new: list[Score] = []
            scores_old: list[Score] = []
            for score in distinct_scores:
                if song := songs.by_id(score.id):
                    (scores_new if song.version >= enums.current_version else scores_old).append(score)
            b35 = (scores_old.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True))[:35]
            b15 = (scores_new.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True))[:15]
        self.scores_b35 = b35
        self.scores_b15 = b15
        self.rating_b35 = sum(score.dx_rating for score in b35)
        self.rating_b15 = sum(score.dx_rating for score in b15)
        self.rating = self.rating_b35 + self.rating_b15

    @cached_property
    def as_distinct(self) -> "MaimaiScores":
        """Get the distinct scores.

        Normally, player has more than one score for the same song and level, this method will return a new `MaimaiScores` object with the highest scores for each song and level.

        This method won't modify the original scores object, it will return a new one.

        If ScoreKind is BEST, this won't make any difference, because the scores are already the best ones.
        """
        distinct_scores = MaimaiScores._get_distinct_scores(self.scores)
        return MaimaiScores(b35=self.scores_b35, b15=self.scores_b15, all=distinct_scores)

    def by_song(self, song_id: int) -> list[Score]:
        """Get all level scores of the song.

        If `ScoreKind` is `BEST`, only the b50 scores will be filtered.

        Args:
            song_id: the ID of the song to get the scores by.
        Returns:
            the list of scores of the song, return an empty list if no score is found.
        """
        return [score for score in self.scores if score.id == song_id]

    def by_level(self, song_id: int, level_index: LevelIndex) -> Score | None:
        """Get score by the song and level index.

        If `ScoreKind` is `BEST`, only the b50 scores will be filtered.

        Args:
            song_id: the ID of the song to get the scores by.
            level_index: the level index of the scores to get.
        Returns:
            the score if it exists, otherwise return None
        """
        return next((score for score in self.scores if score.id == song_id and score.level_index == level_index), None)

    def filter(self, **kwargs) -> list[Score]:
        """Filter scores by their attributes.

        Make sure the attribute is of the score, and the value is of the same type. All conditions are connected by AND.

        If `ScoreKind` is `BEST`, only the b50 scores will be filtered.

        Args:
            kwargs: the attributes to filter the scores by.
        Returns:
            the list of scores that match all the conditions, return an empty list if no score is found.
        """
        return [score for score in self.scores if all(getattr(score, key) == value for key, value in kwargs.items())]


class MaimaiClient:
    """The main client of maimai.py."""

    _client: AsyncClient

    def __init__(self, retries: int = 3, **kwargs) -> None:
        """Initialize the maimai.py client.

        Args:
            retries: the number of retries to attempt on failed requests, defaults to 3.
        """
        self._client = AsyncClient(transport=AsyncHTTPTransport(retries=retries), **kwargs)

    async def songs(
        self,
        provider: ISongProvider = LXNSProvider(),
        alias_provider: IAliasProvider = YuzuProvider(),
    ) -> MaimaiSongs:
        """Fetch all maimai songs from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Available alias providers: `YuzuProvider`, `LXNSProvider`.

        Args:
            provider: the data source to fetch the player from, defaults to `LXNSProvider`.
            alias_provider: the data source to fetch the song aliases from, defaults to `YuzuProvider`.
        Returns:
            A wrapper of the song list, for easier access and filtering.
        """
        aliases = await alias_provider.get_aliases(self) if alias_provider else None
        songs = await provider.get_songs(self)
        caches.cached_songs = MaimaiSongs(songs, aliases)
        return caches.cached_songs

    async def players(
        self,
        identifier: PlayerIdentifier,
        provider: IPlayerProvider = LXNSProvider(),
    ) -> DivingFishPlayer | LXNSPlayer:
        """Fetch player data from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(username="turou")`.
            provider: the data source to fetch the player from, defaults to `LXNSProvider`.
        Returns:
            The player object of the player, with all the data fetched.
        """
        return await provider.get_player(identifier, self)

    async def scores(
        self,
        identifier: PlayerIdentifier,
        kind: ScoreKind = ScoreKind.BEST,
        provider: IScoreProvider = LXNSProvider(),
    ):
        """Fetch player's scores from the provider.

        Available providers: `DivingFishProvider`, `LXNSProvider`.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            kind: the kind of scores list to fetch, defaults to `ScoreKind.BEST`.
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            The scores object of the player, with all the data fetched.
        """
        # MaimaiScores should always cache b35 and b15 scores, in ScoreKind.ALL cases, we can calc the b50 scores from all scores.
        # But there is one exception, LXNSProvider's ALL scores are incomplete, which doesn't contain dx_rating and achievements, leading to sorting difficulties.
        # In this case, we should always fetch the b35 and b15 scores for LXNSProvider.
        b35, b15, all = None, None, None
        if kind == ScoreKind.BEST or isinstance(provider, LXNSProvider):
            b35, b15 = await provider.get_scores_best(identifier, self)
        # For some cases, the provider doesn't support fetching b35 and b15 scores, we should fetch all scores instead.
        if kind == ScoreKind.ALL or (b35 == None and b15 == None):
            all = await provider.get_scores_all(identifier, self)
        return MaimaiScores(b35, b15, all)

    async def plates(
        self,
        identifier: PlayerIdentifier,
        plate: str,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiPlates:
        """Get the plate achievement of the given player and plate.

        Args:
            identifier: the identifier of the player to fetch, e.g. `PlayerIdentifier(friend_code=664994421382429)`.
            plate: the name of the plate, e.g. "樱将", "真舞舞".
            provider: the data source to fetch the player and scores from, defaults to `LXNSProvider`.
        Returns:
            A wrapper of the plate achievement, with plate information, and matched player scores.
        """
        songs = caches.cached_songs if caches.cached_songs else await self.songs()
        scores = await provider.get_scores_all(identifier, self)
        return MaimaiPlates(scores, plate[0], plate[1:], songs)
