import os
import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider


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
