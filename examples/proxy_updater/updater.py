import asyncio
import json
from pathlib import Path
from httpx import ConnectError, ReadTimeout
from maimai_py.enums import ScoreKind
from maimai_py.exceptions import InvalidPlayerIdentifierError, PrivacyLimitationError
from maimai_py.maimai import MaimaiClient
from maimai_py.models import PlayerIdentifier
from maimai_py.providers.divingfish import DivingFishProvider
from maimai_py.providers.lxns import LXNSProvider
from maimai_py.providers.wechat import WechatProvider

maimai = MaimaiClient()
diving_provider = DivingFishProvider()
lxns_provider = LXNSProvider()


async def update_prober(r: str, t: str, code: str, state: str):
    config = json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))
    tasks: list[asyncio.Task] = []  # prepare a list of updating tasks
    try:
        print("A prober updating was triggered.")
        # fetch the player's scores from Wahlap Wechat OffiAccount
        wx_player = await maimai.wechat(r, t, code, state)
        scores = await maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())
        # establish the tasks of updating the prober according to the configuration
        if config["diving_fish"]["enabled"]:
            diving_player = PlayerIdentifier(username=config["diving_fish"]["username"], credentials=config["diving_fish"]["credentials"])
            tasks.append(maimai.updates(diving_player, scores.scores, diving_provider))
        if config["lxns"]["enabled"]:
            lxns_player = PlayerIdentifier(friend_code=config["lxns"]["friend_code"], developer_token=config["lxns"]["developer_token"])
            tasks.append(maimai.updates(lxns_player, scores.scores, lxns_provider))
        # execute the tasks concurrently
        await asyncio.gather(*tasks)
        print(f"{len(tasks)} prober updated successfully.")
    except (ConnectError, ReadTimeout):
        print("Failed to update prober due to network error.")
    except InvalidPlayerIdentifierError as e:
        print(f"Failed to update prober due to invalid player identifier: {e}.")
    except PrivacyLimitationError as e:
        print(f"Failed to update prober due to privacy limitation: {e}.")
