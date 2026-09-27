"""Mock-based tests for the DivingFishProvider OAuth support (no network, no credentials).

The Diving Fish developer token endpoints return 410 Gone since 2026-10-01; the OAuth subject
identifiers must be routed to the Bearer endpoints instead. Legacy branches (password login,
Import-Token, developer token) are covered as regressions.
"""

import json
import time
from urllib.parse import parse_qs

import httpx
import pytest

from maimai_py import DivingFishProvider, MaimaiClientMultithreading
from maimai_py.exceptions import (
    InvalidDeveloperTokenError,
    PlayerNotAuthorizedError,
    RateLimitError,
)
from maimai_py.models import FCType, LevelIndex, PlayerIdentifier, RateType, Score, Song, SongType

AUTH_TOKEN_URL = "https://auth.diving-fish.com/oauth/token"
PROBER_BASE = "https://www.diving-fish.com/api/maimaidxprober"
GRANT_ON_BEHALF_OF = "urn:diving-fish:params:oauth:grant-type:on-behalf-of"

SUBJECT = "ref:" + "0a" * 32  # 64 hex chars, as produced by sha256 of "<client_id>:<external_id>"

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


class Recorder:
    """Collects the requests seen by the mock transport and counts the token exchanges."""

    def __init__(self):
        self.requests = []
        self.exchanges = 0


def make_transport(state: Recorder, *, consent=False, reject_first_token=False, quota_exceeded=False, scope_forbidden=False):
    def handler(request: httpx.Request) -> httpx.Response:
        state.requests.append(request)
        url = str(request.url)
        if url == AUTH_TOKEN_URL:
            state.exchanges += 1
            if consent:
                return httpx.Response(400, json={"error": "consent_required", "error_description": "the player has not consented"})
            return httpx.Response(
                200,
                json={
                    "access_token": f"token-{state.exchanges}",
                    "token_type": "Bearer",
                    "expires_in": 300,
                    "scope": "prober.records.read",
                },
            )
        if url == AUTH_TOKEN_URL:
            state.exchanges += 1
            if consent:
                return httpx.Response(400, json={"error": "consent_required", "error_description": "the player has not consented"})
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
        if path in ("/api/maimaidxprober/dev/player/records", "/api/maimaidxprober/dev/player/record"):
            return httpx.Response(410, json={"message": "sunset"})
        if path == "/api/maimaidxprober/player/records":
            if scope_forbidden:
                return httpx.Response(403, json={"status": "error", "message": "access token 缺少权限：prober.records.write"})
            if quota_exceeded:
                return httpx.Response(429, json={"status": "error", "message": "已超出今日请求上限"})
            if reject_first_token and request.headers.get("Authorization") == "Bearer token-1":
                return httpx.Response(401, json={"status": "error", "message": "token expired"})
            return httpx.Response(
                200,
                json={
                    "username": "tester",
                    "nickname": "tester",
                    "rating": 15000,
                    "additional_rating": 20,
                    "plate": "舞舞舞",
                    "records": [SCORE_JSON],
                },
            )
        if path == "/api/maimaidxprober/player/record":
            return httpx.Response(200, json={"834": [SCORE_JSON]})
        if path == "/api/maimaidxprober/player/update_records":
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404, json={"message": f"unexpected url {url}"})

    return httpx.MockTransport(handler)


def make_app(state: Recorder, **flags):
    provider = DivingFishProvider(client_id="test-client-id", client_secret="test-client-secret")
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


async def test_oauth_scores_all_exchanges_and_uses_bearer():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert scores[0].id == 834
    assert scores[0].level_index == LevelIndex.MASTER
    exchange, records = state.requests[0], state.requests[1]
    assert str(exchange.url) == AUTH_TOKEN_URL
    form = parse_qs(exchange.content.decode())
    assert form["grant_type"] == [GRANT_ON_BEHALF_OF]
    assert form["client_id"] == ["test-client-id"]
    assert form["client_secret"] == ["test-client-secret"]
    assert form["subject"] == [SUBJECT]
    assert "scope" not in form  # omitted on purpose: the granted scope is the consent/approval intersection
    assert str(records.url) == f"{PROBER_BASE}/player/records"
    assert records.headers["Authorization"] == "Bearer token-1"
    assert "qq" not in records.url.params and "username" not in records.url.params


async def test_oauth_token_is_cached_across_calls():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    await provider.get_scores_all(identifier, client)
    await provider.get_scores_all(identifier, client)

    assert state.exchanges == 1  # the 5-minute token is reused instead of re-exchanged


async def test_oauth_expired_token_is_refreshed_once():
    state = Recorder()
    provider, client = make_app(state, reject_first_token=True)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert state.exchanges == 2  # 401 -> drop cache -> re-exchange -> retry
    assert state.requests[-1].headers["Authorization"] == "Bearer token-2"


async def test_oauth_consent_required_raises_player_not_authorized():
    state = Recorder()
    provider, client = make_app(state, consent=True)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    with pytest.raises(PlayerNotAuthorizedError):
        await provider.get_scores_all(identifier, client)
    # the failure happens at the exchange, nothing reaches the prober
    assert len(state.requests) == 1 and str(state.requests[0].url) == AUTH_TOKEN_URL


async def test_oauth_missing_scope_raises_player_not_authorized():
    state = Recorder()
    provider, client = make_app(state, scope_forbidden=True)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    with pytest.raises(PlayerNotAuthorizedError, match="缺少权限"):
        await provider.get_scores_all(identifier, client)


async def test_oauth_quota_exceeded_raises_rate_limit_error():
    state = Recorder()
    provider, client = make_app(state, quota_exceeded=True)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    with pytest.raises(RateLimitError):
        await provider.get_scores_all(identifier, client)


async def test_oauth_subject_takes_precedence_over_password_login():
    state = Recorder()
    provider, client = make_app(state)
    # a subject in credentials must never be treated as the password of the username login flow
    identifier = PlayerIdentifier(username="someone", credentials=SUBJECT)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert str(state.requests[0].url) == AUTH_TOKEN_URL  # no login call happened


async def test_oauth_scores_one_sends_music_id_only():
    state = Recorder()
    provider, client = make_app(state)
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)
    song = make_song()

    scores = await provider.get_scores_one(identifier, song, client)

    assert len(scores) == 1 and scores[0].id == 834
    record = state.requests[1]
    assert str(record.url) == f"{PROBER_BASE}/player/record"
    assert json.loads(record.content) == {"music_id": list(song.get_divingfish_ids())}
    assert record.headers["Authorization"] == "Bearer token-1"


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

    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)
    await provider.update_scores(identifier, [make_score()], client)

    update = state.requests[-1]
    assert str(update.url) == f"{PROBER_BASE}/player/update_records"
    assert update.headers["Authorization"] == "Bearer token-1"
    body = json.loads(update.content)
    assert len(body) == 1 and body[0]["title"] == "Altale"
    assert "qq" not in body[0] and "username" not in body[0]


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


async def test_developer_token_endpoints_sunset_410():
    state = Recorder()
    provider = DivingFishProvider(developer_token="legacy-developer-token")
    client = MaimaiClientMultithreading(transport=make_transport(state))
    identifier = PlayerIdentifier(qq=12345)

    with pytest.raises(InvalidDeveloperTokenError, match="410"):
        await provider.get_scores_all(identifier, client)


async def test_subject_without_client_credentials_raises():
    state = Recorder()
    provider = DivingFishProvider()  # subject given but the application credentials are missing
    client = MaimaiClientMultithreading(transport=make_transport(state))
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    with pytest.raises(InvalidDeveloperTokenError, match="client_id"):
        await provider.get_scores_all(identifier, client)


async def test_expired_cached_token_is_exchanged_again():
    state = Recorder()
    provider, client = make_app(state)
    provider._oauth_tokens[SUBJECT] = ("stale-token", time.time() - 1)  # already expired
    identifier = PlayerIdentifier(qq=12345, credentials=SUBJECT)

    scores = await provider.get_scores_all(identifier, client)

    assert len(scores) == 1
    assert state.exchanges == 1
    assert state.requests[1].headers["Authorization"] == "Bearer token-1"  # not the stale token
