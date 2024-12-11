import pytest
from maimai_py.enums import LevelIndex, ScoreKind
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider


@pytest.mark.asyncio()
async def test_scores_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert my_scores.rating_b35 > 10000
    assert my_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308  # 生命不詳 MASTER SSS+

    my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    assert my_scores.rating > 15000
    assert my_scores.by_level(1231, LevelIndex.MASTER).dx_rating >= 308  # 生命不詳 MASTER SSS+

    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "舞将", provider=lxns)
    assert my_plate.cleared_num + my_plate.remained_num == my_plate.all_num

    my_plate = await maimai.plates(PlayerIdentifier(username="turou"), "舞将", provider=divingfish)
    assert my_plate.cleared_num + my_plate.remained_num == my_plate.all_num


@pytest.mark.asyncio()
async def test_scores_updating(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    scores = await maimai.scores(PlayerIdentifier(username="turou"), kind=ScoreKind.ALL, provider=divingfish)
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
