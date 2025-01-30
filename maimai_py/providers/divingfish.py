import dataclasses
from typing import Generator
from httpx import AsyncClient, Response

from maimai_py.enums import *
from maimai_py.models import *
from maimai_py.providers import ICurveProvider, IPlayerProvider, IScoreProvider, ISongProvider
from maimai_py.exceptions import InvalidDeveloperTokenError, InvalidPlayerIdentifierError, PrivacyLimitationError


class DivingFishProvider(ISongProvider, IPlayerProvider, IScoreProvider, ICurveProvider):
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

    def __eq__(self, value):
        return isinstance(value, DivingFishProvider) and value.developer_token == self.developer_token

    def _deser_song(song: dict) -> Song:
        return Song(
            id=int(song["id"]) % 10000,
            title=song["basic_info"]["title"] if int(song["id"]) != 383 else "Link",
            artist=song["basic_info"]["artist"],
            genre=song["basic_info"]["genre"],
            bpm=song["basic_info"]["bpm"],
            map=None,
            rights=None,
            aliases=None,
            version=divingfish_to_version[song["basic_info"]["from"]].value,
            disabled=False,
            difficulties=SongDifficulties(standard=[], dx=[], utage=[]),
        )

    def _deser_diffs(song: dict) -> Generator[SongDifficulty, None, None]:
        song_type = SongType._from_id(song["id"])
        for idx, chart in enumerate(song["charts"]):
            song_diff = SongDifficulty(
                type=song_type,
                level=song["level"][idx],
                level_value=song["ds"][idx],
                level_index=LevelIndex(idx),
                note_designer=chart["charter"],
                version=divingfish_to_version[song["basic_info"]["from"]].value,
                tap_num=chart["notes"][0],
                hold_num=chart["notes"][1],
                slide_num=chart["notes"][2],
                touch_num=chart["notes"][3],
                break_num=chart["notes"][4] if len(chart["notes"]) > 4 else 0,
                curve=None,
            )
            if song_type == SongType.UTAGE:
                song_diff = SongDifficultyUtage(
                    **dataclasses.asdict(song_diff),
                    kanji=song["basic_info"]["title"][1:2],
                    description="LET'S PARTY!",
                    is_buddy=False,
                )
            yield song_diff

    def _deser_score(score: dict) -> Score:
        return Score(
            id=score["song_id"] % 10000,
            song_name=score["title"] if score["song_id"] != 383 else "Link(CoF)",
            level=score["level"],
            level_index=LevelIndex(score["level_index"]),
            achievements=score["achievements"],
            fc=FCType[score["fc"].upper()] if score["fc"] else None,
            fs=FSType[score["fs"].upper()] if score["fs"] else None,
            dx_score=score["dxScore"],
            dx_rating=score["ra"],
            rate=RateType[score["rate"].upper()],
            type=SongType._from_id(score["song_id"]),
        )

    def _ser_score(score: Score) -> dict:
        return {
            "song_id": score.type._to_id(score.id),
            "title": score.song_name if score.id != 383 else "Link(CoF)",
            "level": score.level,
            "level_index": score.level_index.value,
            "achievements": score.achievements,
            "fc": score.fc.name.lower() if score.fc else None,
            "fs": score.fs.name.lower() if score.fs else None,
            "dxScore": score.dx_score,
            "ra": score.dx_rating,
            "rate": score.rate.name.lower(),
            "type": score.type._to_abbr(),
        }

    def _deser_curve(chart: dict) -> CurveObject:
        return CurveObject(
            sample_size=int(chart["cnt"]),
            fit_level_value=chart["fit_diff"],
            avg_achievements=chart["avg"],
            stdev_achievements=chart["std_dev"],
            avg_dx_score=chart["avg_dx"],
            rate_sample_size={v: chart["dist"][13 - i] for i, v in enumerate(RateType)},
            fc_sample_size={v: chart["dist"][4 - i] for i, v in enumerate(FCType)},
        )

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

    async def get_songs(self, client: AsyncClient) -> list[Song]:
        resp = await client.get(self.base_url + "music_data")
        resp.raise_for_status()
        resp_json = resp.json()
        unique_songs: dict[int, Song] = {}
        for song in resp_json:
            unique_key = int(song["id"]) % 10000
            song_type: SongType = SongType._from_id(song["id"])
            if unique_key not in unique_songs:
                unique_songs[unique_key] = DivingFishProvider._deser_song(song)
            difficulties: list[SongDifficulty] = unique_songs[unique_key].difficulties.__getattribute__(song_type.value)
            difficulties.extend(DivingFishProvider._deser_diffs(song))
        return list(unique_songs.values())

    async def get_player(self, identifier: PlayerIdentifier, client: AsyncClient) -> Player:
        resp = await client.post(self.base_url + "query/player", json=identifier._as_diving_fish())
        self._check_response_player(resp)
        resp_json = resp.json()
        return DivingFishPlayer(
            name=resp_json["username"],
            rating=resp_json["rating"],
            nickname=resp_json["nickname"],
            plate=resp_json["plate"],
            additional_rating=resp_json["additional_rating"],
        )

    async def get_scores_best(self, identifier: PlayerIdentifier, client: AsyncClient) -> tuple[list[Score], list[Score]]:
        req_json = identifier._as_diving_fish()
        req_json["b50"] = True
        resp = await client.post(self.base_url + "query/player", json=req_json)
        self._check_response_player(resp)
        resp_json = resp.json()
        return (
            [DivingFishProvider._deser_score(score) for score in resp_json["charts"]["sd"]],
            [DivingFishProvider._deser_score(score) for score in resp_json["charts"]["dx"]],
        )

    async def get_scores_all(self, identifier: PlayerIdentifier, client: AsyncClient) -> list[Score]:
        resp = await client.get(self.base_url + "dev/player/records", params=identifier._as_diving_fish(), headers=self.headers)
        self._check_response_player(resp)
        resp_json = resp.json()
        return [s for score in resp_json["records"] if (s := DivingFishProvider._deser_score(score))]

    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: AsyncClient) -> None:
        headers, cookies = None, None
        if identifier.username and identifier.credentials:
            login_json = {"username": identifier.username, "password": identifier.credentials}
            resp1 = await client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=login_json)
            self._check_response_player(resp1)
            cookies = resp1.cookies
        elif not identifier.username and identifier.credentials:
            headers = {"Import-Token": identifier.credentials}
        else:
            raise InvalidPlayerIdentifierError("Either username and password or import token is required to deliver scores")
        scores_json = [DivingFishProvider._ser_score(score) for score in scores]
        resp2 = await client.post(self.base_url + "player/update_records", cookies=cookies, headers=headers, json=scores_json)
        self._check_response_player(resp2)

    async def get_curves(self, client: AsyncClient) -> dict[str, list[CurveObject | None]]:
        resp = await client.get(self.base_url + "chart_stats")
        resp.raise_for_status()
        return {idx: ([DivingFishProvider._deser_curve(chart) for chart in charts if chart != {}]) for idx, charts in (resp.json())["charts"].items()}
