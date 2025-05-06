import pytest

from maimai_py.maimai import MaimaiClient


@pytest.mark.asyncio()
async def test_areas(maimai: MaimaiClient):
    areas = await maimai.areas()
    async for area in areas.iter_areas():
        assert len(area.songs) >= 1


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
