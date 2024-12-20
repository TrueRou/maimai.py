# maimai.py

maimai.py 是一个用于舞萌相关开发的工具库，封装了常用函数和模型，便于开发者调用。

我们的关键功能与特性:

- **模型通用**: 提供了基于MaimaiJP标准的数据模型，打破不同数据源之间术语混乱的屏障。
- **功能全面**: 功能多样，覆盖了爬取、查询、上传等多个功能。对于歌曲、玩家信息、玩家分数、Rating、姓名框、牌子进度等数据都有支持。
- **使用简单**: 例如 `maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)` 即可获取 turou 在水鱼的所有分数。
- **文档详细**: 提供了用户友好的说明文档，也提供了完备的API文档。框架内代码提示规范，可以直接在IDE中即时查阅参数说明。
- **高技术力**: 支持联动微信 OpenID 获取玩家分数, 解析分数HTML, 并上传至数据源
- **机台支持✨**: 支持通过玩家二维码从机台获取玩家成绩，玩家ID全程加密，强大且安全

可以在这里访问我们的API文档: https://maimai-py.pages.dev/.

## 使用方式

```bash
pip install maimai-py
```

升级方式:

```bash
pip install -U maimai-py
```

## 示例

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