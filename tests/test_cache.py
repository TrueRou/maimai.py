import asyncio
import time
import pytest

from maimai_py import caches
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerChara, PlayerFrame, PlayerIcon, PlayerNamePlate, PlayerPartner, PlayerTrophy


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_songs_caching(maimai: MaimaiClient):
    caches.default_caches._caches = {}  # ensure that the cache is empty

    # Fetch the songs for the first time
    start_time = time.time()
    await maimai.songs()
    first_time = time.time() - start_time

    # Fetch the songs for the second time
    start_time = time.time()
    await maimai.songs()
    second_time = time.time() - start_time

    await maimai.flush()  # to test whether the flush is working properly

    assert second_time * 10 <= first_time  # the second time should be much faster than the first time


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_items_caching(maimai: MaimaiClient):
    tasks = [maimai.items(item) for item in [PlayerIcon, PlayerNamePlate, PlayerFrame, PlayerTrophy, PlayerChara, PlayerPartner]]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    pytest.main(["-q", "--runslow", "-x", "-p no:warnings", "-s", __file__])
