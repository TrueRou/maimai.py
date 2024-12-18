from httpx import ConnectError, ConnectTimeout, ReadTimeout
import pytest
from maimai_py.exceptions import QRCodeExpiredError
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.arcade import ArcadeProvider


@pytest.mark.asyncio()
async def test_scores_fetching_arcade(maimai: MaimaiClient):
    try:
        try:
            # This is from my alt account for testing purposes, it's not a real account, don't try to attack it.
            my_account = await maimai.qrcode("SGWCMAID241218124023A51D36BFBF65DB955DEB72905905D6A12D8056371E0499C74CD3592FCF65854C")
        except QRCodeExpiredError:
            # If the QR code is expired, use the cached encrypted user id, the user id is AES encrypted.
            # notice that the encrypted user id can only used in maimai.py, it's not applicable for the other use cases.
            # This is from my alt account for testing purposes, it's not a real account, don't try to attack it.
            encrypted_userid = "gAAAAABnYlOGEA5SI1y3YylkrvMWUk6Y5HuGKHHgAeFpYfmhpr7FXFkIpgyc_pVKp2wokC6lMf_KjIut1D02tgA4owQ0R2Dfvg=="
            my_account = PlayerIdentifier(credentials=encrypted_userid)
        scores = await maimai.scores(my_account, provider=ArcadeProvider())
        assert scores.rating > 2000
    except (ConnectError, ConnectTimeout, ReadTimeout):
        pytest.skip("Connection error, skipping the test.")
