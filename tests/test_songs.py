import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers import LXNSProvider


@pytest.mark.asyncio()
async def test_songs_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    songs = await maimai.songs()
    song1 = songs.by_id(1231)  # 生命不詳
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"

    song2 = songs.by_alias("不知死活")
    assert song2.id == song1.id

    songs_lxns_provider = await maimai.songs(alias_provider=lxns)
    song3 = songs_lxns_provider.by_alias("星穹列车")
    assert song3.id == 241
