import json
import os
from pathlib import Path


config_path = Path(__file__).parent / "config.json"
proxy_path = Path(__file__).parent / "proxy.yaml"

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

default_proxy_rules = """
mixed-port: 7890
mode: rule
log-level: info

proxies:
  - name: maimai.py
    server: 127.0.0.1
    port: 8080
    type: http
    
rules:
  - DOMAIN,tgk-wcaime.wahlap.com,maimai.py
  - MATCH,DIRECT
"""

if not proxy_path.exists():
    proxy_path.write_text(default_proxy_rules, encoding="utf-8")
    print("Proxy rules file created, please import it into your Clash.")
if not config_path.exists():
    config_path.write_text(json.dumps(default_config, indent=4, ensure_ascii=False), encoding="utf-8")
    print("Config file created. Please configure it and restart the proxy.")
    os._exit(0)

config = json.loads(config_path.read_text(encoding="utf-8"))
