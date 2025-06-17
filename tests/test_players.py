import pytest

from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers import DivingFishProvider, LXNSProvider


@pytest.mark.asyncio(scope="session")
async def test_players_fetching_lxns(maimai: MaimaiClient, lxns: LXNSProvider, lxns_player: PlayerIdentifier):
    player = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
    assert player.rating > 10000

    player_personal = await maimai.players(lxns_player, provider=lxns)
    assert player.rating == player_personal.rating


@pytest.mark.asyncio(scope="session")
async def test_players_fetching_divingfish(maimai: MaimaiClient, divingfish: DivingFishProvider, divingfish_player: PlayerIdentifier):
    player = await maimai.players(divingfish_player, provider=divingfish)
    assert player.rating > 10000


if __name__ == "__main__":
    pytest.main(["-q", "-x", "-p no:warnings", "-s", __file__])
