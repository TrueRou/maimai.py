import os
import pytest

from maimai_py import MaimaiClient
from maimai_py.providers import ArcadeProvider, DivingFishProvider, LXNSProvider


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="run slow tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope="function")
def maimai():
    return MaimaiClient()


@pytest.fixture(scope="session")
def lxns():
    if not (token := os.environ.get("LXNS_DEVELOPER_TOKEN")):
        from tests import secrets

        token = secrets.lxns_developer_token
    return LXNSProvider(developer_token=token)


@pytest.fixture(scope="session")
def divingfish():
    if not (token := os.environ.get("DIVINGFISH_DEVELOPER_TOKEN")):
        from tests import secrets

        token = secrets.divingfish_developer_token
    return DivingFishProvider(developer_token=token)


@pytest.fixture(scope="session")
def arcade():
    return ArcadeProvider()
