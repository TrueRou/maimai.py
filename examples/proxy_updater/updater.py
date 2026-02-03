import asyncio
import os
import traceback
import typing

from httpx import ConnectError, ReadTimeout

from maimai_py import DivingFishProvider, LXNSProvider, MaimaiClient, PlayerIdentifier, WechatProvider
from maimai_py.exceptions import InvalidPlayerIdentifierError, InvalidWechatTokenError, PrivacyLimitationError
from maimai_py.maimai import MaimaiClientMultithreading
from maimai_py.models import WechatPlayer

diving_provider = DivingFishProvider()
lxns_provider = LXNSProvider()


async def generate_url():
    threaded_maimai = MaimaiClientMultithreading(timeout=300)
    url = await threaded_maimai.wechat()
    print("\033[32mPlease visit the following URL in Wechat to authorize: \033[0m")
    print(url)


async def update_prober(r: str, t: str, code: str, state: str):
    try:
        maimai = MaimaiClient(timeout=300)
        print("\033[32mProber updating was triggered.\033[0m")
        # fetch the player's scores from Wahlap Wechat OffiAccount
        wx_player = await maimai.wechat(r, t, code, state)
        assert isinstance(wx_player, PlayerIdentifier)
        print("\033[32mPlayer fetched successfully.\033[0m")
        scores = await maimai.scores(wx_player, WechatProvider())
        records = await maimai.records(wx_player, WechatProvider())
        print("\033[32mScores fetched successfully.\033[0m")
        # print player information as debug message
        player = typing.cast(WechatPlayer, await maimai.players(wx_player, WechatProvider()))
        print(f"\033[32mPlayer: {player.name} ({player.rating})\033[0m")
        # establish the tasks of updating the prober according to the configuration
        update_tasks = []
        if token := os.getenv("DIVINGFISH_IMPORT_TOKEN"):
            task = asyncio.create_task(
                maimai.updates(PlayerIdentifier(credentials=token), scores.scores, DivingFishProvider())
            )
            update_tasks.append(task)
        if token := os.getenv("LXNS_PERSONAL_TOKEN"):
            task1 = asyncio.create_task(maimai.updates(PlayerIdentifier(credentials=token), records, LXNSProvider()))
            task2 = asyncio.create_task(
                maimai.updates(PlayerIdentifier(credentials=token), scores.scores, LXNSProvider())
            )
            update_tasks.append(task1)
            update_tasks.append(task2)
        asyncio.gather(*update_tasks)
        print("\033[32mProber updated successfully.\033[0m")
    except (ConnectError, ReadTimeout):
        print("\033[31mConnection to the server timed out.\033[0m")
    except (InvalidPlayerIdentifierError, PrivacyLimitationError, InvalidWechatTokenError) as e:
        print(f"\033[31m{e}.\033[0m")
    except Exception:
        traceback.print_exc()
        print("\033[31mAn unexpected error occurred.\033[0m")
