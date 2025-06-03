import dataclasses
import hashlib
from typing import TYPE_CHECKING

from httpx import Response

from maimai_py.enums import *
from maimai_py.exceptions import InvalidDeveloperTokenError, InvalidPlayerIdentifierError, PrivacyLimitationError
from maimai_py.models import *
from maimai_py.providers.base import IAliasProvider, IItemListProvider, IPlayerProvider, IScoreProvider, ISongProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class LXNSProvider(ISongProvider, IPlayerProvider, IScoreProvider, IAliasProvider, IItemListProvider):
    """The provider that fetches data from the LXNS.

    LXNS: https://maimai.lxns.net/
    """

    developer_token: str | None
    """The developer token used to access the LXNS API."""
    base_url = "https://maimai.lxns.net/"
    """The base URL for the LXNS API."""

    @property
    def headers(self):
        """@private"""
        if not self.developer_token:
            raise InvalidDeveloperTokenError()
        return {"Authorization": self.developer_token}

    def __init__(self, developer_token: str | None = None):
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
            dx_rating=score["dx_rating"] if "dx_rating" in score else None,
            rate=RateType[score["rate"].upper()],
            type=SongType[score["type"].upper()],
        )

    @staticmethod
    async def _ser_score(score: Score, songs: "MaimaiSongs") -> dict | None:
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
        resp.raise_for_status()
        resp_json = resp.json()
        if not resp_json["success"]:
            if resp_json["code"] in [400, 404]:
                raise InvalidPlayerIdentifierError(resp_json["message"])
            elif resp_json["code"] in [403]:
                raise PrivacyLimitationError(resp_json["message"])
            elif resp_json["code"] in [401]:
                raise InvalidDeveloperTokenError(resp_json["message"])
        return resp_json

    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/song/list")
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
        resp = await client._client.get(self.base_url + f"api/v0/maimai/player/{identifier._as_lxns()}", headers=self.headers)
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

    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> tuple[list[Score], list[Score]]:
        await self._ensure_friend_code(client, identifier)
        entrypoint = f"api/v0/maimai/player/{identifier.friend_code}/bests"
        resp = await client._client.get(self.base_url + entrypoint, headers=self.headers)
        resp_data = self._check_response_player(resp)["data"]
        return (
            [s for score in resp_data["standard"] if (s := LXNSProvider._deser_score(score))],
            [s for score in resp_data["dx"] if (s := LXNSProvider._deser_score(score))],
        )

    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        await self._ensure_friend_code(client, identifier)
        entrypoint = f"api/v0/maimai/player/{identifier.friend_code}/scores"
        resp = await client._client.get(self.base_url + entrypoint, headers=self.headers)
        resp_data = self._check_response_player(resp)["data"]
        return [s for score in resp_data if (s := LXNSProvider._deser_score(score))]

    async def update_scores(self, identifier: PlayerIdentifier, scores: list[Score], client: "MaimaiClient") -> None:
        maimai_songs = await client.songs()
        await self._ensure_friend_code(client, identifier)
        entrypoint = f"api/v0/maimai/player/{identifier.friend_code}/scores"
        use_headers = self.headers
        if identifier.credentials and isinstance(identifier.credentials, str):
            # If the player has a personal token, use it to update the scores
            use_headers["X-User-Token"] = identifier.credentials
            entrypoint = f"api/v0/user/maimai/player/scores"
        scores_dict = {"scores": [json for score in scores if (json := await LXNSProvider._ser_score(score, maimai_songs))]}
        resp = await client._client.post(self.base_url + entrypoint, headers=use_headers, json=scores_dict)
        resp.raise_for_status()
        resp_json = resp.json()
        if not resp_json["success"] and resp_json["code"] == 400:
            raise ValueError(resp_json["message"])

    async def get_aliases(self, client: "MaimaiClient") -> list[SongAlias]:
        resp = await client._client.get(self.base_url + "api/v0/maimai/alias/list")
        resp.raise_for_status()
        return [SongAlias(song_id=item["song_id"], aliases=item["aliases"]) for item in resp.json()["aliases"]]

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
