import pytest

from maimai_py.maimai import MaimaiClient


@pytest.mark.asyncio()
async def test_songs_fetching():
    maimai = MaimaiClient()
    songs = await maimai.songs()
    song1 = songs.by_id(1231)  # 生命不詳
    assert song1.title == "生命不詳"
    assert song1.difficulties.dx[3].note_designer == "はっぴー"
