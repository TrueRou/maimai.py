import pytest

from maimai_py.enums import LevelIndex
from maimai_py.maimai import MaimaiClient
from maimai_py.models import Player, PlayerIdentifier
from maimai_py.providers import ArcadeProvider, DivingFishProvider, LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    my_scores = await maimai.scores(lxns_player, provider=lxns)
    assert my_scores.rating_b35 > 10000
    score = my_scores.by_song(1231, level_index=LevelIndex.MASTER)[0]
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    bests = await maimai.bests(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert my_scores.rating == bests.rating

    bests_fallback = await maimai.bests(lxns_player, provider=lxns)
    assert my_scores.rating == bests_fallback.rating
    assert len(bests_fallback.scores_b35) <= 35

    preview = await maimai.minfo(1231, PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert preview is not None
    assert all(score.id == preview.song.id for score in preview.scores)

    for song, diff, score in await my_scores.get_mapping():
        assert song.id == score.id and diff.type == score.type and diff.level_index == score.level_index


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    assert my_scores.rating_b35 > 10000
    score = my_scores.by_song(1231, level_index=LevelIndex.MASTER)[0]
    assert score.dx_rating >= 308 if score.dx_rating else True  # 生命不詳 MASTER SSS+

    bests = await maimai.bests(divingfish_player, provider=divingfish)
    assert my_scores.rating == bests.rating
    assert len(bests.scores_b15) <= 15

    preview = await maimai.minfo("1231", PlayerIdentifier(username="turou"), provider=divingfish)
    assert preview is not None
    assert all(score.id == preview.song.id for score in preview.scores)


@pytest.mark.asyncio(scope="session")
async def test_scores_fetching_arcade(maimai: MaimaiClient, arcade: ArcadeProvider, arcade_player: PlayerIdentifier):
    try:
        scores = await maimai.scores(arcade_player, provider=arcade)
        assert scores.rating > 2000

        player: Player = await maimai.players(arcade_player, provider=arcade)
        assert player.rating == scores.rating
    except Exception:
        pytest.skip("Connection error, skipping the test.")


@pytest.mark.asyncio(scope="session")
async def test_plate_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "桃将", provider=lxns)
    cleared_obj = [obj for obj in await my_plate.get_cleared() if obj.song.id == 411]
    remained_obj = [obj for obj in await my_plate.get_remained() if obj.song.id == 411]
    assert len(cleared_obj) == 1 and LevelIndex.MASTER in cleared_obj[0].levels
    assert len(remained_obj) == 1 and LevelIndex.MASTER not in remained_obj[0].levels
    assert await my_plate.count_cleared() + await my_plate.count_remained() == await my_plate.count_all()


@pytest.mark.asyncio(scope="session")
async def test_scores_updating_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    scores = []
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores, provider=lxns)
    await maimai.updates(lxns_player, scores, provider=lxns)


@pytest.mark.asyncio(scope="session")
async def test_scores_updating_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    scores = []
    await maimai.updates(divingfish_player, scores, provider=divingfish)


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
