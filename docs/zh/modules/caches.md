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
# 当然，你也可以通过提供 flush 参数来强制刷新缓存
# 因为默认数据源已经被覆写，将选用数据源(DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(flush=True)
```

## 缓存刷新

maimai.py 不会自动刷新缓存，第一种刷新的方法上文已经提到，即通过指定 flush 参数来强制刷新缓存。

```python
songs = await maimai.songs()
await asyncio.sleep(86400) # 模拟一天后
songs = await maimai.songs(flush=True)
```

对于多种类型的数据，逐一调用方法是很麻烦的，因此 maimai.py 提供了 `flush` 方法来刷新所有缓存数据。

```python
songs = await maimai.songs()
nameplates = await maimai.items(PlayerNameplates)()
await asyncio.sleep(86400) # 模拟一天后
await maimai.flush() # 刷新所有缓存数据
```

## 性能建议

您没有必要频繁刷新缓存，通常来说，只需要在每天的固定时间刷新一下缓存即可。

如果您正在开发Web应用，我们建议您用类似下面的方式来使用 maimai.py：

```python
from fastapi import FastAPI
import asyncio
from maimai import MaimaiClient, DivingFishProvider

app = FastAPI()
maimai = MaimaiClient()

@app.on_event("startup")
async def startup_event():
    maimai_songs = await maimai.songs()
    my_scheduler = asyncio.create_task(daily_flush()) # 在每天固定时间调用 flush

@app.get("/songs/list", response_model=list[Song])
async def get_songs():
    return await maimai.songs() # 这里会从缓存中获取数据，不会造成额外的请求
```

::: info
关于 Web 应用的更多信息，请参考我们的内置 Web 实现 [api.py](https://github.com/TrueRou/maimai.py/blob/main/maimai_py/api.py)
:::