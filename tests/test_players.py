from importlib.util import find_spec

import pytest

from maimai_py import LXNSProvider, MaimaiClient, PlayerIdentifier


@pytest.mark.asyncio(scope="session")
async def test_players_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    player = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert player.rating > 10000

    if find_spec("tests.secrets"):
        from tests import secrets

        personal_player = await maimai.players(PlayerIdentifier(credentials=secrets.lxns_personal_token), provider=lxns)
        assert player.rating == personal_player.rating


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
