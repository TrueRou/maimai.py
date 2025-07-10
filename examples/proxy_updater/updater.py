import asyncio
import os
import traceback

from httpx import ConnectError, ReadTimeout

from maimai_py import DivingFishProvider, LXNSProvider, MaimaiClient, PlayerIdentifier, WechatProvider
from maimai_py.exceptions import InvalidPlayerIdentifierError, InvalidWechatTokenError, PrivacyLimitationError

maimai = MaimaiClient(timeout=60)
diving_provider = DivingFishProvider()
lxns_provider = LXNSProvider()


async def generate_url():
    threaded_maimai = MaimaiClient(timeout=60)
    url = await threaded_maimai.wechat()
    print(f"\033[32mPlease visit the following URL in Wechat to authorize: \033[0m")
    print(url)


async def update_prober(r: str, t: str, code: str, state: str):
    try:
        print("\033[32mProber updating was triggered.\033[0m")
        # fetch the player's scores from Wahlap Wechat OffiAccount
        wx_player = await maimai.wechat(r, t, code, state)
        assert isinstance(wx_player, PlayerIdentifier)
        print("\033[32mPlayer fetched successfully.\033[0m")
        scores = await maimai.scores(wx_player, WechatProvider())
        print("\033[32mScores fetched successfully.\033[0m")
        # establish the tasks of updating the prober according to the configuration
        update_tasks = []
        if token := os.getenv("DIVINGFISH_IMPORT_TOKEN"):
            task = asyncio.create_task(maimai.updates(PlayerIdentifier(credentials=token), scores.scores, DivingFishProvider()))
            update_tasks.append(task)
        if token := os.getenv("LXNS_PERSONAL_TOKEN"):
            task = asyncio.create_task(maimai.updates(PlayerIdentifier(credentials=token), scores.scores, LXNSProvider()))
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
