import hashlib
import time
import typing
from json import JSONDecodeError
from typing import TYPE_CHECKING, Generator, Iterable

from httpx import HTTPStatusError, RequestError, Response
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from maimai_py.exceptions import PlayerNotAuthorizedError, RateLimitError
from maimai_py.models import *
from maimai_py.models import PlayerIdentifier, Score, Song

from .base import ICurveProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ISongProvider

if TYPE_CHECKING:
    from maimai_py.maimai import MaimaiClient, MaimaiSongs


class DivingFishProvider(ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ICurveProvider):
    """The provider that fetches data from the Diving Fish.

    DivingFish: https://www.diving-fish.com/maimaidx/prober/

    Besides the legacy developer token, this provider supports the Diving Fish account OAuth
    (https://maimai.diving-fish.com/manual/docs/developer/oauth-migration), which replaces the developer
    token endpoints sunset on 2026-10-01. Pass the ``client_id``/``client_secret`` of your application
    registered at https://auth.diving-fish.com/console, and designate the queried player by putting an
    OAuth subject into ``PlayerIdentifier.credentials`` (``ref:<digest>``, ``sub:<user id>`` or
    ``username:<name>``). Access tokens are exchanged on the fly and cached until they nearly expire.
    """

    developer_token: Optional[str]
    """The developer token used to access the legacy developer endpoints (sunset on 2026-10-01)."""
    client_id: Optional[str]
    """The OAuth client id of the application registered at the Diving Fish authorization server."""
    client_secret: Optional[str]
    """The OAuth client secret of the application, must be kept server-side only."""
    base_url = "https://www.diving-fish.com/api/maimaidxprober/"
    """The base URL for the Diving Fish API."""
    auth_base_url = "https://auth.diving-fish.com/"
    """The base URL for the Diving Fish authorization server."""
    oauth_subject_prefixes = ("ref:", "sub:", "username:")
    """Prefixes that mark ``PlayerIdentifier.credentials`` as an OAuth subject instead of an Import-Token or a password."""

    @property
    def headers(self):
        """@private"""
        if not self.developer_token:
            raise InvalidDeveloperTokenError("Developer token is not provided.")
        return {"developer-token": self.developer_token}

    def __init__(
        self,
        developer_token: Optional[str] = None,
        *,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """Initializes the DivingFishProvider.

        Args:
            developer_token: The developer token used to access the legacy developer endpoints (sunset on 2026-10-01).
            client_id: The OAuth client id of your registered application.
            client_secret: The OAuth client secret of your application, keep it server-side only.
        """
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self._oauth_tokens: dict[str, tuple[str, float]] = {}
        """Exchanged access tokens as subject -> (token, expires_at), reused until 30 seconds before expiry."""

    def _hash(self) -> str:
        return hashlib.md5(b"divingfish").hexdigest()

    @staticmethod
    def _deser_song(song: dict) -> Song:
        return Song(
            id=int(song["id"]) % 10000,
            title=song["basic_info"]["title"] if int(song["id"]) != 383 else "Link",
            artist=song["basic_info"]["artist"],
            genre=name_to_genre[song["basic_info"]["genre"]],
            bpm=song["basic_info"]["bpm"],
            map=None,
            rights=None,
            aliases=None,
            version=divingfish_to_version[song["basic_info"]["from"]].value,
            disabled=False,
            difficulties=SongDifficulties(standard=[], dx=[], utage=[]),
        )

    @staticmethod
    def _deser_diffs(song: dict) -> Generator[SongDifficulty, None, None]:
        song_id, song_type = int(song["id"]), SongType._from_id(song["id"])
        if song_type == SongType.STANDARD or song_type == SongType.DX:
            for idx, chart in enumerate(song["charts"]):
                yield SongDifficulty(
                    type=song_type,
                    level=song["level"][idx],
                    level_value=song["ds"][idx],
                    level_index=LevelIndex(idx),
                    note_designer=chart["charter"],
                    version=divingfish_to_version[song["basic_info"]["from"]].value,
                    tap_num=chart["notes"][0],
                    hold_num=chart["notes"][1],
                    slide_num=chart["notes"][2],
                    touch_num=chart["notes"][3] if song_type == SongType.DX else 0,
                    break_num=chart["notes"][4] if song_type == SongType.DX else chart["notes"][3],
                    curve=None,
                )
        elif song_type == SongType.UTAGE and len(song["charts"]) > 0:
            first_diff = song["charts"][0]
            second_diff = song["charts"][1] if len(song["charts"]) > 1 else None
            yield SongDifficultyUtage(
                diff_id=song_id,
                kanji=song["basic_info"]["title"][1:2],
                description="LET'S PARTY!",
                is_buddy=len(song["charts"]) == 2,
                type=song_type,
                level=song["level"][0],
                level_value=song["ds"][0],
                level_index=LevelIndex(0),
                note_designer=first_diff["charter"],
                version=divingfish_to_version[song["basic_info"]["from"]].value,
                tap_num=first_diff["notes"][0] + (second_diff["notes"][0] if second_diff else 0),
                hold_num=first_diff["notes"][1] + (second_diff["notes"][1] if second_diff else 0),
                slide_num=first_diff["notes"][2] + (second_diff["notes"][2] if second_diff else 0),
                touch_num=first_diff["notes"][3] + (second_diff["notes"][3] if second_diff else 0),
                break_num=first_diff["notes"][4] + (second_diff["notes"][4] if second_diff else 0),
                buddy_notes=BuddyNotes(
                    left_tap_num=first_diff["notes"][0],
                    left_hold_num=first_diff["notes"][1],
                    left_slide_num=first_diff["notes"][2],
                    left_touch_num=first_diff["notes"][3],
                    left_break_num=first_diff["notes"][4],
                    right_tap_num=second_diff["notes"][0],
                    right_hold_num=second_diff["notes"][1],
                    right_slide_num=second_diff["notes"][2],
                    right_touch_num=second_diff["notes"][3],
                    right_break_num=second_diff["notes"][4],
                )
                if second_diff
                else None,
                curve=None,
            )

    @staticmethod
    def _deser_score(score: dict) -> Score:
        return Score(
            id=score["song_id"] if score["song_id"] > 100000 else score["song_id"] % 10000,
            level=score["level"],
            level_index=LevelIndex(score["level_index"]),
            achievements=score["achievements"],
            fc=FCType[score["fc"].upper()] if score["fc"] else None,
            fs=FSType[score["fs"].upper()] if score["fs"] else None,
            dx_score=score["dxScore"],
            dx_rating=score["ra"],
            play_count=None,
            play_time=None,
            rate=RateType[score["rate"].upper()],
            type=SongType._from_id(score["song_id"]),
        )

    @staticmethod
    async def _ser_score(score: Score, songs: "MaimaiSongs") -> Optional[dict]:
        if song := await songs.by_id(score.id % 10000):
            song_title = "Link(CoF)" if score.id == 383 else song.title
            if score.type == SongType.UTAGE and (diff := song.get_difficulty(score.type, score.id)):
                diff = typing.cast(SongDifficultyUtage, diff)
                song_title = f"[{diff.kanji}]{song_title}"
            return {
                "title": song_title,
                "level_index": score.level_index.value,
                "achievements": score.achievements,
                "fc": score.fc.name.lower() if score.fc else None,
                "fs": score.fs.name.lower() if score.fs else None,
                "dxScore": score.dx_score,
                "type": score.type._to_abbr(),
            }

    @staticmethod
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

    @staticmethod
    def _oauth_subject(identifier: PlayerIdentifier) -> Optional[str]:
        """Returns the OAuth subject carried in ``credentials``, or None if the credentials are not a subject."""
        credentials = identifier.credentials
        if isinstance(credentials, str) and credentials.startswith(DivingFishProvider.oauth_subject_prefixes):
            return credentials
        return None

    async def _access_token(self, subject: str, client: "MaimaiClient") -> str:
        """Fetches a short-lived access token representing the subject, reusing the cached one while valid."""
        cached = self._oauth_tokens.get(subject)
        if cached is not None and cached[1] > time.time() + 30:
            return cached[0]
        if not (self.client_id and self.client_secret):
            raise InvalidDeveloperTokenError("OAuth client_id/client_secret is required to exchange a subject for an access token.")
        resp = await client._client.post(
            f"{self.auth_base_url}oauth/token",
            data={
                "grant_type": "urn:diving-fish:params:oauth:grant-type:on-behalf-of",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "subject": subject,
                # No scope requested: the granted scope is the intersection of the player's consent and the approved scopes.
            },
        )
        try:
            resp_json: dict = resp.json()
        except JSONDecodeError as exc:
            raise InvalidJsonError(resp.text) from exc
        if resp.status_code == 200:
            token, expires_in = resp_json["access_token"], int(resp_json.get("expires_in", 300))
            self._oauth_tokens[subject] = (token, time.time() + expires_in)
            return token
        error, description = resp_json.get("error"), resp_json.get("error_description", "")
        if error == "consent_required":
            raise PlayerNotAuthorizedError(description or "The player has not authorized this application.")
        if resp.status_code == 401:
            raise InvalidDeveloperTokenError("OAuth client_id/client_secret is invalid, or the application is disabled.")
        if resp.status_code == 429:
            raise RateLimitError(description or "The token exchange is rate limited, cache and reuse your access tokens.")
        raise MaimaiPyError(f"OAuth token exchange failed ({resp.status_code}): {error or description}")

    async def _bearer_request(self, client: "MaimaiClient", subject: str, method: str, url: str, **kwargs) -> Response:
        """Performs a Bearer-authenticated request, refreshing the access token once if it expires in flight."""
        headers = {"Authorization": f"Bearer {await self._access_token(subject, client)}"}
        resp = await client._client.request(method, url, headers=headers, **kwargs)
        if resp.status_code == 401:  # the cached token may have just expired or been revoked, refresh once and retry
            self._oauth_tokens.pop(subject, None)
            headers = {"Authorization": f"Bearer {await self._access_token(subject, client)}"}
            resp = await client._client.request(method, url, headers=headers, **kwargs)
        return resp

    def _check_response_player(self, resp: Response) -> dict:
        try:
            resp_json = resp.json()
            if resp.status_code in [400, 401]:
                raise InvalidPlayerIdentifierError(resp_json["message"])
            elif resp.status_code == 403:
                message = resp_json.get("message", "")
                if "缺少权限" in message:  # the access token lacks the scope required by the endpoint
                    raise PlayerNotAuthorizedError(message)
                raise PrivacyLimitationError(message)
            elif resp.status_code == 410:
                raise InvalidDeveloperTokenError("The developer token endpoints are sunset (410 Gone), migrate to OAuth Bearer.")
            elif resp.status_code == 429:
                raise RateLimitError(resp_json.get("message", "The daily request quota is exceeded."))
            elif "msg" in resp_json and resp_json["msg"] in [
                "请先联系水鱼申请开发者token",
                "开发者token有误",
                "开发者token被禁用",
            ]:
                raise InvalidDeveloperTokenError(resp_json["msg"])
            elif "message" in resp_json and resp_json["message"] in ["导入token有误", "尚未登录", "会话过期"]:
                raise InvalidPlayerIdentifierError(resp_json["message"])
            elif not resp.is_success:
                resp.raise_for_status()
            return resp_json
        except JSONDecodeError as exc:
            raise InvalidJsonError(resp.text) from exc
        except HTTPStatusError as exc:
            raise MaimaiPyError(exc) from exc

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_songs(self, client: "MaimaiClient") -> list[Song]:
        resp = await client._client.get(self.base_url + "music_data")
        resp.raise_for_status()
        resp_json = resp.json()
        songs_unique: dict[int, Song] = {}
        for song in resp_json:
            song_key = int(song["id"]) % 10000
            song_type: SongType = SongType._from_id(song["id"])
            if song_key not in songs_unique:
                songs_unique[song_key] = DivingFishProvider._deser_song(song)
            difficulties: list[SongDifficulty] = songs_unique[song_key].difficulties.__getattribute__(song_type.value)
            difficulties.extend(DivingFishProvider._deser_diffs(song))
        return list(songs_unique.values())

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_player(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> DivingFishPlayer:
        resp = await client._client.post(self.base_url + "query/player", json=identifier._as_diving_fish())
        resp_json = self._check_response_player(resp)
        return DivingFishPlayer(
            name=resp_json["username"],
            rating=resp_json["rating"],
            nickname=resp_json["nickname"],
            plate=resp_json["plate"],
            additional_rating=resp_json["additional_rating"],
        )

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_scores_all(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        subject = self._oauth_subject(identifier)
        if subject is not None:  # OAuth Bearer, the replacement of the sunset GET /dev/player/records
            resp = await self._bearer_request(client, subject, "GET", self.base_url + "player/records")
        elif identifier.username and identifier.credentials:
            login_json = {"username": identifier.username, "password": identifier.credentials}
            login_resp = await client._client.post(
                "https://www.diving-fish.com/api/maimaidxprober/login", json=login_json
            )
            self._check_response_player(login_resp)
            resp = await client._client.get(self.base_url + "player/records", cookies=login_resp.cookies)
        elif not identifier.username and identifier.credentials and isinstance(identifier.credentials, str):
            resp = await client._client.get(
                self.base_url + "player/records", headers={"Import-Token": identifier.credentials}
            )
        else:
            resp = await client._client.get(
                self.base_url + "dev/player/records", params=identifier._as_diving_fish(), headers=self.headers
            )
        resp_json = self._check_response_player(resp)
        return [s for score in resp_json["records"] if (s := DivingFishProvider._deser_score(score))]

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_scores_best(self, identifier: PlayerIdentifier, client: "MaimaiClient") -> list[Score]:
        resp = await client._client.post(
            self.base_url + "query/player", json={"b50": True, **identifier._as_diving_fish()}
        )
        resp_json = self._check_response_player(resp)
        return [
            DivingFishProvider._deser_score(score) for score in resp_json["charts"]["sd"] + resp_json["charts"]["dx"]
        ]

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_scores_one(self, identifier: PlayerIdentifier, song: Song, client: "MaimaiClient") -> list[Score]:
        subject = self._oauth_subject(identifier)
        if subject is not None:  # OAuth Bearer, the replacement of the sunset POST /dev/player/record
            resp = await self._bearer_request(
                client,
                subject,
                "POST",
                self.base_url + "player/record",
                json={"music_id": list(song.get_divingfish_ids())},
            )
        else:
            resp = await client._client.post(
                self.base_url + "dev/player/record",
                json={"music_id": list(song.get_divingfish_ids()), **identifier._as_diving_fish()},
                headers=self.headers,
            )
        resp_json: dict[str, dict] = self._check_response_player(resp)
        return [s for scores in resp_json.values() for score in scores if (s := DivingFishProvider._deser_score(score))]

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def update_scores(
        self, identifier: PlayerIdentifier, scores: Iterable[Score], client: "MaimaiClient"
    ) -> None:
        headers, cookies = None, None
        maimai_songs = await client.songs()
        scores_json = [json for score in scores if (json := await DivingFishProvider._ser_score(score, maimai_songs))]
        subject = self._oauth_subject(identifier)
        if subject is not None:  # OAuth Bearer, requires the prober.records.write scope on the consent
            resp2 = await self._bearer_request(
                client, subject, "POST", self.base_url + "player/update_records", json=scores_json
            )
        else:
            if identifier.username and identifier.credentials:
                login_json = {"username": identifier.username, "password": identifier.credentials}
                resp1 = await client._client.post("https://www.diving-fish.com/api/maimaidxprober/login", json=login_json)
                self._check_response_player(resp1)
                cookies = resp1.cookies
            elif not identifier.username and identifier.credentials and isinstance(identifier.credentials, str):
                headers = {"Import-Token": identifier.credentials}
            else:
                raise InvalidPlayerIdentifierError(
                    "Either username and password or import token is required to deliver scores"
                )
            resp2 = await client._client.post(
                self.base_url + "player/update_records", cookies=cookies, headers=headers, json=scores_json
            )
        self._check_response_player(resp2)

    @retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(RequestError), reraise=True)
    async def get_curves(self, client: "MaimaiClient") -> dict[tuple[int, SongType], list[CurveObject]]:
        resp = await client._client.get(self.base_url + "chart_stats")
        resp.raise_for_status()
        return {
            (int(idx) % 10000, SongType._from_id(int(idx))): (
                [DivingFishProvider._deser_curve(chart) for chart in charts if chart != {}]
            )
            for idx, charts in (resp.json())["charts"].items()
        }
