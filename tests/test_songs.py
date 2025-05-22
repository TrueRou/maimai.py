import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers import LXNSProvider
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.hybrid import HybridProvider


@pytest.mark.asyncio(scope="session")
async def test_songs_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    songs = await maimai.songs(provider=divingfish, curve_provider=divingfish)
    song1 = await songs.by_id(1231)  # 生命不詳
    song2 = await songs.by_alias("不知死活")

    assert song1 is not None and song2 is not None
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
    assert song1.difficulties.dx[3].curve is not None
    assert song1.difficulties.dx[3].curve.sample_size > 10000
    assert song2.id == song1.id

    hybrid = HybridProvider()

    songs = await maimai.songs(provider=hybrid)
    song4 = await songs.by_id(1231)
    assert song4 is not None
    assert song4.title == song1.title
    assert song4.difficulties.dx[0].tap_num == song1.difficulties.dx[0].tap_num

    assert any([song.id == 1568 async for song in songs.by_keywords("超天酱")])


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
