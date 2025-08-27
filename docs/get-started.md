# 开始

安装方式：

```bash
pip install maimai-py
```

升级方式：

```bash
pip install -U maimai-py
```

## 什么是 maimai.py？

maimai.py 是一个用于舞萌相关开发的 `Python` 工具库，封装了常用函数和模型，便于开发者调用。

基于 **maimai でらっくす** 日服的标准数据模型，maimai.py 提供了一个通用的接口，旨在简化舞萌相关数据的获取、查询和更新。

通过标准的数据模型，maimai.py 解决了不同数据源之间术语混乱的问题，使得开发者可以更专注于业务逻辑，而不是数据处理。

下面是一个最基本的示例：

```python
import asyncio
from maimai_py import MaimaiClient, MaimaiPlates, MaimaiScores, MaimaiSongs, PlayerIdentifier, LXNSProvider, DivingFishProvider

maimai = MaimaiClient() # 全局创建 MaimaiClient 实例
divingfish = DivingFishProvider(developer_token="your_token_here")
lxns = LXNSProvider(developer_token="your_token_here")

async def main():
    # 获取水鱼查分器用户 turou 的成绩
    scores: MaimaiScores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    # 将成绩更新到落雪查分器账户 664994421382429
    await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
```

上面的示例展示了 maimai.py 的两个核心功能：

- **查询与更新**：使用 `maimai.scores()` 方法从**源数据源**获取成绩，并使用 `maimai.updates()` 方法将成绩更新到**目标数据源**。
- **统一的数据模型**：即使水鱼和落雪的 Score 结构不同，使用 maimai.py 也可以轻松处理。

你可能已经有了些疑问。先别急，在后续的文档中我们会详细介绍每一个细节。

## 数据源

上文的实例中，我们多次提到了**数据源**（Provider）的概念。数据源指示从何处获取数据或者更新数据。

在 maimai.py 中，大多数方法都可以传入一个 `provider` 参数来指定数据源。

下面是一个使用示例：

```python
from maimai_py import MaimaiClient, DivingFishProvider, MaimaiSongs, PlayerIdentifier

client = MaimaiClient()
divingfish = DivingFishProvider(developer_token="your_token_here")

async def main():
    # 从水鱼查分器获取用户 turou 的玩家信息
    player = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
    # 获取所有歌曲及其元数据 （因为未提供数据源，默认选择了落雪数据源来缓存歌曲信息）
    songs: MaimaiSongs = await maimai.songs()
```

::: info
截止目前，我们已经支持水鱼、落雪、微信服务号、机台✨等数据源，支持向水鱼和落雪更新数据。

通过从 **机台✨** 数据源获取玩家成绩，然后更新到水鱼或落雪，你可以实现查分器的成绩同步。
:::

## 封装对象

你可能注意到了上文的 `MaimaiSongs` 对象，与直接返回 `list[Song]` 相比，封装对象为你提供了一些方便的方法。

例如，你可以直接调用 `by_title()`、`by_id()` 方法进行筛选，也可以通过 `get_all()` 获取整个歌曲列表。

我们针对大多数数据都进行了封装（`MaimaiSongs`, `MaimaiScores`, `MaimaiPlates`），读者可以通过代码提示了解更多。

## 缓存与异步

由于封装对象的灵活性，我们设计了基于封装对象的缓存机制，从而避免多次请求歌曲信息等数据。

在 maimai.py 中，许多数据（例如歌曲信息）支持缓存机制，默认情况下会直接保存在内存中，缓存 24 小时。

缓存的读写依赖于单例模式的 `MaimaiClient` 实例，因此我们建议在全局范围内只创建一个 `MaimaiClient` 实例。

```python
from maimai_py import MaimaiClient, MaimaiSongs, MaimaiScores

# ✅ 全局创建一个 MaimaiClient 实例, 避免缓存失效
maimai = MaimaiClient()

async def main():
    songs: MaimaiSongs = await maimai.songs() # 填充缓存
    songs: MaimaiSongs = await maimai.songs() # 命中缓存
    scores: MaimaiScores = await maimai.scores(...) # 被动使用缓存
```

::: danger
务必在全局只创建一个 `MaimaiClient` 实例，避免缓存失效。
:::

关于缓存机制与缓存刷新的更多细节，请查阅[缓存策略](./concepts/caches.md)章节。

## 玩家标识

在获取或上传玩家信息时，往往需要标识玩家的身份，我们使用 `PlayerIdentifier` 实例来作为标识符。

`PlayerIdentifier` 是一个通用的概念，你需要根据使用场景传入合适的值，阅读对应 Provider 的章节可以了解更多关于如何使用 `PlayerIdentifier` 的信息：

- [DivingFishProvider](./providers/divingfish.md)
- [LXNSProvider](./providers/lxns.md)
- [ArcadeProvider](./providers/arcade.md)
- [WeChatProvider](./providers/wechat.md)

## 曲目 ID

在 maimai.py 中，同一首曲目的标准、DX 谱面、宴会谱面的**曲目 ID** 一致，不存在大于 10000 的曲目 ID（如有，均会对 10000 / 100000 取余处理）。
宴会场**成绩**为例外，宴会场**成绩 ID** 可能会大于 100000。

例如，针对 Oshama Scramble! 而言：

- 标准、DX、宴会谱面的 曲目 ID 均为 363
- 标准、DX、宴会成绩的 成绩 ID 分别为 363、363、100363。

> 通常来说，你不需要关心**成绩 ID**，因为 maimai.py 在大多数场景下基于**曲目 ID**。
> 
> 如果你需要将成绩关联到曲目，可以直接使用 [`scores.get_mapping()`](./modules/scores.md#遍历成绩对象) 方法。

## 下一步

至此，你已经了解了 maimai.py 的全部核心概念。

- 如果你想要更进一步详细了解我们的功能：推荐阅读[功能章节](./modules/songs.md)。
- 如果你是经验丰富的开发者，想要了解更多细节：推荐阅读 [API 文档](https://api.maimai.turou.fun/maimai_py)。
- `Talk is cheap. Show me the code`：推荐阅读[例子章节](.//examples.md)。

如果你希望通过其他语言调用 maimai.py 的功能，请参考 [RESTful 客户端](./concepts/client.md)。

