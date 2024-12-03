from httpx import AsyncClient, AsyncHTTPTransport
from maimai_py.models import Song
from maimai_py.providers import ISongProvider, LXNSProvider


class MaimaiSongs:
    songs: list[Song]

    def __init__(self, songs: list[Song]) -> None:
        self.songs = songs

    def by_id(self, id: int) -> Song | None:
        """
        Get a song by its ID, if it exists, otherwise return None

        :param id: int, the ID of the song
        :return: Song, the song with the given ID
        """
        return next((song for song in self.songs if song.id == id), None)

    def by_title(self, title: str) -> Song | None:
        """
        Get a song by its title, if it exists, otherwise return None

        :param title: str, the title of the song
        :return: Song, the song with the given title
        """
        return next((song for song in self.songs if song.title == title), None)

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

    async def songs(self, provider: ISongProvider = LXNSProvider()) -> MaimaiSongs:
        """
        Fetch songs from the provider

        :param provider: ISongProvider, the source of the songs, defaults to LXNSProvider
        :return: MaimaiSongs, a wrapper of the songs fetched from the provider
        """
        return MaimaiSongs(await provider.get_songs(self.client))
