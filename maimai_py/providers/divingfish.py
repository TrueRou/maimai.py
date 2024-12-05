from httpx import AsyncClient
from maimai_py import enums
from maimai_py.enums import LevelIndex, SongType
from maimai_py.exceptions import InvalidDeveloperTokenError
from maimai_py.models import DivingFishPlayer, Player, PlayerIdentifier, Score, Song, SongDifficulties, SongDifficulty, SongDifficultyUtage
from maimai_py.providers.base import IPlayerProvider, IScoreProvider, ISongProvider


class DivingFishProvider(ISongProvider, IPlayerProvider, IScoreProvider):
    base_url = "https://www.diving-fish.com/api/maimaidxprober/"

    def headers(self):
        if not self.developer_token:
            raise InvalidDeveloperTokenError()
        return {"developer-token": self.developer_token}

    def __init__(self, developer_token: str | None = None):
        self.developer_token = developer_token

    async def get_songs(self, client: AsyncClient) -> list[Song]:
        resp = await client.get("https://www.diving-fish.com/api/maimaidxprober/music_data")
        resp.raise_for_status()
        resp_json = resp.json()
        songs_unique: dict[int, Song] = {}
        for song in resp_json:
            song_key = int(song["id"]) % 10000
            if song_key not in songs_unique:
                songs_unique[song_key] = Song(
                    id=int(song["id"]) % 10000,
                    title=song["basic_info"]["title"],
                    artist=song["basic_info"]["artist"],
                    genre=song["basic_info"]["genre"],
                    bpm=song["basic_info"]["bpm"],
                    map=None,
                    rights=None,
                    aliases=None,
                    version=enums.divingfish_to_version[song["basic_info"]["from"]],
                    disabled=False,
                    difficulties=SongDifficulties(standard=[], dx=[], utage=[]),
                )
            difficulties = songs_unique[song_key].difficulties
            if song["type"] == "SD":
                difficulties.standard = [
                    SongDifficulty(
                        type=SongType.STANDARD,
                        difficulty=LevelIndex(idx),
                        level=song["level"][idx],
                        level_value=song["ds"][idx],
                        note_designer=chart["charter"],
                        version=enums.divingfish_to_version[song["basic_info"]["from"]],
                        tap_num=chart["notes"][0],
                        hold_num=chart["notes"][1],
                        slide_num=chart["notes"][2],
                        touch_num=chart["notes"][3],
                        break_num=chart["notes"][4] if len(chart["notes"]) > 4 else 0,
                    )
                    for idx, chart in enumerate(song["charts"])
                ]
            elif song["type"] == "DX" and int(song["id"]) < 100000:
                difficulties.dx = [
                    SongDifficulty(
                        type=SongType.DX,
                        difficulty=LevelIndex(idx),
                        level=song["level"][idx],
                        level_value=song["ds"][idx],
                        note_designer=chart["charter"],
                        version=enums.divingfish_to_version[song["basic_info"]["from"]],
                        tap_num=chart["notes"][0],
                        hold_num=chart["notes"][1],
                        slide_num=chart["notes"][2],
                        touch_num=chart["notes"][3],
                        break_num=chart["notes"][4],
                    )
                    for idx, chart in enumerate(song["charts"])
                ]
            elif int(song["id"]) > 100000:
                difficulties.utage = [
                    SongDifficultyUtage(
                        kanji=song["basic_info"]["title"][1:2],
                        description="LET'S PARTY!",
                        is_buddy=False,
                        tap_num=chart["notes"][0],
                        hold_num=chart["notes"][1],
                        slide_num=chart["notes"][2],
                        touch_num=chart["notes"][3],
                        break_num=chart["notes"][4],
                    )
                    for chart in song["charts"]
                ]
        return list(songs_unique.values())

    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        resp = await client.post(self.base_url + "query/player", json=identifier.as_diving_fish())
        resp.raise_for_status()
        resp_json = resp.json()
        return DivingFishPlayer(
            name=resp_json["username"],
            rating=resp_json["rating"],
            nickname=resp_json["nickname"],
            plate=resp_json["plate"],
            additional_rating=resp_json["additional_rating"],
        )

    async def get_scores_best(self, identifier: PlayerIdentifier, ap_only: bool, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        return await super().get_scores_best(identifier, ap_only, client)

    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        return await super().get_scores_all(identifier, client)
