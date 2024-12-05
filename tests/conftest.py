import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider
from tests import secrets


@pytest.fixture(scope="function")
def maimai():
    return MaimaiClient()


@pytest.fixture(scope="session")
def lxns():
    return LXNSProvider(developer_token=secrets.lxns_developer_token)


@pytest.fixture(scope="session")
def divingfish():
    return DivingFishProvider(developer_token=secrets.divingfish_developer_token)
