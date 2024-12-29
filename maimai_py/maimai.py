from functools import cached_property
from httpx import AsyncClient
import httpx

from maimai_ffi import arcade
from maimai_py import caches, enums
from maimai_py.enums import FCType, FSType, LevelIndex, RateType, ScoreKind, SongType
from maimai_py.exceptions import InvalidPlateError, WechatTokenExpiredError
from maimai_py.models import ArcadeResponse, DivingFishPlayer, LXNSPlayer, PlateObject, PlayerIdentifier, Score, Song, SongAlias
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
                    scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))
            if song.difficulties.dx != []:
                if any(song.difficulties.dx[0].version % ver <= 100 for ver in versions):
                    scores_unique[score_key] = score._compare(scores_unique.get(score_key, None))
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
        """Get the remained songs and scores of the player on this plate.

        If player has ramained levels on one song, the song and ramained `level_index` will be included in the result, otherwise it won't.

        The distinct scores which NOT met the plate requirement will be included in the result, the finished scores won't.
        """
        scores: dict[int, list[Score]] = {}
        [scores.setdefault(score.id, []).append(score) for score in self.scores]
        results = {
            song.id: PlateObject(song=song, levels=song._get_level_index(self.no_remaster), score=scores.get(song.id, [])) for song in self.songs
        }

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
        """Get the cleared songs and scores of the player on this plate.

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
        """Get the played songs and scores of the player on this plate.

        If player has ever played levels on the song, whether they met or not, the song and played `level_index` will be included in the result.

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
        """Get all songs and scores on this plate, usually used for statistics of the plate.

        All songs will be included in the result, with all levels, whether they met or not.

        No scores will be included in the result, use played, cleared, remained to get the scores.
        """
        results = {song.id: PlateObject(song=song, levels=song._get_level_index(self.no_remaster), score=[]) for song in self.songs}
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

    def __init__(self, b35: list[Score] = None, b15: list[Score] = None, all: list[Score] = None, songs: "MaimaiSongs" = None):
        self.scores = all or b35 + b15
        # if b35 and b15 are not provided, try to calculate them from all scores
        if (not b35 or not b15) and all:
            distinct_scores = MaimaiScores._get_distinct_scores(all)  # scores have to be distinct to calculate the bests
            scores_new: list[Score] = []
            scores_old: list[Score] = []
            for score in distinct_scores:
                if song := songs.by_id(score.id):
                    (scores_new if song.version >= enums.current_version else scores_old).append(score)
            scores_old.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
            scores_new.sort(key=lambda score: (score.dx_rating, score.dx_score, score.achievements), reverse=True)
            b35 = scores_old[:35]
            b15 = scores_new[:15]
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


class MaimaiClient:
    """The main client of maimai.py."""

    _client: AsyncClient

    def __init__(self, timeout: float = 20.0, **kwargs) -> None:
        """Initialize the maimai.py client.

        Args:
            timeout: the timeout of the requests, defaults to 20.0.
        """
        self._args = {"timeout": timeout, **kwargs}

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
        Raises:
            RequestError: Request failed due to network issues.
        """
        async with httpx.AsyncClient(**self._args) as client:
            aliases = await alias_provider.get_aliases(client) if alias_provider else None
            songs = await provider.get_songs(client)
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
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            RequestError: Request failed due to network issues.
        """
        async with httpx.AsyncClient(**self._args) as client:
            return await provider.get_player(identifier, client)

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
            RequestError: Request failed due to network issues.
        Raises:
            TitleServerError: Only for ArcadeProvider, maimai title server related errors, possibly network problems.
            ArcadeError: Only for ArcadeProvider, maimai response is invalid, or user id is invalid.
        """
        # MaimaiScores should always cache b35 and b15 scores, in ScoreKind.ALL cases, we can calc the b50 scores from all scores.
        # But there is one exception, LXNSProvider's ALL scores are incomplete, which doesn't contain dx_rating and achievements, leading to sorting difficulties.
        # In this case, we should always fetch the b35 and b15 scores for LXNSProvider.
        async with httpx.AsyncClient(**self._args) as client:
            b35, b15, all, songs = None, None, None, None
            if kind == ScoreKind.BEST or isinstance(provider, LXNSProvider):
                b35, b15 = await provider.get_scores_best(identifier, client)
            # For some cases, the provider doesn't support fetching b35 and b15 scores, we should fetch all scores instead.
            if kind == ScoreKind.ALL or (b35 == None and b15 == None):
                songs = caches.cached_songs if caches.cached_songs else await self.songs()
                all = await provider.get_scores_all(identifier, client)
            return MaimaiScores(b35, b15, all, songs)

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
            RequestError: Request failed due to network issues.
        """
        async with httpx.AsyncClient(**self._args) as client:
            await provider.update_scores(identifier, scores, client)

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
        Raises:
            InvalidPlayerIdentifierError: Player identifier is invalid for the provider, or player is not found.
            InvalidPlateError: Provided version or plate is invalid.
            InvalidDeveloperTokenError: Developer token is not provided or token is invalid.
            PrivacyLimitationError: The user has not accepted the 3rd party to access the data.
            RequestError: Request failed due to network issues.
        """
        async with httpx.AsyncClient(**self._args) as client:
            songs = caches.cached_songs if caches.cached_songs else await self.songs()
            scores = await provider.get_scores_all(identifier, client)
            return MaimaiPlates(scores, plate[0], plate[1:], songs)

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
            RequestError: Request failed due to network issues.
        """
        async with httpx.AsyncClient() as client:
            if not all([r, t, code, state]):
                resp = await client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/authorize/maimai-dx")
                return resp.headers["location"].replace("redirect_uri=https", "redirect_uri=http")
            params = {"r": r, "t": t, "code": code, "state": state}
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x6307001e)",
                "Host": "tgk-wcaime.wahlap.com",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            }
            resp = await client.get("https://tgk-wcaime.wahlap.com/wc_auth/oauth/callback/maimai-dx", params=params, headers=headers, timeout=5)
            if resp.status_code != 302:
                raise WechatTokenExpiredError("Wechat token is expired")
            resp_next = await client.get(resp.next_request.url, headers=headers)
            return PlayerIdentifier(credentials=resp_next.cookies)

    async def qrcode(self, qrcode: str) -> PlayerIdentifier:
        """Get the player identifier from the Wahlap QR code.

        Player identifier is the encrypted userId, can't be used in any other cases outside the maimai.py.

        Args:
            qrcode: the QR code of the player, should begin with SGWCMAID.
        Returns:
            The player identifier of the player.
        Raises:
            AimeServerError: Maimai Aime server error, may be invalid QR code or QR code has expired.
            TitleServerError: Maimai title server related errors, possibly network problems.
        """
        resp: ArcadeResponse = await arcade.get_uid_encrypted(qrcode)
        ArcadeResponse._throw_error(resp)
        return PlayerIdentifier(credentials=resp.data.decode())
