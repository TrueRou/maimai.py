import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers import LXNSProvider
from maimai_py.providers.divingfish import DivingFishProvider


@pytest.mark.asyncio()
async def test_songs_fetching(maimai: MaimaiClient, lxns: LXNSProvider, divingfish: DivingFishProvider):
    songs = await maimai.songs()
    song1 = songs.by_id(1231)  # 生命不詳
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
    assert song1.difficulties.dx[3].curve.sample_size > 10000

    song2 = songs.by_alias("不知死活")
    assert song2.id == song1.id

    songs_lxns_provider = await maimai.songs(alias_provider=lxns)
    song3 = songs_lxns_provider.by_alias("星穹列车")
    assert song3.id == 241

    songs = await maimai.songs(provider=divingfish)
    song4 = songs.by_id(1231)
    assert song4.title == song1.title
