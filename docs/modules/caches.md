# 缓存策略

## 缓存策略

在当前版本的 maimai.py 中，共有 9 类数据会被缓存，如下表所示。

| 参数名       | 说明     | 缓存场景                                 | 默认缓存数据源       |
|--------------|--------|--------------------------------------|----------------------|
| `songs`      | 曲目     | 获取曲目列表或获取分数时依赖曲目信息     | `LXNSProvider`       |
| `aliases`    | 曲目别名 | 获取曲目列表或获取分数时依赖曲目信息     | `YuzuProvider`       |
| `curves`     | 曲目拟合 | 获取曲目列表或获取分数时依赖曲目信息     | `DivingFishProvider` |
| `icons`      | 头像     | 获取头像列表或获取分数时依赖头像         | `LXNSProvider`       |
| `nameplates` | 姓名框   | 获取姓名框列表或获取分数时依赖姓名框     | `LXNSProvider`       |
| `frames`     | 背景     | 获取背景列表或获取分数时依赖背景         | `LXNSProvider`       |
| `trophies`   | 称号     | 获取称号列表或获取分数时依赖称号         | `LocalProvider`      |
| `charas`     | 旅行伙伴 | 获取旅行伙伴列表或获取分数时依赖旅行伙伴 | `LocalProvider`      |
| `partners`   | 搭档     | 获取搭档列表或获取分数时依赖搭档         | `LocalProvider`      |

当遇到缓存场景时，会先检查缓存是否存在，如果存在则直接返回缓存数据，否则会向数据源请求数据并缓存。

需要注意的是，当对默认数据源进行覆写时，会使用您主动指定的数据源刷新缓存，同时替换默认数据源。

因此，您可以通过主动调用方法来手动指定数据源，并且提前将数据进行缓存，例如：

```python
# 第一次获取分数，被动缓存曲目信息，选用默认缓存数据源(LXNSProvider, YuzuProvider, DivingFishProvider)
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 再获取一次分数，因为曲目信息已经被缓存，所以不会再次请求曲目信息
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 手动获取曲目信息，因为覆写了Provider，将进行主动缓存刷新，选用数据源(DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())
# 再获取一次分数，因为曲目信息已经被缓存，所以不会再次请求曲目信息
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 再获取一次曲目信息，因为曲目信息已经被缓存，所以不会再次请求曲目信息
songs = await maimai.songs()
```

## 缓存刷新

maimai.py 的缓存遵循生存周期，默认的生存周期为24小时，您可以通过 `MaimaiClient` 的 `cache_ttl` 参数来设置缓存的生存周期。

如果您需要手动刷新缓存，可以通过获取 `MaimaiClient` 的 `_cache` 属性来获取缓存对象，并调用 `clear` 方法来清除缓存。

然而，我们不推荐您主动调用 `clear` 方法，如果您在开发Web应用，这可能会导致没有关闭的连接无法找到缓存资源。


## 性能建议

如果您正在开发Web应用，我们建议您用类似下面的方式来使用 maimai.py：

```python
from fastapi import FastAPI
import asyncio
from maimai import MaimaiClient, DivingFishProvider

app = FastAPI()
maimai = MaimaiClient()

@app.get("/songs/list", response_model=list[Song])
async def get_songs():
    return await maimai.songs() # 这里会从缓存中按需加载数据，不会造成额外的请求和性能损失
```

创建 `MaimaiSongs` 不会引入额外的性能损失，因为所有的曲目信息都已经被缓存，并且只有在需要的时候才会被加载。

::: info
关于 Web 应用的更多信息，请参考我们的内置 Web 实现 [api.py](https://github.com/TrueRou/maimai.py/blob/main/maimai_py/api.py)
:::