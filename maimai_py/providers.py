from abc import abstractmethod

from httpx import AsyncClient

from maimai_py.enums import LevelIndex, SongType
from maimai_py.models import Song, SongAlias, SongDifficulties, SongDifficulty, SongDifficultyUtage


class ISongProvider:
    @abstractmethod
    async def get_songs(self, client: AsyncClient) -> list[Song]:
        pass


class IAliasProvider:
    @abstractmethod
    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        pass


class LXNSProvider(ISongProvider, IAliasProvider):
    base_url = "https://maimai.lxns.net/"

    async def get_songs(self, client: AsyncClient) -> list[Song]:
        resp = await client.get(self.base_url + "api/v0/maimai/song/list")
        resp.raise_for_status()
        resp_json = resp.json()
        return [
            Song(
                id=song["id"],
                title=song["title"],
                artist=song["artist"],
                genre=song["genre"],
                bpm=song["bpm"],
                aliases=None,
                map=song["map"] if "map" in song else None,
                version=song["version"],
                rights=song["rights"] if "rights" in song else None,
                disabled=song["disabled"] if "disabled" in song else False,
                difficulties=SongDifficulties(
                    standard=[
                        SongDifficulty(
                            type=SongType[difficulty["type"].upper()],
                            difficulty=LevelIndex(difficulty["difficulty"]),
                            level=difficulty["level"],
                            level_value=difficulty["level_value"],
                            note_designer=difficulty["note_designer"],
                            version=difficulty["version"],
                            tap_num=difficulty["notes"]["tap"] if "notes" in difficulty else 0,
                            hold_num=difficulty["notes"]["hold"] if "notes" in difficulty else 0,
                            slide_num=difficulty["notes"]["slide"] if "notes" in difficulty else 0,
                            touch_num=difficulty["notes"]["touch"] if "notes" in difficulty else 0,
                            break_num=difficulty["notes"]["break"] if "notes" in difficulty else 0,
                        )
                        for difficulty in song["difficulties"]["standard"]
                    ],
                    dx=[
                        SongDifficulty(
                            type=SongType[difficulty["type"].upper()],
                            difficulty=LevelIndex(difficulty["difficulty"]),
                            level=difficulty["level"],
                            level_value=difficulty["level_value"],
                            note_designer=difficulty["note_designer"],
                            version=difficulty["version"],
                            tap_num=difficulty["notes"]["tap"] if "notes" in difficulty else 0,
                            hold_num=difficulty["notes"]["hold"] if "notes" in difficulty else 0,
                            slide_num=difficulty["notes"]["slide"] if "notes" in difficulty else 0,
                            touch_num=difficulty["notes"]["touch"] if "notes" in difficulty else 0,
                            break_num=difficulty["notes"]["break"] if "notes" in difficulty else 0,
                        )
                        for difficulty in song["difficulties"]["dx"]
                    ],
                    utage=(
                        [
                            SongDifficultyUtage(
                                kanji=difficulty["kanji"],
                                description=difficulty["description"],
                                is_buddy=difficulty["is_buddy"],
                                tap_num=difficulty["notes"]["tap"] if "notes" in difficulty and "tap" in difficulty["notes"] else 0,
                                hold_num=difficulty["notes"]["hold"] if "notes" in difficulty and "hold" in difficulty["notes"] else 0,
                                slide_num=difficulty["notes"]["slide"] if "notes" in difficulty and "slide" in difficulty["notes"] else 0,
                                touch_num=difficulty["notes"]["touch"] if "notes" in difficulty and "touch" in difficulty["notes"] else 0,
                                break_num=difficulty["notes"]["break"] if "notes" in difficulty and "break" in difficulty["notes"] else 0,
                                left_num=difficulty["notes"]["left"] if "notes" in difficulty and "left" in difficulty["notes"] else 0,
                                right_num=difficulty["notes"]["right"] if "notes" in difficulty and "right" in difficulty["notes"] else 0,
                            )
                            for difficulty in song["difficulties"]["utage"]
                        ]
                        if "utage" in song["difficulties"]
                        else []
                    ),
                ),
            )
            for song in resp_json["songs"]
        ]

    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        resp = await client.get(self.base_url + "api/v0/maimai/alias/list")
        resp.raise_for_status()
        return [SongAlias(song_id=item["song_id"], aliases=item["aliases"]) for item in resp.json()["aliases"]]


class YuzuProvider(IAliasProvider):
    base_url = "https://api.yuzuchan.moe/"

    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        resp = await client.get(self.base_url + "maimaidx/maimaidxalias")
        resp.raise_for_status()
        return [SongAlias(song_id=item["SongID"] % 10000, aliases=item["Alias"]) for item in resp.json()["content"]]
