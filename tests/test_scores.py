import pytest

from maimai_py.enums import LevelIndex
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert my_scores.rating_b35 > 10000
    score = next(my_scores.by_song(1231, level_index=LevelIndex.MASTER))
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    assert my_scores.rating > 15000
    score = next(my_scores.by_song(1231, level_index=LevelIndex.MASTER))
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    maimai_songs = await maimai.songs()

    assert all(
        [
            diff.level_value <= 15.0 and song.bpm > 10
            for score in my_scores.scores
            if (song := await maimai_songs.by_id(score.id)) and (diff := song.get_difficulty(score.type, score.level_index))
        ]
    )

    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "桃将", provider=lxns)
    assert await my_plate.count_cleared() + await my_plate.count_remained() == await my_plate.count_all()


@pytest.mark.asyncio(scope="session")
@pytest.mark.slow()
async def test_scores_updating_lxns_personal(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    from tests import secrets

    scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    await maimai.updates(PlayerIdentifier(credentials=secrets.lxns_personal_token), scores.scores, provider=lxns)


@pytest.mark.asyncio(scope="session")
async def test_scores_updating(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
