"""Mock-based tests for the DivingFishProvider OAuth support (no network, no credentials).

OAuth identities are provided through the ``ref``/``sub`` fields of PlayerIdentifier (or ``username``
together with the client credentials) and routed to the Bearer endpoints. Legacy branches (password
login, Import-Token, developer token) are covered as regressions.
"""

import asyncio
import hashlib
import json
from urllib.parse import parse_qs

import httpx
import pytest

from maimai_py import DivingFishProvider, MaimaiClientMultithreading
from maimai_py.exceptions import (
    InvalidDeveloperTokenError,
    InvalidPlayerIdentifierError,
    MaimaiPyError,
    PlayerNotAuthorizedError,
    PrivacyLimitationError,
    RateLimitError,
)
from maimai_py.models import FCType, LevelIndex, PlayerIdentifier, RateType, Score, Song, SongType

AUTH_TOKEN_URL = "https://auth.diving-fish.com/oauth/token"
PROBER_BASE = "https://www.diving-fish.com/api/maimaidxprober"
GRANT_ON_BEHALF_OF = "urn:diving-fish:params:oauth:grant-type:on-behalf-of"

CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-client-secret"
EXTERNAL_ID = "external-user-1"
REF_SUBJECT = "ref:" + hashlib.sha256(f"{CLIENT_ID}:{EXTERNAL_ID}".encode()).hexdigest()

SCORE_JSON = {
    "achievements": 101.0,
    "ds": 13.6,
    "dxScore": 644,
    "fc": "fc",
    "fs": "",
    "level": "13+",
    "level_index": 3,
    "level_label": "Master",
    "ra": 270,
    "rate": "ssp",
    "song_id": 834,
    "title": "Altale",
    "type": "SD",
}

MUSIC_DATA = {
    "id": "834",
    "basic_info": {"title": "Altale", "artist": "Yunosuke", "genre": "maimai", "bpm": 175, "from": "maimai"},
    "level": ["5", "8", "11+", "13+"],
    "ds": [5.0, 8.5, 11.9, 13.6],
    "charts": [
        {"charter": "charteer", "notes": [100, 5, 3, 4]},
        {"charter": "charteer", "notes": [120, 8, 6, 7]},
        {"charter": "charteer", "notes": [150, 12, 10, 9]},
        {"charter": "charteer", "notes": [200, 20, 15, 12]},
    ],
}

RECORDS_RESPONSE = {
    "username": "tester",
    "nickname": "tester",
    "rating": 15000,
    "additional_rating": 20,
    "plate": "舞舞舞",
    "records": [SCORE_JSON],
}

EXCHANGE_ERRORS = {
    # error responses of the on-behalf-of token exchange, see the OAuth API document section 4.3
    "invalid_scope": (400, {"error": "invalid_scope", "error_description": "scope is not approved for this client"}),
    "unauthorized_client": (400, {"error": "unauthorized_client", "error_description": "grant type not allowed"}),
    "malformed_subject": (400, {"error": "invalid_request", "error_description": "subject is missing or malformed"}),
}


class Recorder:
    """Collects the requests seen by the mock transport and counts the token exchanges."""

    def __init__(self):
        self.requests = []
        self.exchanges = 0


def make_transport(
    state: Recorder,
    *,
    consent=False,
    reject_first_token=False,
    quota_exceeded=False,
    scope_forbidden=False,
    privacy_limited=False,
    oauth_disabled=False,
    exchange_error=None,
):
    def handler(request: httpx.Request) -> httpx.Response:
        state.requests.append(request)
        url = str(request.url)
        if url == AUTH_TOKEN_URL:
            state.exchanges += 1
            if consent:
                return httpx.Response(400, json={"error": "consent_required", "error_description": "the player has not consented"})
            if exchange_error is not None:
                status_code, body = EXCHANGE_ERRORS[exchange_error]
                return httpx.Response(status_code, json=body)
            return httpx.Response(
                200,
                json={
                    "access_token": f"token-{state.exchanges}",
                    "token_type": "Bearer",
                    "expires_in": 300,
                    "scope": "prober.records.read",
                },
            )
        path = request.url.path
        if path in ("/api/maimaidxprober/player/records", "/api/maimaidxprober/player/update_records"):
            if oauth_disabled and request.headers.get("Authorization"):
                return httpx.Response(503, json={"status": "error", "message": "服务端未启用 OAuth"})
            if scope_forbidden:
                return httpx.Response(403, json={"status": "error", "message": "access token 缺少权限：prober.records.write"})
            if privacy_limited:
                return httpx.Response(403, json={"status": "error", "message": "该用户未同意用户协议"})
            if quota_exceeded:
                return httpx.Response(429, json={"status": "error", "message": "已超出今日请求上限"})
            if reject_first_token and request.headers.get("Authorization") == "Bearer token-1":
                return httpx.Response(401, json={"status": "error", "message": "token expired"})
        if path == "/api/maimaidxprober/player/records":
            return httpx.Response(200, json=RECORDS_RESPONSE)
        if path == "/api/maimaidxprober/player/record":
            return httpx.Response(200, json={"834": [SCORE_JSON]})
        if path == "/api/maimaidxprober/player/update_records":
            return httpx.Response(200, json={"status": "success"})
        if path == "/api/maimaidxprober/query/player":
            return httpx.Response(200, json={**RECORDS_RESPONSE, "charts": {"sd": [SCORE_JSON], "dx": []}})
        if path == "/api/maimaidxprober/login":
            if json.loads(request.content) == {"username": "someone", "password": "some-password"}:
                return httpx.Response(200, json={"message": "登录成功"})
            return httpx.Response(400, json={"message": "用户名或密码错误"})
        return httpx.Response(404, json={"message": f"unexpected url {url}"})

    return httpx.MockTransport(handler)


def make_app(state: Recorder, **flags):
    provider = DivingFishProvider(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    client = MaimaiClientMultithreading(transport=make_transport(state, **flags))
    return provider, client


def make_song() -> Song:
    song = DivingFishProvider._deser_song(MUSIC_DATA)
    song.difficulties.standard.extend(DivingFishProvider._deser_diffs(MUSIC_DATA))
    return song


def make_score() -> Score:
    return Score(
        id=834,
        level="13+",
        level_index=LevelIndex.MASTER,
        achievements=101.0,
        fc=FCType.FC,
        fs=None,
        dx_score=644,
        dx_rating=270,
        play_count=None,
        play_time=None,
        rate=RateType.SSSP,
        type=SongType.STANDARD,
    )


async def get_cached_token(client, subject: str) -> str | None:
    return await client._cache.get(subject, namespace=DivingFishProvider.oauth_token_namespace)


async def test_oauth_scores_all_exchanges_and_uses_bearer():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert scores[0].id == 834
    assert scores[0].level_index == LevelIndex.MASTER
    exchange, records = state.requests[0], state.requests[1]
    assert str(exchange.url) == AUTH_TOKEN_URL
    form = parse_qs(exchange.content.decode())
    assert form["grant_type"] == [GRANT_ON_BEHALF_OF]
    assert form["client_id"] == [CLIENT_ID]
    assert form["client_secret"] == [CLIENT_SECRET]
    assert form["subject"] == [REF_SUBJECT]
    assert "scope" not in form  # omitted on purpose: the granted scope is the consent/approval intersection
    assert str(records.url) == f"{PROBER_BASE}/player/records"
    assert records.headers["Authorization"] == "Bearer token-1"
    assert "qq" not in records.url.params and "username" not in records.url.params


async def test_oauth_sub_subject_is_prefixed_as_is():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(sub=12345)

    await provider.get_scores_all(identifier, client)

    form = parse_qs(state.requests[0].content.decode())
    assert form["subject"] == ["sub:12345"]


async def test_oauth_username_uses_subject_when_client_credentials_configured():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(username="turou")

    await provider.get_scores_all(identifier, client)

    form = parse_qs(state.requests[0].content.decode())
    assert form["subject"] == ["username:turou"]
    assert state.requests[1].headers["Authorization"] == "Bearer token-1"


async def test_oauth_token_is_cached_across_calls():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    await provider.get_scores_all(identifier, client)
    await provider.get_scores_all(identifier, client)

    assert state.exchanges == 1  # the 5-minute token is reused instead of re-exchanged
    assert await get_cached_token(client, REF_SUBJECT) == "token-1"


async def test_oauth_token_cache_is_shared_across_providers():
    state = Recorder()
    provider, client = make_app(state)
    another_provider = DivingFishProvider(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    await provider.get_scores_all(identifier, client)
    await another_provider.get_scores_all(identifier, client)

    assert state.exchanges == 1  # the token lives in the client cache, not on the provider instance


async def test_oauth_expired_token_is_refreshed_once():
    state = Recorder()
    provider, client = make_app(state, reject_first_token=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert state.exchanges == 2  # 401 -> drop cache -> re-exchange -> retry
    assert state.requests[-1].headers["Authorization"] == "Bearer token-2"
    assert await get_cached_token(client, REF_SUBJECT) == "token-2"


async def test_oauth_consent_required_raises_player_not_authorized():
    state = Recorder()
    provider, client = make_app(state, consent=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(PlayerNotAuthorizedError):
        await provider.get_scores_all(identifier, client)
    # the failure happens at the exchange, nothing reaches the prober
    assert len(state.requests) == 1 and str(state.requests[0].url) == AUTH_TOKEN_URL


@pytest.mark.parametrize("exchange_error", ["invalid_scope", "unauthorized_client"])
async def test_oauth_exchange_client_misconfiguration_raises_developer_token_error(exchange_error):
    state = Recorder()
    provider, client = make_app(state, exchange_error=exchange_error)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(InvalidDeveloperTokenError):
        await provider.get_scores_all(identifier, client)


async def test_oauth_exchange_malformed_subject_raises_identifier_error():
    state = Recorder()
    provider, client = make_app(state, exchange_error="malformed_subject")
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(InvalidPlayerIdentifierError, match="malformed"):
        await provider.get_scores_all(identifier, client)


async def test_oauth_missing_scope_raises_player_not_authorized_with_scope():
    state = Recorder()
    provider, client = make_app(state, scope_forbidden=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(PlayerNotAuthorizedError, match="prober.records.write"):
        await provider.get_scores_all(identifier, client)


async def test_oauth_privacy_limited_raises_privacy_limitation():
    state = Recorder()
    provider, client = make_app(state, privacy_limited=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(PrivacyLimitationError, match="用户协议"):
        await provider.get_scores_all(identifier, client)


async def test_oauth_disabled_on_server_raises_maimai_py_error():
    state = Recorder()
    provider, client = make_app(state, oauth_disabled=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(MaimaiPyError, match="503"):
        await provider.get_scores_all(identifier, client)


async def test_oauth_quota_exceeded_raises_rate_limit_error():
    state = Recorder()
    provider, client = make_app(state, quota_exceeded=True)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(RateLimitError):
        await provider.get_scores_all(identifier, client)


async def test_oauth_ref_takes_precedence_over_password_login():
    state = Recorder()
    provider, client = make_app(state)
    # a ref identity must never be treated as the password of the username login flow
    identifier = PlayerIdentifier(username="someone", credentials="some-password", ref=EXTERNAL_ID)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert str(state.requests[0].url) == AUTH_TOKEN_URL  # no login call happened


async def test_oauth_credentials_subject_is_passed_through_verbatim():
    state = Recorder()
    provider, client = make_app(state)
    raw_subject = "ref:" + "ff" * 32  # pre-computed by the caller, must not be hashed again
    identifier = PlayerIdentifier(credentials=raw_subject)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    form = parse_qs(state.requests[0].content.decode())
    assert form["subject"] == [raw_subject]  # used as-is


async def test_oauth_ref_field_yields_to_credentials_subject():
    state = Recorder()
    provider, client = make_app(state)
    # credentials carrying a subject prefix take precedence over the ref field
    identifier = PlayerIdentifier(ref=EXTERNAL_ID, credentials="sub:99999")

    await provider.get_scores_all(identifier, client)

    form = parse_qs(state.requests[0].content.decode())
    assert form["subject"] == ["sub:99999"]  # the credentials subject wins over the ref field


async def test_password_login_stays_on_login_flow_with_client_credentials():
    state = Recorder()
    provider, client = make_app(state)  # OAuth credentials configured, but a password must not become a subject
    identifier = PlayerIdentifier(username="someone", credentials="some-password")

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    login, records = state.requests[0], state.requests[1]
    assert str(login.url) == f"{PROBER_BASE}/login"  # the password flow was taken
    assert json.loads(login.content) == {"username": "someone", "password": "some-password"}
    assert str(records.url) == f"{PROBER_BASE}/player/records"
    assert "Authorization" not in records.headers
    assert state.exchanges == 0


async def test_oauth_scores_one_sends_music_id_only():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)
    song = make_song()

    scores = await provider.get_scores_one(identifier, song, client)

    assert len(scores) == 1 and scores[0].id == 834
    record = state.requests[1]
    assert str(record.url) == f"{PROBER_BASE}/player/record"
    assert json.loads(record.content) == {"music_id": list(song.get_divingfish_ids())}
    assert record.headers["Authorization"] == "Bearer token-1"


async def test_password_scores_one_uses_login_cookies():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(username="someone", credentials="some-password")
    song = make_song()

    scores = await provider.get_scores_one(identifier, song, client)

    assert len(scores) == 1 and scores[0].id == 834
    login, record = state.requests[0], state.requests[1]
    assert str(login.url) == f"{PROBER_BASE}/login"
    assert str(record.url) == f"{PROBER_BASE}/player/record"
    assert "Authorization" not in record.headers
    assert state.exchanges == 0


async def test_oauth_bests_falls_back_to_full_records():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    scores = await provider.get_scores_best(identifier, client)

    # the public /query/player endpoint does not accept subjects; the full records are fetched instead
    assert len(scores) == 1 and scores[0].id == 834
    assert str(state.requests[-1].url) == f"{PROBER_BASE}/player/records"
    assert state.requests[-1].headers["Authorization"] == "Bearer token-1"


async def test_legacy_bests_still_uses_query_player():
    state = Recorder()
    provider = DivingFishProvider()  # no OAuth credentials: username stays on the public endpoints
    client = MaimaiClientMultithreading(transport=make_transport(state))
    identifier = PlayerIdentifier(username="tester")

    scores = await provider.get_scores_best(identifier, client)

    assert len(scores) == 1 and scores[0].id == 834
    assert str(state.requests[0].url) == f"{PROBER_BASE}/query/player"
    assert json.loads(state.requests[0].content) == {"b50": True, "username": "tester"}


async def test_oauth_update_scores_uses_bearer():
    state = Recorder()
    provider, client = make_app(state)
    song = make_song()

    class SongListStub:
        async def by_id(self, song_id: int):
            return song if song_id == song.id % 10000 else None

    async def stub_songs(*args, **kwargs):
        return SongListStub()

    client.songs = stub_songs  # update_scores serializes scores against the song list; keep the test offline

    identifier = PlayerIdentifier(ref=EXTERNAL_ID)
    await provider.update_scores(identifier, [make_score()], client)

    update = state.requests[-1]
    assert str(update.url) == f"{PROBER_BASE}/player/update_records"
    assert update.headers["Authorization"] == "Bearer token-1"
    body = json.loads(update.content)
    assert len(body) == 1 and body[0]["title"] == "Altale"
    assert "qq" not in body[0] and "username" not in body[0]


async def test_oauth_update_scores_missing_write_scope_raises_with_scope():
    state = Recorder()
    provider, client = make_app(state, scope_forbidden=True)
    song = make_song()

    class SongListStub:
        async def by_id(self, song_id: int):
            return song if song_id == song.id % 10000 else None

    async def stub_songs(*args, **kwargs):
        return SongListStub()

    client.songs = stub_songs

    identifier = PlayerIdentifier(ref=EXTERNAL_ID)
    with pytest.raises(PlayerNotAuthorizedError, match="prober.records.write"):
        await provider.update_scores(identifier, [make_score()], client)


async def test_import_token_branch_unchanged():
    state = Recorder()
    provider = DivingFishProvider()  # no OAuth credentials configured
    client = MaimaiClientMultithreading(transport=make_transport(state))
    identifier = PlayerIdentifier(credentials="plain-import-token")

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    request = state.requests[0]
    assert str(request.url) == f"{PROBER_BASE}/player/records"
    assert request.headers.get("Import-Token") == "plain-import-token"
    assert "Authorization" not in request.headers
    assert state.exchanges == 0


async def test_ref_without_client_credentials_raises():
    state = Recorder()
    provider = DivingFishProvider()  # ref given but the application credentials are missing
    client = MaimaiClientMultithreading(transport=make_transport(state))
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    with pytest.raises(InvalidDeveloperTokenError, match="client_id"):
        await provider.get_scores_all(identifier, client)


async def test_stale_cached_token_is_exchanged_again():
    state = Recorder()
    provider, client = make_app(state)
    await client._cache.set(REF_SUBJECT, "stale-token", ttl=0.001, namespace=DivingFishProvider.oauth_token_namespace)
    await asyncio.sleep(0.01)  # let the cached entry expire
    identifier = PlayerIdentifier(ref=EXTERNAL_ID)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert state.exchanges == 1
    assert state.requests[1].headers["Authorization"] == "Bearer token-1"  # not the stale token
