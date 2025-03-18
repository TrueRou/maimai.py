import pytest

from maimai_py.maimai import MaimaiClient


@pytest.mark.asyncio()
async def test_areas(maimai: MaimaiClient):
    areas = await maimai.areas()
    for area in areas.values:
        for song in area.songs:
            if song.id == -1:
                print(f"Song not found: {song.title} by {song.artist}")


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
