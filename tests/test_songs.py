import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers import LXNSProvider
from maimai_py.providers.divingfish import DivingFishProvider


@pytest.mark.asyncio()
async def test_songs_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    songs = await maimai.songs()
    song1 = songs.by_id(1231)  # 生命不詳
    song2 = songs.by_alias("不知死活")

    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
    assert song1.difficulties.dx[3].curve.sample_size > 10000
    assert song2.id == song1.id

    songs = await maimai.songs(provider=divingfish)
    song4 = songs.by_id(1231)
    assert song4.title == song1.title

    song5 = songs.by_keywords("超天酱")
    assert any(song.id == 1568 for song in song5)


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
