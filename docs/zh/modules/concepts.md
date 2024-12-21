# 核心概念

在 maimai.py 中，我们使用了一种较为规范的方式定义了方法和接口的调用方式。

与 `RESTful` 规范类似，如果您能理解我们的规范，便可以直接使用符合直觉的方式进行开发，而不必过多阅读文档和API。

## 调用接口

在 maimai.py 中，所有方法和接口都需要通过 `MaimaiClient` 进行**异步**的调用，类似下面的形式。

```python
from maimai_py.maimai import MaimaiClient, MaimaiSongs

client: MaimaiClient = MaimaiClient()
songs: MaimaiSongs = await client.songs()
```

这里 `await client.songs()` 返回了一个封装过的 `MaimaiSongs`，与直接返回 `list[Song]` 相比，封装实例可以提供一些方便的方法。

例如，您可以直接调用 `songs.by_title()` 等方法直接进行筛选，如果需要，您也可以通过 `songs.songs` 访问原始列表。

我们针对大多数数据都进行了封装（`MaimaiSongs`, `MaimaiScores`, `MaimaiPlates`），读者可以自行查看预置的方法。

> 您可以在整个应用程序中共用 `MaimaiClient` 实例，也可以在每次请求中创建新的实例。

## 提供数据源

在 maimai.py 中，大部分方法都离不开 **“从某处 获取/提交 数据”** 的逻辑，我们将目标位置称为**数据源(Provider)**。

> 截止目前，我们已经支持水鱼、落雪、微信服务号、舞萌机台等数据源，支持向水鱼和落雪提交数据。

您可以在调用方法时传入 `provider` 参数，来提示框架从何处获取数据，例如：

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

## 提供玩家标识

在获取或上传玩家信息时，往往需要标识玩家的身份，我们使用 `PlayerIdentifier` 实例来作为标识符。

`PlayerIdentifier` 是一个通用的概念，您需要根据使用场景传入合适的值，例如：

- 落雪没有 `username` 这个概念，所以在使用落雪作为数据源时，传入 `username` 会抛出异常。
- 上传分数到水鱼时使用用户名和密码：`PlayerIdentitifer(username="Username", credentials="Password")`。
- 上传分数到水鱼时使用Import-Token：`PlayerIdentitifer(credentials="Import-Token")`。
- 使用机台作为数据源时，`credentials` 就是玩家加密后的userId，您可以保存并复用。

## 下一步

至此，您已经了解了 maimai.py 的全部核心概念。

- 您已经具备了基于 maimai.py 开发舞萌相关项目的能力，可以开始旅程了。
- 如果想要更进一步详细了解我们的功能，可以继续阅读文档。
- 对于有经验的开发者，也可以直接[阅读API文档](https://maimai-py.pages.dev/maimai_py)。