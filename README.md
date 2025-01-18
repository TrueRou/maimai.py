# maimai.py ([documentation](https://maimai.turou.fun))

[![PyPI version](https://img.shields.io/pypi/v/maimai-py)](https://pypi.org/project/maimai-py/)
![License](https://img.shields.io/pypi/l/maimai-py)
![Python versions](https://img.shields.io/pypi/pyversions/maimai-py)
[![zh](https://img.shields.io/badge/README-中文-green.svg)](https://github.com/TrueRou/maimai.py/blob/main/README_CN.md)

<p align="center">
  <a href="https://maimai.turou.fun">
      <img src="https://s2.loli.net/2024/12/23/7T5nbMfzdAi8BtF.png" alt="maimai.py" />
  </a>
</p>

The definitive python wrapper for MaimaiCN related development, wrapping the frequently used methods from DivingFish and LXNS.

We provide data models and methods based on MaiMai standard, and make implementation for both DivingFish and LXNS.

Support querying songs, player information, scores, ratings, name plates from any data sources.

In addition, we support getting player scores with WeChat OpenID, parsing the score HTML, and uploading it to the data sources.

## Installation

```bash
pip install maimai-py
```

To upgrade:

```bash
pip install -U maimai-py
```

For more, read the docs: https://maimai.turou.fun/.

Additionally, you can [download the maimai.py client](https://github.com/TrueRou/maimai.py/releases) and develop using any programming language.

## Quickstart

```python
import asyncio
from maimai_py import MaimaiClient, MaimaiPlates, MaimaiScores, MaimaiSongs, PlayerIdentifier, LXNSProvider, DivingFishProvider


async def quick_start():
    maimai = MaimaiClient()
    divingfish = DivingFishProvider(developer_token="")

    # fetch all songs and their metadata
    songs: MaimaiSongs = await maimai.songs()
    # fetch divingfish user turou's scores (b50 scores by default)
    scores: MaimaiScores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    # fetch divingfish user turou's 舞将 plate information
    plates: MaimaiPlates = await maimai.plates(PlayerIdentifier(username="turou"), "舞将", provider=divingfish)

    song = songs.by_id(1231)  # 生命不詳 by 蜂屋ななし

    print(f"Song 1231: {song.artist} - {song.title}")
    print(f"TuRou's rating: {scores.rating}, b15 top rating: {scores.scores_b15[0].dx_rating}")
    print(f"TuRou's 舞将: {plates.cleared_num}/{plates.all_num} cleared")

asyncio.run(quick_start())
```

## Async

maimai.py is fully asynchronous by default, and there are no plans to provide synchronous methods.

If you don't want to be asynchronous, you can use the `asyncio.run` wrapper to call asynchronous methods synchronously.

## Client

maimai.py provides a RESTful API client, which you can call maimai.py features via HTTP requests from any language.

The client is compiled using Nuitka, please download it from the [Releases](https://github.com/TrueRou/maimai.py/releases) page.

Our client supports Windows and Linux, please download the corresponding version according to your system.

For the client API documentation, please see: https://openapi.maimai.turou.fun/.