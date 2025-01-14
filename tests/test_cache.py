import asyncio
import time
import pytest

from maimai_py import caches
from maimai_py.maimai import MaimaiClient, MaimaiSongs
from maimai_py.providers import LXNSProvider


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_songs_caching(maimai: MaimaiClient, lxns: LXNSProvider):
    caches.default_caches._caches = {}  # ensure that the cache is empty

    # Fetch the songs for the first time
    start_time = time.time()
    await MaimaiSongs._get_or_fetch()
    first_time = time.time() - start_time

    # Fetch the songs for the second time
    start_time = time.time()
    await MaimaiSongs._get_or_fetch()
    second_time = time.time() - start_time

    await maimai.flush()  # to test whether the flush is working properly

    assert second_time * 10 <= first_time  # the second time should be much faster than the first time


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_items_caching(maimai: MaimaiClient, lxns: LXNSProvider):
    tasks = [caches.default_caches.get_or_fetch(item) for item in ["icons", "nameplates", "frames", "trophies", "charas", "partners"]]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    pytest.main(["-q", "--runslow", "-x", "-p no:warnings", "-s", __file__])
