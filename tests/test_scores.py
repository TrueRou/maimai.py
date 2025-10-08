import pytest

from maimai_py.enums import LevelIndex
from maimai_py.maimai import MaimaiClient
from maimai_py.models import Player, PlayerIdentifier
from maimai_py.providers import ArcadeProvider, DivingFishProvider, LXNSProvider
from maimai_py.utils.page_parser import wmdx_html2score, wmdx_html2record


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
    assert all((score.id % 10000) == preview.song.id for score in preview.scores)

    for song, diff, score in await my_scores.get_mapping():
        assert song.id == (score.id % 10000) and diff.type == score.type and diff.level_index == score.level_index


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
    assert all((score.id % 10000) == preview.song.id for score in preview.scores)


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


@pytest.mark.asyncio(scope="session")
async def test_scores_wechat():
    with (open("./tests/sample_data/scores.html", "r", encoding="utf-8") as file):
        html_scores = wmdx_html2score(file.read())
        assert len(html_scores) == 8
        
        score1 = [s for s in html_scores if s.title == "花となれ"][0]
        assert score1.achievements == 101.0000 and score1.fc == "app" and score1.fs == "sync" and score1.rate == "sssp"
        assert score1.level == "8+" and score1.level_index == 2 and score1.type == "DX" and score1.dx_score == 752
        score2 = [s for s in html_scores if s.title == "\u3000"][0] # corner case：如月车站
        assert score2.achievements == 100.8750 and score2.fc == "ap" and score2.fs == "sync" and score2.rate == "sssp"
        score3 = [s for s in html_scores if s.title == "シックスプラン"][0]
        assert score3.achievements == 99.9338 and score3.fc == "fcp" and score3.fs == "fs" and score3.rate == "ssp"
        score4 = [s for s in html_scores if s.title == "Cyaegha"][0]
        assert score4.achievements == 97.0887 and score4.fc == "" and score4.fs == "" and score4.rate == "s"
        score5 = [s for s in html_scores if s.title == "maimaiちゃんのテーマ"][0]
        assert score5.achievements == 98.1502 and score5.fc == "fc" and score5.fs == "fsp" and score5.rate == "sp"
        assert score5.type == "SD" and score5.dx_score == 557 and score5.level == "9" # 测一个标谱的type
        score6 = [s for s in html_scores if s.title == "STARTLINER"][0]
        assert score6.achievements == 100.1990 and score6.fc == "fcp" and score6.fs == "fdx" and score6.rate == "sss"
        score7 = [s for s in html_scores if s.title == "Limits"][0]
        assert score7.achievements == 99.3390 and score7.fc == "" and score7.fs == "sync" and score7.rate == "ss"
        score8 = [s for s in html_scores if s.title == "ロストワンの号哭"][0]
        assert score8.achievements == 90.4090 and score8.fc == "" and score8.fs == "sync" and score8.rate == "aa"


@pytest.mark.asyncio(scope="session")
async def test_records_play_time_wechat():
    with open("./tests/sample_data/record.html", "r", encoding="utf-8") as file:
        html_scores = wmdx_html2record(file.read())
        assert len(html_scores) > 0
        assert all(score.play_time is not None for score in html_scores)
        s = html_scores[0]
        assert s.title == "Re:Unknown X" and s.achievements == 98.6484 and s.fc == "" and s.fs == "sync"


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
