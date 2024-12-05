import pytest
from maimai_py.enums import LevelIndex
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.lxns import LXNSProvider


@pytest.mark.asyncio()
async def test_players_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert my_scores.rating_b35 > 10000
    assert my_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308  # 生命不詳 MASTER SSS+

    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "舞将", provider=lxns)
    assert my_plate.cleared_num + my_plate.remained_num == my_plate.total_num
