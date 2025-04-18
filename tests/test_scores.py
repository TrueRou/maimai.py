import pytest

from maimai_py.enums import LevelIndex, ScoreKind
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider


@pytest.mark.asyncio()
async def test_scores_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), kind=ScoreKind.ALL, provider=lxns)
    assert my_scores.rating_b35 > 10000
    score = next(my_scores.by_song(1231, level_index=LevelIndex.MASTER))
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    my_scores = await maimai.scores(PlayerIdentifier(username="turou"), kind=ScoreKind.ALL, provider=divingfish)
    assert my_scores.rating > 15000
    score = next(my_scores.by_song(1231, level_index=LevelIndex.MASTER))
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    assert all([score.difficulty.level_value <= 15.0 for score in my_scores.scores if score.difficulty])
    assert all([score.song.bpm > 10 for score in my_scores.scores if score.song])

    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "舞将", provider=lxns)
    assert my_plate.cleared_num + my_plate.remained_num == my_plate.all_num


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_scores_updating_lxns_personal(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    from tests import secrets

    scores = await maimai.scores(PlayerIdentifier(username="turou"), kind=ScoreKind.ALL, provider=divingfish)
    await maimai.updates(PlayerIdentifier(credentials=secrets.lxns_personal_token), scores.scores, provider=lxns)


@pytest.mark.asyncio()
async def test_scores_updating(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    scores = await maimai.scores(PlayerIdentifier(username="turou"), kind=ScoreKind.ALL, provider=divingfish)
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
