import os

import pytest
from dotenv import load_dotenv

from maimai_py import ArcadeProvider, DivingFishProvider, LXNSProvider, MaimaiClient
from maimai_py.models import PlayerIdentifier

load_dotenv()


@pytest.fixture(scope="session")
def maimai():
    return MaimaiClient()


@pytest.fixture(scope="session")
def lxns():
    token = os.environ.get("LXNS_DEVELOPER_TOKEN")
    return LXNSProvider(developer_token=token)


@pytest.fixture(scope="session")
def divingfish():
    token = os.environ.get("DIVINGFISH_DEVELOPER_TOKEN")
    return DivingFishProvider(developer_token=token)


@pytest.fixture(scope="session")
def arcade():
    return ArcadeProvider()


@pytest.fixture(scope="session")
def lxns_player():
    personal_token = os.environ.get("LXNS_PERSONAL_TOKEN")
    return PlayerIdentifier(credentials=personal_token)


@pytest.fixture(scope="session")
def divingfish_player():
    username = os.environ.get("DIVINGFISH_USERNAME")
    password = os.environ.get("DIVINGFISH_PASSWORD")
    return PlayerIdentifier(username=username, credentials=password)


@pytest.fixture(scope="session")
def arcade_player():
    encrypted_userid = os.environ.get("ARCADE_ENCRYPTED_USERID")
    return PlayerIdentifier(credentials=encrypted_userid)
