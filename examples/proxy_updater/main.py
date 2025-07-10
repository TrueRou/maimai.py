import asyncio
import logging
import os
import threading

from mitmproxy.addons import default_addons
from mitmproxy.master import Master
from mitmproxy.options import Options

from proxy_updater.proxy import WechatWahlapAddon
from proxy_updater.updater import generate_url

listen_host = os.getenv("LISTEN_HOST", "0.0.0.0")
listen_port = int(os.getenv("LISTEN_PORT", 8080))


class MitmMaster(Master):
    def _asyncio_exception_handler(self, loop, context):
        exc: Exception = context["exception"]
        logging.exception(exc)
        return super()._asyncio_exception_handler(loop, context)


async def run_proxy_async():
    master = MitmMaster(Options())
    master.addons.add(*default_addons())
    master.addons.add(WechatWahlapAddon())
    master.options.update(listen_host=listen_host, listen_port=listen_port)
    await master.run()


def run_console_blocked():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"\033[32mHTTPProxy Running on {listen_host}:{listen_port}.\033[0m")
    while True:
        input("\033[33mPress Enter to generate the Wechat URL, or Ctrl+C to exit.\n\033[0m")
        os.system("cls" if os.name == "nt" else "clear")
        asyncio.run(generate_url())


if __name__ == "__main__":
    threading.Thread(target=run_console_blocked).start()
    asyncio.run(run_proxy_async())
