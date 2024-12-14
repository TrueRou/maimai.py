import asyncio
import logging
import os
import threading

from mitmproxy.master import Master
from mitmproxy.options import Options
from mitmproxy.addons import default_addons

from examples.proxy_updater.config import config
from examples.proxy_updater.proxy import WechatWahlapAddon
from examples.proxy_updater.updater import generate_url


class MitmMaster(Master):
    def _asyncio_exception_handler(self, loop, context):
        exc: Exception = context["exception"]
        logging.exception(exc)
        return super()._asyncio_exception_handler(loop, context)


async def run_proxy_async():
    master = MitmMaster(Options())
    master.addons.add(*default_addons())
    master.addons.add(WechatWahlapAddon())
    master.options.update(listen_host=config["listen_host"], listen_port=config["listen_port"])
    await master.run()


def run_console_blocked():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\033[32mHTTPProxy Running on {config["listen_host"]}:{config["listen_port"]}.\033[0m")
    while True:
        input("\033[33mPress Enter to generate the Wechat URL, or Ctrl+C to exit.\n\033[0m")
        os.system("cls" if os.name == "nt" else "clear")
        asyncio.run(generate_url())


if __name__ == "__main__":
    threading.Thread(target=run_console_blocked).start()
    asyncio.run(run_proxy_async())
