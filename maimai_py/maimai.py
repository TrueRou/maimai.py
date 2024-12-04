from httpx import AsyncClient, AsyncHTTPTransport
from maimai_py.models import DivingFishPlayer, LXNSPlayer, Song, SongAlias
from maimai_py.providers import DivingFishProvider, IAliasProvider, IPlayerProvider, ISongProvider, LXNSProvider, YuzuProvider


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

        :param id: int, the ID of the song
        :return: Song, the song with the given ID
        """
        return self._song_id_dict.get(id, None)

    def by_title(self, title: str) -> Song | None:
        """
        Get a song by its title, if it exists, otherwise return None

        :param title: str, the title of the song
        :return: Song, the song with the given title
        """
        return next((song for song in self.songs if song.title == title), None)

    def by_alias(self, alias: str) -> Song | None:
        """
        Get song by alias

        :param alias: str, the alias of the songs
        :param maimai_aliases: MaimaiAliases, return value of client.aliases()
        :return: Song, the song with the given alias
        """
        song_id = self._alias_entry_dict.get(alias, 0)
        return self.by_id(song_id)

    def by_artist(self, artist: str) -> list[Song]:
        """
        Get songs by their artist

        :param artist: str, the artist of the songs
        :return: list[Song], the songs with the given artist
        """
        return [song for song in self.songs if song.artist == artist]

    def by_genre(self, genre: str) -> list[Song]:
        """
        Get songs by their genre

        :param genre: str, the genre of the songs
        :return: list[Song], the songs with the given genre
        """
        return [song for song in self.songs if song.genre == genre]

    def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
        """
        Get songs by their BPM

        :param minimum: int, the minimum (inclusive) BPM of the songs
        :param maximum: int, the maximum (inclusive) BPM of the songs
        :return: list[Song], the songs with the given BPM range
        """
        return [song for song in self.songs if minimum <= song.bpm <= maximum]

    def filter(self, **kwargs) -> list[Song]:
        """
        Filter songs by their attributes

        :param kwargs: dict, the attributes to filter the songs by
        :return: list[Song], the songs that match the attributes
        """
        return [song for song in self.songs if all(getattr(song, key) == value for key, value in kwargs.items())]


class MaimaiClient:
    client: AsyncClient

    def __init__(self, retries: int = 3, **kwargs) -> None:
        """
        Initialize the maimai.py client

        :param retries: int, the number of retries to attempt on failed requests, defaults to 3
        """
        self.client = AsyncClient(transport=AsyncHTTPTransport(retries=retries), **kwargs)

    async def songs(self, provider: ISongProvider = LXNSProvider(), alias_provider: IAliasProvider = YuzuProvider()) -> MaimaiSongs:
        """
        Fetch songs from the provider

        :param provider: ISongProvider, the source of the songs, defaults to LXNSProvider
        :return: MaimaiSongs, a wrapper of the songs fetched from the provider
        """
        aliases = await alias_provider.get_aliases(self.client) if alias_provider else None
        songs = await provider.get_songs(self.client)
        maimai_songs = MaimaiSongs(songs, aliases)
        return maimai_songs

    async def players(
        self,
        provider: IPlayerProvider = DivingFishProvider(),
        username: str | None = None,
        friend_code: int | None = None,
        qq: int | None = None,
    ) -> DivingFishPlayer | LXNSPlayer:
        """
        Fetch player data from the provider, using the given one identifier

        :param provider: IPlayerProvider, the source of the player data
        :param username: str, the username of the player
        :param friend_code: int, the friend code of the player
        :param qq: int, the QQ of the player
        """
        if username:
            return await provider.by_username(username, self.client)
        elif friend_code:
            return await provider.by_friend_code(friend_code, self.client)
        elif qq:
            return await provider.by_qq(qq, self.client)
        else:
            raise ValueError("No identifier provided")
