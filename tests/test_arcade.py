import pytest
from maimai_py.exceptions import TitleServerError
from maimai_py.maimai import MaimaiClient
from maimai_py.models import ArcadePlayer, PlayerIdentifier
from maimai_py.providers.arcade import ArcadeProvider


@pytest.mark.asyncio()
@pytest.mark.slow()
async def test_arcade(maimai: MaimaiClient, arcade: ArcadeProvider):
    try:
        # notice that the encrypted user id can only used in maimai.py, it's not applicable for the other use cases.
        # This is from my alt account for testing purposes, it's not a real account, don't try to attack it.
        encrypted_userid = "gAAAAABnYlOGEA5SI1y3YylkrvMWUk6Y5HuGKHHgAeFpYfmhpr7FXFkIpgyc_pVKp2wokC6lMf_KjIut1D02tgA4owQ0R2Dfvg=="
        my_account = PlayerIdentifier(credentials=encrypted_userid)
        scores = await maimai.scores(my_account, provider=arcade)
        assert scores.rating > 2000

        player: ArcadePlayer = await maimai.players(my_account, provider=arcade)  # type: ignore
        assert player.rating == scores.rating
        assert player.icon is not None

        regions = await maimai.regions(my_account, provider=arcade)
        assert any(region.region_id == 2 for region in regions)
    except TitleServerError:
        pytest.skip("Connection error, skipping the test.")


if __name__ == "__main__":
    pytest.main(["-q", "-x", "--runslow", "-p no:warnings", "-s", __file__])
