# maimai.py ([文档](https://maimai.turou.fun/zh/))

[![PyPI version](https://img.shields.io/pypi/v/maimai-py)](https://pypi.org/project/maimai-py/)
![License](https://img.shields.io/pypi/l/maimai-py)
![Python versions](https://img.shields.io/pypi/pyversions/maimai-py)
[![en](https://img.shields.io/badge/README-en-red.svg)](https://github.com/TrueRou/maimai.py/blob/main/README.md)

用于国服舞萌相关开发的最佳Python工具库, 封装水鱼/落雪查分器常用函数.

提供了基于日服舞萌标准的数据模型和接口, 为水鱼和落雪分别做了数据源实现.

支持从数据源查询歌曲、谱面、玩家信息、分数、Rating、姓名框、牌子进度.

另外, 支持联动微信 OpenID 获取玩家分数, 解析分数HTML, 并上传至数据源

## 使用方式

```bash
pip install maimai-py
```

升级方式:

```bash
pip install -U maimai-py
```

更多内容请查看文档: https://maimai.turou.fun/zh/.

## 快速开始

```python
import asyncio
from maimai_py import MaimaiClient, MaimaiPlates, MaimaiScores, MaimaiSongs, PlayerIdentifier, LXNSProvider, DivingFishProvider


async def quick_start():
    maimai = MaimaiClient()
    divingfish = DivingFishProvider(developer_token="")

    # 获取所有歌曲及其元数据
    songs: MaimaiSongs = await maimai.songs()
    # 获取水鱼查分器用户 turou 的分数 (默认获取 b50 分数)
    scores: MaimaiScores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    # 获取水鱼查分器用户 turou 的舞将牌子信息
    plates: MaimaiPlates = await maimai.plates(PlayerIdentifier(username="turou"), "舞将", provider=divingfish)

    song = songs.by_id(1231)  # 生命不詳 by 蜂屋ななし

    print(f"歌曲 1231 是: {song.artist} - {song.title}")
    print(f"TuRou 的 Rating 为: {scores.rating}, b15 中最高 Rating 为: {scores.scores_b15[0].dx_rating}")
    print(f"TuRou 的 舞将 完成度: {plates.cleared_num}/{plates.all_num}")

asyncio.run(quick_start())
```

## 异步

maimai.py 默认采用全异步, 且暂时没有提供同步方法和接口的计划.

如果您不希望采用异步, 可以使用 `asyncio.run` 包裹方法, 将异步方法同步调用.