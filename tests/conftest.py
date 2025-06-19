import os

import pytest

from maimai_py import ArcadeProvider, DivingFishProvider, LXNSProvider, MaimaiClient
from maimai_py.models import PlayerIdentifier


@pytest.fixture(scope="session")
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


@pytest.fixture(scope="session")
def lxns_player():
    if not (personal_token := os.environ.get("LXNS_PERSONAL_TOKEN")):
        from tests import secrets

        personal_token = secrets.lxns_personal_token
    return PlayerIdentifier(credentials=personal_token)


@pytest.fixture(scope="session")
def divingfish_player():
    if not (username := os.environ.get("DIVINGFISH_USERNAME")) or not (password := os.environ.get("DIVINGFISH_PASSWORD")):
        from tests import secrets

        username = secrets.divingfish_username
        password = secrets.divingfish_password
    return PlayerIdentifier(username=username, credentials=password)


@pytest.fixture(scope="session")
def arcade_player():
    if not (encrypted_userid := os.environ.get("ARCADE_ENCRYPTED_USERID")):
        from tests import secrets

        encrypted_userid = secrets.arcade_encrypted_userid
    return PlayerIdentifier(credentials=encrypted_userid)
