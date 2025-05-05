# 核心概念

在 maimai.py 中，我们使用了一种较为规范的方式定义了方法和接口的调用方式。

与 `RESTful` 规范类似，如果您能理解我们的规范，便可以直接使用符合直觉的方式进行开发，而不必过多阅读文档和API。

## 异步

在 maimai.py 中，所有方法和接口都需要通过 `MaimaiClient` 进行**异步**的调用，类似下面的形式。

```python
from maimai_py.maimai import MaimaiClient, MaimaiSongs

client: MaimaiClient = MaimaiClient()
songs: MaimaiSongs = await client.songs()
```

针对密集IO类应用，异步可以提供较大的开发优势，在不影响可读性的情况下避免阻塞，**maimai.py仅支持异步**。

我们尚未有提供同步调度的开发计划，如果您有使用上的困难，请联系我们，我们将尽可能为您提供帮助。

::: tip
您可以在整个应用程序中共用 `MaimaiClient` 实例，也可以在每次请求中创建新的实例。
:::

## 封装对象

上文提到过的 `MaimaiSongs` 是一个封装对象，与直接返回 `list[Song]` 相比，封装对象为您提供了一些方便的方法。

例如，您可以直接调用 `songs.by_title()` 等方法直接进行筛选，如果需要，您也可以通过 `songs.songs` 访问原始列表。

我们针对大多数数据都进行了封装（`MaimaiSongs`, `MaimaiScores`, `MaimaiPlates`），读者可以自行查看预置的方法。

由于封装对象的灵活性，我们设计了基于封装对象的缓存机制，从而避免多次请求谱面信息等数据。关于缓存机制与缓存刷新等内容，请查阅 [缓存策略](./caches.md) 章节。

## 数据源

在 maimai.py 中，我们引入了数据源的概念，进而支持了以通用的方式从多个位置获取或者上传数据。

::: info
截止目前，我们已经支持水鱼、落雪、微信服务号、舞萌机台等数据源，支持向水鱼和落雪提交数据。
:::

您可以在调用方法时用 `provider` 参数，来指示从何处获取数据，例如：

```python
from maimai_py.maimai import MaimaiClient

client = MaimaiClient()
lxns = LXNSProvider(developer_token="your_lxns_developer_token")
divingfish = DivingFishProvider()

# 使用落雪作为数据源
player_lxns = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 使用水鱼作为数据源
player_diving = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
```

我们推荐您使用全局变量来储存数据源实例，这样只需要提供一次 `developer_token` 就可以了。

## 玩家标识

在获取或上传玩家信息时，往往需要标识玩家的身份，我们使用 `PlayerIdentifier` 实例来作为标识符。

`PlayerIdentifier` 是一个通用的概念，您需要根据使用场景传入合适的值，例如：

- 落雪没有 `username` 这个概念，所以在使用落雪作为数据源时，传入 `username` 会抛出异常。
- 上传分数到水鱼时使用用户名和密码：`PlayerIdentitifer(username="Username", credentials="Password")`。
- 上传分数到水鱼时使用Import-Token：`PlayerIdentitifer(credentials="Import-Token")`。
- 使用机台作为数据源时，`credentials` 就是玩家加密后的userId，您可以保存并复用。

## 曲目ID

在本查分器中，同一首曲目的标准、DX 谱面、宴会谱面的 曲目ID 一致，不存在大于 10000 的 曲目ID（如有，均会对 10000 / 100000 取余处理）。

例如，Oshama Scramble! 的标准、DX、宴会谱面的 曲目ID 均为 363。

## 下一步

至此，您已经了解了 maimai.py 的全部核心概念。

- 您已经具备了基于 maimai.py 开发舞萌相关项目的能力，可以开始旅程了。
- 如果想要更进一步详细了解我们的功能，可以继续阅读文档。
- 对于有经验的开发者，也可以直接[阅读API文档](https://api.maimai.turou.fun/maimai_py)。