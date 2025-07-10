import asyncio
import dataclasses
import hashlib
from functools import reduce
from json import JSONDecodeError
from operator import concat
from typing import TYPE_CHECKING, Iterable

from httpx import HTTPStatusError, Response

from maimai_py.models import *
from maimai_py.models import PlayerIdentifier, Score, Song

from .base import IAliasProvider, IItemListProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ISongProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class LXNSProvider(ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, IAliasProvider, IItemListProvider):
    """The provider that fetches data from the LXNS.

    LXNS: https://maimai.lxns.net/
    """

    developer_token: Optional[str]
    """The developer token used to access the LXNS API."""
    base_url = "https://maimai.lxns.net/"
    """The base URL for the LXNS API."""

    @property
    def headers(self):
        """@private"""
        if not self.developer_token:
            raise InvalidDeveloperTokenError("Developer token is not provided.")
        return {"Authorization": self.developer_token}

    def __init__(self, developer_token: Optional[str] = None):
        """Initializes the LXNSProvider.

        Args:
            developer_token: The developer token used to access the LXNS API.
        """
        self.developer_token = developer_token

    def _hash(self) -> str:
        return hashlib.md5(b"lxns").hexdigest()

    async def _ensure_friend_code(self, client: "MaimaiClient", identifier: PlayerIdentifier) -> None:
        if identifier.friend_code is None:
            if identifier.qq is not None:
                resp = await client._client.get(self.base_url + f"api/v0/maimai/player/qq/{identifier.qq}", headers=self.headers)
                if not resp.json()["success"]:
                    raise InvalidPlayerIdentifierError(resp.json()["message"])
                identifier.friend_code = resp.json()["data"]["friend_code"]

    async def _build_player_request(self, path: str, identifier: PlayerIdentifier, client: "MaimaiClient") -> tuple[str, dict[str, str], bool]:
        use_user_api = identifier.credentials is not None and isinstance(identifier.credentials, str)
        if use_user_api:
            # user-level API takes the precedence: If personal token provided, use it first
            assert isinstance(identifier.credentials, str)
            entrypoint = f"api/v0/user/maimai/player/{path}"
            headers = {"X-User-Token": identifier.credentials}
        else:
            await self._ensure_friend_code(client, identifier)
            entrypoint = f"api/v0/maimai/player/{identifier.friend_code}/{path}"
            headers = self.headers
        entrypoint = entrypoint.removesuffix("/")
        return self.base_url + entrypoint, headers, use_user_api

    @staticmethod
    def _deser_note(diff: dict, key: str) -> int:
        if "notes" in diff:
            if "is_buddy" in diff and diff["is_buddy"]:
                return diff["notes"]["left"][key] + diff["notes"]["right"][key]
            return diff["notes"][key]
        return 0

    @staticmethod
    def _deser_item(item: dict, cls: type) -> Any:
        return cls(
            id=item["id"],
            name=item["name"],
            description=item["description"] if "description" in item else None,
            genre=item["genre"] if "genre" in item else None,
        )

    @staticmethod
    def _deser_song(song: dict) -> Song:
        return Song(
            id=song["id"],
            title=song["title"],
            artist=song["artist"],
            genre=name_to_genre[song["genre"]],
            bpm=song["bpm"],
            aliases=song["aliases"] if "aliases" in song else None,
            map=song["map"] if "map" in song else None,
            version=song["version"],
            rights=song["rights"] if "rights" in song else None,
            disabled=song["disabled"] if "disabled" in song else False,
            difficulties=SongDifficulties(standard=[], dx=[], utage=[]),
        )

    @staticmethod
    def _deser_diff(difficulty: dict) -> SongDifficulty:
        return SongDifficulty(
            type=SongType[difficulty["type"].upper()],
            level=difficulty["level"],
            level_value=difficulty["level_value"],
            level_index=LevelIndex(difficulty["difficulty"]),
            note_designer=difficulty["note_designer"],
            version=difficulty["version"],
            tap_num=LXNSProvider._deser_note(difficulty, "tap"),
            hold_num=LXNSProvider._deser_note(difficulty, "hold"),
            slide_num=LXNSProvider._deser_note(difficulty, "slide"),
            touch_num=LXNSProvider._deser_note(difficulty, "touch"),
            break_num=LXNSProvider._deser_note(difficulty, "break"),
            curve=None,
        )

    @staticmethod
    def _deser_diff_utage(difficulty: dict) -> SongDifficultyUtage:
        return SongDifficultyUtage(
            **dataclasses.asdict(LXNSProvider._deser_diff(difficulty)),
            kanji=difficulty["kanji"],
            description=difficulty["description"],
            is_buddy=difficulty["is_buddy"],
        )

    @staticmethod
    def _deser_score(score: dict) -> Score:
        return Score(
            id=score["id"],
            level=score["level"],
            level_index=LevelIndex(score["level_index"]),
            achievements=score["achievements"] if "achievements" in score else None,
            fc=FCType[score["fc"].upper()] if score["fc"] else None,
            fs=FSType[score["fs"].upper()] if score["fs"] else None,
            dx_score=score["dx_score"] if "dx_score" in score else None,
            dx_rating=int(score["dx_rating"]) if "dx_rating" in score else None,
            play_count=None,
            rate=RateType[score["rate"].upper()],
            type=SongType[score["type"].upper()],
        )

    @staticmethod
    async def _ser_score(score: Score, songs: "MaimaiSongs") -> Optional[dict]:
        song_title = song.title if (song := await songs.by_id(score.id)) else None
        if song_title is not None:
            return {
                "id": score.id,
                "song_name": song_title,
                "level": score.level,
                "level_index": score.level_index.value,
                "achievements": score.achievements,
                "fc": score.fc.name.lower() if score.fc else None,
                "fs": score.fs.name.lower() if score.fs else None,
                "dx_score": score.dx_score,
                "dx_rating": score.dx_rating,
                "rate": score.rate.name.lower(),
                "type": score.type.name.lower(),
            }

    def _check_response_player(self, resp: Response) -> dict:
        try:
            resp_json = resp.json()
            if not resp_json["success"]:
                if resp_json["code"] in [400, 404]:
                    raise InvalidPlayerIdentifierError(resp_json["message"])
                elif resp_json["code"] in [403]:
                    raise PrivacyLimitationError(resp_json["message"])
                elif resp_json["code"] in [401]:
                    raise InvalidDeveloperTokenError(resp_json["message"])
                elif resp.status_code in [400, 401]:
                    raise InvalidPlayerIdentifierError(resp_json["message"])
                elif not resp.is_success:
                    resp.raise_for_status()
            return resp_json
        except JSONDecodeError as exc:
            raise InvalidJsonError(resp.text) from exc
        except HTTPStatusError as exc:
            raise MaimaiPyError(exc) from exc

    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/song/list?notes=true")
        resp.raise_for_status()
        resp_json = resp.json()
        unique_songs: dict[int, Song] = {}
        for song in resp_json["songs"]:
            unique_key = int(song["id"]) % 10000
            if unique_key not in unique_songs:
                unique_songs[unique_key] = LXNSProvider._deser_song(song)
            difficulties = unique_songs[unique_key].difficulties
            difficulties.standard.extend(LXNSProvider._deser_diff(difficulty) for difficulty in song["difficulties"].get("standard", []))
            difficulties.dx.extend(LXNSProvider._deser_diff(difficulty) for difficulty in song["difficulties"].get("dx", []))
            difficulties.utage.extend(LXNSProvider._deser_diff_utage(difficulty) for difficulty in song["difficulties"].get("utage", []))
        return list(unique_songs.values())

    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> LXNSPlayer:
        maimai_frames = await client.items(PlayerFrame)
        maimai_icons = await client.items(PlayerIcon)
        maimai_trophies = await client.items(PlayerTrophy)
        maimai_nameplates = await client.items(PlayerNamePlate)
        url, headers, _ = await self._build_player_request("", identifier, client)
        resp = await client._client.get(url, headers=headers)
        resp_data = self._check_response_player(resp)["data"]
        return LXNSPlayer(
            name=resp_data["name"],
            rating=resp_data["rating"],
            friend_code=resp_data["friend_code"],
            course_rank=resp_data["course_rank"],
            class_rank=resp_data["class_rank"],
            star=resp_data["star"],
            frame=await maimai_frames.by_id(resp_data["frame"]["id"]) if "frame" in resp_data else None,
            icon=await maimai_icons.by_id(resp_data["icon"]["id"]) if "icon" in resp_data else None,
            trophy=await maimai_trophies.by_id(resp_data["trophy"]["id"]) if "trophy" in resp_data else None,
            name_plate=await maimai_nameplates.by_id(resp_data["name_plate"]["id"]) if "name_plate" in resp_data else None,
            upload_time=resp_data["upload_time"],
        )

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        url, headers, use_user_api = await self._build_player_request("scores", identifier, client)
        resp = await client._client.get(url, headers=headers)
        resp_data = self._check_response_player(resp)["data"]
        scores = [s for score in resp_data if (s := LXNSProvider._deser_score(score))]
        if not use_user_api:
            # LXNSProvider's developer-level API scores are incomplete, which doesn't contain dx_rating and achievements, leading to sorting difficulties.
            # In this case, we should always fetch the b35 and b15 scores for LXNSProvider.
            scores.extend(await self.get_scores_best(identifier, client))
        return scores

    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        if identifier.friend_code is None:
            return await self.get_scores_all(identifier, client)
        await self._ensure_friend_code(client, identifier)
        entrypoint = f"api/v0/maimai/player/{identifier.friend_code}/bests"
        resp = await client._client.get(self.base_url + entrypoint, headers=self.headers)
        resp_data = self._check_response_player(resp)["data"]
        return [s for score in resp_data["standard"] + resp_data["dx"] if (s := LXNSProvider._deser_score(score))]

    async def get_scores_one(self, identifier: PlayerIdentifier, song: Song, client: "MaimaiClient") -> list[Score]:
        await self._ensure_friend_code(client, identifier)
        request_tasks, create_task = [], lambda type: asyncio.create_task(
            client._client.get(
                self.base_url + f"api/v0/maimai/player/{identifier.friend_code}/bests",
                params={"song_id": song.id if type != SongType.UTAGE else song.id + 100000, "song_type": type.value},
                headers=self.headers,
            )
        )
        if len(song.difficulties.standard) > 0:
            request_tasks.append(create_task(SongType.STANDARD))
        if len(song.difficulties.dx) > 0:
            request_tasks.append(create_task(SongType.DX))
        if len(song.difficulties.utage) > 0:
            request_tasks.append(create_task(SongType.UTAGE))
        resps = await asyncio.gather(*request_tasks)
        resp_data = [self._check_response_player(resp)["data"] for resp in resps]
        return [s for score in reduce(concat, resp_data) if (s := LXNSProvider._deser_score(score))]

    async def update_scores(self, identifier: PlayerIdentifier, scores: Iterable[Score], client: "MaimaiClient") -> None:
        maimai_songs = await client.songs()
        url, headers, _ = await self._build_player_request("scores", identifier, client)
        scores_dict = {"scores": [json for score in scores if (json := await LXNSProvider._ser_score(score, maimai_songs))]}
        resp = await client._client.post(url, headers=headers, json=scores_dict)
        resp.raise_for_status()
        resp_json = resp.json()
        if not resp_json["success"] and resp_json["code"] == 400:
            raise ValueError(resp_json["message"])

    async def get_aliases(self, client: "MaimaiClient") -> dict[int, list[str]]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/alias/list")
        resp.raise_for_status()
        return {item["song_id"]: item["aliases"] for item in resp.json()["aliases"]}

    async def get_icons(self, client: "MaimaiClient") -> dict[int, PlayerIcon]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/icon/list")
        resp.raise_for_status()
        return {item["id"]: LXNSProvider._deser_item(item, PlayerIcon) for item in resp.json()["icons"]}

    async def get_nameplates(self, client: "MaimaiClient") -> dict[int, PlayerNamePlate]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/plate/list")
        resp.raise_for_status()
        return {item["id"]: LXNSProvider._deser_item(item, PlayerNamePlate) for item in resp.json()["plates"]}

    async def get_frames(self, client: "MaimaiClient") -> dict[int, PlayerFrame]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/frame/list")
        resp.raise_for_status()
        return {item["id"]: LXNSProvider._deser_item(item, PlayerFrame) for item in resp.json()["frames"]}
