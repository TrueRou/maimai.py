from typing import TYPE_CHECKING

from httpx import Response
from maimai_py import enums
from maimai_py.enums import FCType, FSType, LevelIndex, RateType, SongType
from maimai_py.exceptions import InvalidDeveloperTokenError, InvalidPlayerIdentifierError, PrivacyLimitationError
from maimai_py.models import DivingFishPlayer, Player, PlayerIdentifier, Score, Song, SongDifficulties, SongDifficulty, SongDifficultyUtage
from maimai_py.providers.base import IPlayerProvider, IScoreProvider, ISongProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient


class DivingFishProvider(ISongProvider, IPlayerProvider, IScoreProvider):
    """The provider that fetches data from the Diving Fish.

    DivingFish: https://www.diving-fish.com/maimaidx/prober/
    """

    developer_token: str | None
    """The developer token used to access the Diving Fish API."""
    base_url = "https://www.diving-fish.com/api/maimaidxprober/"
    """The base URL for the Diving Fish API."""

    @property
    def headers(self):
        """@private"""
        if not self.developer_token:
            raise InvalidDeveloperTokenError()
        return {"developer-token": self.developer_token}

    def __init__(self, developer_token: str | None = None):
        """Initializes the DivingFishProvider.

        Args:
            developer_token: The developer token used to access the Diving Fish API.
        """
        self.developer_token = developer_token

    def _deser_score(score: dict) -> Score:
        song_type = (
            SongType.STANDARD if score["type"] == "SD" else SongType.DX if score["type"] == "DX" and score["song_id"] < 100000 else SongType.UTAGE
        )
        return Score(
            id=score["song_id"] % 10000,
            song_name=score["title"],
            level=score["level"],
            level_index=LevelIndex(score["level_index"]),
            achievements=score["achievements"],
            fc=FCType[score["fc"].upper()] if score["fc"] else None,
            fs=FSType[score["fs"].upper()] if score["fs"] else None,
            dx_score=score["dxScore"],
            dx_rating=score["ra"],
            rate=RateType[score["rate"].upper()],
            type=song_type,
        )

    def _ser_score(score: Score) -> dict:
        diving_id = score.id if score.type == SongType.STANDARD else score.id + 10000 if score.type == SongType.DX else score.id + 100000
        diving_type = "SD" if score.type == SongType.STANDARD else "DX" if score.type == SongType.DX else "UTAGE"
        return {
            "song_id": diving_id,
            "title": score.song_name,
            "level": score.level,
            "level_index": score.level_index.value,
            "achievements": score.achievements,
            "fc": score.fc.name.lower() if score.fc else None,
            "fs": score.fs.name.lower() if score.fs else None,
            "dxScore": score.dx_score,
            "ra": score.dx_rating,
            "rate": score.rate.name.lower(),
            "type": diving_type,
        }

    def _check_response_player(self, resp: Response) -> None:
        resp_json = resp.json()
        if "msg" in resp_json and resp_json["msg"] in ["请先联系水鱼申请开发者token", "开发者token有误", "开发者token被禁用"]:
            raise InvalidDeveloperTokenError(resp_json["msg"])
        elif "message" in resp_json and resp_json["message"] in ["导入token有误", "尚未登录", "会话过期"]:
            raise InvalidPlayerIdentifierError(resp_json["message"])
        elif resp.status_code in [400, 401]:
            raise InvalidPlayerIdentifierError(resp_json["message"])
        elif resp.status_code == 403:
            raise PrivacyLimitationError(resp_json["message"])

    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        resp = await client._client.get("https://www.diving-fish.com/api/maimaidxprober/music_data")
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

    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> Player:
        resp = await client._client.post(self.base_url + "query/player", json=identifier.as_diving_fish())
        self._check_response_player(resp)
        resp_json = resp.json()
        return DivingFishPlayer(
            name=resp_json["username"],
            rating=resp_json["rating"],
            nickname=resp_json["nickname"],
            plate=resp_json["plate"],
            additional_rating=resp_json["additional_rating"],
        )

    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> tuple[list[Score], list[Score]]:
        req_json = identifier.as_diving_fish()
        req_json["b50"] = True
        resp = await client._client.post(self.base_url + "query/player", json=req_json)
        self._check_response_player(resp)
        resp_json = resp.json()
        return (
            [DivingFishProvider._deser_score(score) for score in resp_json["charts"]["sd"]],
            [DivingFishProvider._deser_score(score) for score in resp_json["charts"]["dx"]],
        )

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        resp = await client._client.get(self.base_url + "dev/player/records", params=identifier.as_diving_fish(), headers=self.headers)
        self._check_response_player(resp)
        resp_json = resp.json()
        return [DivingFishProvider._deser_score(score) for score in resp_json["records"]]

    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: "MaimaiClient") -> None:
        headers, cookies = None
        if identifier.username and identifier.credentials:
            login_json = {"username": identifier.username, "password": identifier.credentials}
            resp1 = await client._client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=login_json)
            self._check_response_player(resp1)
            cookies = resp1.cookies
        elif not identifier.username and identifier.credentials:
            headers = {"Import-Token": identifier.credentials}
        else:
            raise InvalidPlayerIdentifierError("Either username and password or import token is required to deliver scores")
        scores_json = [DivingFishProvider._ser_score(score) for score in scores]
        resp2 = await client._client.post(self.base_url + "player/update_records", cookies=cookies, headers=headers, json=scores_json)
        self._check_response_player(resp2)
