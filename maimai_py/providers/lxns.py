from httpx import AsyncClient
from maimai_py.enums import LevelIndex, SongType
from maimai_py.exceptions import DeveloperTokenNotFoundError
from maimai_py.providers.base import IAliasProvider, IPlayerProvider, IScoreProvider, ISongProvider
from maimai_py.models import (
    LXNSPlayer,
    Player,
    PlayerFrame,
    PlayerIcon,
    PlayerIdentifier,
    PlayerNamePlate,
    PlayerTrophy,
    Song,
    SongAlias,
    SongDifficulties,
    SongDifficulty,
    SongDifficultyUtage,
)


class LXNSProvider(ISongProvider, IPlayerProvider, IScoreProvider, IAliasProvider):
    base_url = "https://maimai.lxns.net/"

    @property
    def headers(self):
        if not self.developer_token:
            raise DeveloperTokenNotFoundError()
        return {"Authorization": self.developer_token}

    def __init__(self, developer_token: str | None = None):
        self.developer_token = developer_token

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

    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        resp = await client.get(self.base_url + f"api/v0/maimai/player/{identifier.as_lxns()}", headers=self.headers)
        resp.raise_for_status()
        resp_json = resp.json()["data"]
        return LXNSPlayer(
            name=resp_json["name"],
            rating=resp_json["rating"],
            friend_code=resp_json["friend_code"],
            trophy=PlayerTrophy(id=resp_json["trophy"]["id"], name=resp_json["trophy"]["name"], color=resp_json["trophy"]["color"]),
            course_rank=resp_json["course_rank"],
            class_rank=resp_json["class_rank"],
            star=resp_json["star"],
            icon=(
                PlayerIcon(id=resp_json["icon"]["id"], name=resp_json["icon"]["name"], genre=resp_json["icon"]["genre"])
                if "icon" in resp_json
                else None
            ),
            name_plate=PlayerNamePlate(id=resp_json["name_plate"]["id"], name=resp_json["name_plate"]["name"]) if "name_plate" in resp_json else None,
            frame=PlayerFrame(id=resp_json["frame"]["id"], name=resp_json["frame"]["name"]) if "frame" in resp_json else None,
            upload_time=resp_json["upload_time"],
        )

    async def get_aliases(self, client: AsyncClient) -> list[SongAlias]:
        resp = await client.get(self.base_url + "api/v0/maimai/alias/list")
        resp.raise_for_status()
        return [SongAlias(song_id=item["song_id"], aliases=item["aliases"]) for item in resp.json()["aliases"]]
