import pytest

from maimai_py import MaimaiClient


@pytest.mark.asyncio(scope="session")
async def test_areas(maimai: MaimaiClient):
    areas = await maimai.areas()
    assert len(await areas.get_all()) >= 1
    assert all(len(area.songs) >= 1 for area in await areas.get_all())


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
