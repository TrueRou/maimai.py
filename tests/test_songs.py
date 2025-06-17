import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers import DivingFishProvider, LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider):
    songs = await maimai.songs(provider=divingfish, curve_provider=divingfish)
    song1 = await songs.by_id(1231)  # 生命不詳
    song2 = await songs.by_alias("不知死活")

    assert song1 is not None and song2 is not None
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
    assert song1.difficulties.dx[3].curve is not None
    assert song1.difficulties.dx[3].curve.sample_size > 10000
    assert song2.id == song1.id
    assert any([song.id == 1568 for song in await songs.by_keywords("超天酱")])


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider):
    songs = await maimai.songs(provider=lxns)
    song1 = await songs.by_id(1231)

    assert song1 is not None
    assert song1.difficulties.dx[0].tap_num != 0

    many_songs = await songs.get_batch([1231, 1232, 1233])
    assert len(many_songs) == 3


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
