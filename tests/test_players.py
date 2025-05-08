import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers import LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_players_fetching(maimai: MaimaiClient, lxns: LXNSProvider):
    player = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert player.rating > 10000


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
