import pytest

from maimai_py import MaimaiClient
from maimai_py.exceptions import TitleServerError
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.arcade import ArcadeProvider


@pytest.mark.asyncio(scope="session")
async def test_regions(maimai: MaimaiClient, arcade: ArcadeProvider, arcade_player: PlayerIdentifier):
    try:
        regions = await maimai.regions(arcade_player, provider=arcade)
        assert any(region.region_id == 2 for region in regions)
    except (TitleServerError, IndexError):
        pytest.skip("Connection error, skipping the test.")


@pytest.mark.asyncio(scope="session")
async def test_areas(maimai: MaimaiClient):
    areas = await maimai.areas()
    assert len(await areas.get_all()) >= 1
    assert all(len(area.songs) >= 1 for area in await areas.get_all())


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
