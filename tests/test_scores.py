import pytest
from maimai_py.enums import LevelIndex, ScoreKind
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers import LXNSProvider
from tests import secrets


@pytest.mark.asyncio()
async def test_players_fetching():
    maimai = MaimaiClient()
    lxns_provider = LXNSProvider(developer_token=secrets.lxns_developer_token)
    maimai_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns_provider)
    assert maimai_scores.rating_b35 > 10000
    assert maimai_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308  # 生命不詳 MASTER SSS+

    songs = await maimai.songs()
    scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), kind=ScoreKind.ALL, provider=lxns_provider)
    plate = await maimai.plates("舞将", songs, scores)
    assert plate.cleared_num + plate.remained_num == plate.total_num
