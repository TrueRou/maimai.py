import asyncio
import json
import os
from pathlib import Path
import threading
from typing import Any, Callable, Self

from mitmproxy.addons import default_addons, script
from mitmproxy.master import Master
from mitmproxy.options import Options

from examples.proxy_updater.proxy import WechatWahlapAddon


# https://stackoverflow.com/questions/51893788/using-mitmproxy-inside-python-script
class ThreadedMitmProxy(threading.Thread):
    def __init__(self, user_addon: Callable, **options: Any) -> None:
        self.loop = asyncio.new_event_loop()
        self.master = Master(Options(), event_loop=self.loop)
        # replace the ScriptLoader with the user addon
        self.master.addons.add(*(user_addon() if isinstance(addon, script.ScriptLoader) else addon for addon in default_addons()))
        # set the options after the addons since some options depend on addons
        self.master.options.update(**options)
        super().__init__()

    def run(self) -> None:
        self.loop.run_until_complete(self.master.run())

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, *_) -> None:
        self.master.shutdown()
        self.join()


default_config = {
    "listen_host": "0.0.0.0",
    "listen_port": 8080,
    "diving_fish": {
        "enabled": True,
        "username": "",
        "credentials": "",
    },
    "lxns": {
        "enabled": True,
        "friend_code": 0,
        "developer_token": "",
    },
}

if __name__ == "__main__":
    if (Path(__file__).parent / "config.json").exists():
        with ThreadedMitmProxy(WechatWahlapAddon, listen_host="0.0.0.0", listen_port=8080):
            os.system("cls" if os.name == "nt" else "clear")
            print("\033[32mHTTPProxy Running on 0.0.0.0:8080.\033[0m")
            input("\033[31mPress any key to shutdown.\033[0m")
    else:
        (Path(__file__).parent / "config.json").write_text(json.dumps(default_config, indent=4, ensure_ascii=False), encoding="utf-8")
        print("Config file created. Please configure it before running the proxy.")
