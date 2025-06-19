import asyncio
import traceback

from httpx import ConnectError, ReadTimeout

from examples.proxy_updater.config import config
from maimai_py import DivingFishProvider, LXNSProvider, MaimaiClient, PlayerIdentifier, WechatProvider
from maimai_py.exceptions import InvalidPlayerIdentifierError, InvalidWechatTokenError, PrivacyLimitationError

maimai = MaimaiClient(timeout=60)
diving_provider = DivingFishProvider()
lxns_provider = LXNSProvider(developer_token=config["lxns"]["developer_token"])


async def generate_url():
    threaded_maimai = MaimaiClient(timeout=60)
    url = await threaded_maimai.wechat()
    print(f"\033[32mPlease visit the following URL in Wechat to authorize: \033[0m")
    print(url)


async def update_prober(r: str, t: str, code: str, state: str):
    try:
        print("\033[32mProber updating was triggered.\033[0m")
        # fetch the player's scores from Wahlap Wechat OffiAccount
        wx_player = await maimai.identifiers(code={"r": r, "t": t, "code": code, "state": state}, provider=WechatProvider())
        assert isinstance(wx_player, PlayerIdentifier)
        print("\033[32mPlayer fetched successfully.\033[0m")
        scores = await maimai.scores(wx_player, WechatProvider())
        print("\033[32mScores fetched successfully.\033[0m")
        # establish the tasks of updating the prober according to the configuration
        update_tasks = []
        if config["diving_fish"]["enabled"]:
            diving_player = PlayerIdentifier(username=config["diving_fish"]["username"], credentials=config["diving_fish"]["credentials"])
            task = asyncio.create_task(maimai.updates(diving_player, scores.scores, diving_provider))
            update_tasks.append(task)
        if config["lxns"]["enabled"]:
            lxns_player = PlayerIdentifier(friend_code=config["lxns"]["friend_code"])
            task = asyncio.create_task(maimai.updates(lxns_player, scores.scores, lxns_provider))
            update_tasks.append(task)
        asyncio.gather(*update_tasks)
        print(f"\033[32mProber updated successfully.\033[0m")
    except (ConnectError, ReadTimeout) as e:
        print(f"\033[31mConnection to the server timed out.\033[0m")
    except (InvalidPlayerIdentifierError, PrivacyLimitationError, InvalidWechatTokenError) as e:
        print(f"\033[31m{e}.\033[0m")
    except Exception as e:
        traceback.print_exc()
        print(f"\033[31mAn unexpected error occurred.\033[0m")
