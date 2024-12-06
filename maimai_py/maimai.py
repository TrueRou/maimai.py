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
        self._song_id_dict = {song.id: song for song in songs}
        self._alias_entry_dict = {}
        for alias in aliases:
            target_song = self._song_id_dict.get(alias.song_id)
            if target_song:
                target_song.aliases = alias.aliases
            for alias_entry in alias.aliases:
                self._alias_entry_dict[alias_entry] = alias.song_id

    @property
    def songs(self):
        return self._song_id_dict.values()

    def by_id(self, id: int) -> Song | None:
        """
        Get a song by its ID, if it exists, otherwise return None

        Parameters
        ----------
        id: int
            the ID of the song, always smaller than 10000, should (% 10000) if necessary
        """
        return self._song_id_dict.get(id, None)

    def by_title(self, title: str) -> Song | None:
        """
        Get a song by its title, if it exists, otherwise return None

        Parameters
        ----------
        title: str
            the title of the song
        """
        return next((song for song in self.songs if song.title == title), None)

    def by_alias(self, alias: str) -> Song | None:
        """
        Get song by one possible alias, if it exists, otherwise return None

        Parameters
        ----------
        alias: str
            one possible alias of the song
        """
        song_id = self._alias_entry_dict.get(alias, 0)
        return self.by_id(song_id)

    def by_artist(self, artist: str) -> list[Song]:
        """
        Get songs by their artist, case-sensitive, return an empty list if no song is found

        Parameters
        ----------
        artist: str
            the artist of the songs
        """
        return [song for song in self.songs if song.artist == artist]

    def by_genre(self, genre: str) -> list[Song]:
        """
        Get songs by their genre, case-sensitive, return an empty list if no song is found

        Parameters
        ----------
        genre: str
            the genre of the songs
        """
        return [song for song in self.songs if song.genre == genre]

    def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
        """
        Get songs by their BPM, return an empty list if no song is found

        Parameters
        ----------
        minimum: int
            the minimum (inclusive) BPM of the songs
        maximum: int
            the maximum (inclusive) BPM of the songs
        """
        return [song for song in self.songs if minimum <= song.bpm <= maximum]

    def filter(self, **kwargs) -> list[Song]:
        """
        Filter songs by their attributes, all conditions are connected by AND, return an empty list if no song is found

        Parameters
        ----------
        kwargs: dict
            the attributes to filter the songs by=
        """
        return [song for song in self.songs if all(getattr(song, key) == value for key, value in kwargs.items())]


class MaimaiPlates:
    scores: list[Score] = []  # scores that match the plate version
    songs: list[Song] = []  # songs that match the plate version
    version: str
    kind: str

    def __init__(self, scores: list[Score], version_str: str, kind: str, songs: MaimaiSongs) -> None:
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
        return self.version not in ["舞", "霸"]

    @cached_property
    def remained(self) -> list[PlateObject]:
        scores: dict[int, list[Score]] = {}
        [scores.setdefault(score.id, []).append(score) for score in self.scores]
        results = {song.id: PlateObject(song=song, levels=song.levels(self.no_remaster), score=scores.get(song.id, [])) for song in self.songs}

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
        results = {song.id: PlateObject(song=song, levels=[], score=[]) for song in self.songs}
        for score in self.scores:
            if self.no_remaster and score.level_index == LevelIndex.ReMASTER:
                continue  # skip ReMASTER scores if the plate is not 舞 or 霸
            results[score.id].score.append(score)
            results[score.id].levels.append(score.level_index)
        return [plate for plate in results.values() if plate.levels != []]

    @cached_property
    def total(self) -> list[PlateObject]:
        results = {song.id: PlateObject(song=song, levels=song.levels(self.no_remaster), score=[]) for song in self.songs}
        return results.values()

    @cached_property
    def played_num(self) -> int:
        return len([level for plate in self.played for level in plate.levels])

    @cached_property
    def cleared_num(self) -> int:
        return len([level for plate in self.cleared for level in plate.levels])

    @cached_property
    def remained_num(self) -> int:
        return len([level for plate in self.remained for level in plate.levels])

    @cached_property
    def total_num(self) -> int:
        return len([level for plate in self.total for level in plate.levels])


class MaimaiScores:
    scores: list[Score]
    scores_b35: list[Score]
    scores_b15: list[Score]
    rating: int
    rating_b35: int
    rating_b15: int

    def __init__(self, scores_b35: list[Score], scores_b15: list[Score]) -> None:
        self.scores = scores_b35 + scores_b15
        self.scores_b35 = scores_b35
        self.scores_b15 = scores_b15
        self.rating_b35 = sum(score.dx_rating for score in scores_b35)
        self.rating_b15 = sum(score.dx_rating for score in scores_b15)
        self.rating = self.rating_b35 + self.rating_b15

    @cached_property
    def as_distinct(self) -> "MaimaiScores":
        """
        Get the distinct scores, return a new MaimaiScores object

        Normally, player has more than one score for the same song and level, this method will return a new MaimaiScores object with the highest scores for each song and level.

        If ScoreKind is BEST, this won't make any difference, because the scores are already the best ones.
        """
        new_scores = MaimaiScores(self.scores_b35, self.scores_b15)
        scores_unique = {}
        for score in self.scores:
            score_key = f"{score.id} {score.type} {score.level_index}"
            scores_unique[score_key] = score.compare(scores_unique.get(score_key, None))
        new_scores.scores = list(scores_unique.values())
        return new_scores

    def by_song(self, song_id: int) -> list[Score]:
        """
        Get all level scores of the song, return an empty list if no score is found

        If ScoreKind is BEST, only the b50 scores will be filtered.

        Parameters
        ----------
        song_id: int
            the ID of the song to get the scores by
        """
        return [score for score in self.scores if score.id == song_id]

    def by_level(self, song_id: int, level_index: LevelIndex) -> Score | None:
        """
        Get score by the song and level index, return None if no score is found

        If ScoreKind is BEST, only the b50 scores will be filtered.

        Parameters
        ----------
        song_id: int
            the ID of the song to get the scores by
        level_index: LevelIndex
            the level index of the scores to get
        """
        return next((score for score in self.scores if score.id == song_id and score.level_index == level_index), None)

    def filter(self, **kwargs) -> list[Score]:
        """
        Filter scores by their attributes, all conditions are connected by AND, return an empty list if no score is found

        If ScoreKind is BEST, only the b50 scores will be filtered.

        Parameters
        ----------
        kwargs: dict
            the attributes to filter the scores by
        """
        return [score for score in self.scores if all(getattr(score, key) == value for key, value in kwargs.items())]


class MaimaiClient:
    client: AsyncClient

    def __init__(self, retries: int = 3, **kwargs) -> None:
        """
        Initialize the maimai.py client

        Parameters
        ----------

        retries: int
            the number of retries to attempt on failed requests, defaults to 3
        lxns_developer_token: str
            the developer token for LXNSProvider, this will be used to construct the default LXNSProvider
        divingfish_developer_token: str
            the developer token for DivingFishProvider, this will be used to construct the default DivingFishProvider
        """
        self.client = AsyncClient(transport=AsyncHTTPTransport(retries=retries), **kwargs)

    async def songs(
        self,
        provider: ISongProvider = LXNSProvider(),
        alias_provider: IAliasProvider = YuzuProvider(),
    ) -> MaimaiSongs:
        """
        Fetch all maimai songs from the provider, returning a wrapper of the song list, for easier access and filtering

        Parameters
        ----------
        provider: ISongProvider (DivingFishProvider | LXNSProvider)
            the data source to fetch the player from, defaults to LXNSProvider

        alias_provider: IAliasProvider (YuzuProvider | LXNSProvider)
            the data source to fetch the song aliases from, defaults to YuzuProvider
        """
        aliases = await alias_provider.get_aliases(self.client) if alias_provider else None
        songs = await provider.get_songs(self.client)
        caches.cached_songs = MaimaiSongs(songs, aliases)
        return caches.cached_songs

    async def players(
        self,
        identifier: PlayerIdentifier,
        provider: IPlayerProvider = LXNSProvider(),
    ) -> DivingFishPlayer | LXNSPlayer:
        """
        Fetch player data from the provider, using the given one identifier

        Parameters
        ----------

        identifier: PlayerIdentifier
            the identifier of the player to fetch, e.g. PlayerIdentifier(username="turou")
        provider: IPlayerProvider (DivingFishProvider | LXNSProvider)
            the data source to fetch the player from, defaults to LXNSProvider
        """
        return await provider.get_player(identifier, self.client)

    async def scores(
        self,
        identifier: PlayerIdentifier,
        kind: ScoreKind = ScoreKind.BEST,
        provider: IScoreProvider = LXNSProvider(),
    ):
        """
        Fetch player's scores from the provider, using the given one identifier

        Parameters
        ----------

        identifier: PlayerIdentifier
            the identifier of the player to fetch, e.g. PlayerIdentifier(friend_code=664994421382429)
        kind: ScoreKind
            the kind of scores list to fetch, defaults to ScoreKind.BEST
        provider: IScoreProvider (LXNSProvider | DivingFishProvider)
            the data source to fetch the player and scores from, defaults to LXNSProvider
        """
        b35, b15 = await provider.get_scores_best(identifier, self.client)
        maimai_scores = MaimaiScores(b35, b15)
        if kind == ScoreKind.ALL:
            # fetch all scores if needed, this is a separate request, because of b35 and b15 is always fetched
            maimai_scores.scores = await provider.get_scores_all(identifier, self.client)
        return maimai_scores

    async def plates(
        self,
        identifier: PlayerIdentifier,
        plate: str,
        provider: IScoreProvider = LXNSProvider(),
    ) -> MaimaiPlates:
        """
        Get the plate achievement of the given player and plate.

        Parameters
        ----------
        identifier: PlayerIdentifier
            the identifier of the player to fetch, e.g. PlayerIdentifier(friend_code=664994421382429)
        plate: str
            the name of the plate, e.g. "舞将", "舞舞将"
        provider: IScoreProvider (LXNSProvider | DivingFishProvider)
            the data source to fetch the player and scores from, defaults to LXNSProvider
        """
        songs = caches.cached_songs if caches.cached_songs else await self.songs()
        scores = await provider.get_scores_all(identifier, self.client)
        return MaimaiPlates(scores, plate[0], plate[1:], songs)
