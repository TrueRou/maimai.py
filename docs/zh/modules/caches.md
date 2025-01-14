# 缓存策略

## 缓存策略

在当前版本的 maimai.py 中，共有 9 类数据会被缓存，如下表所示。

| 参数名       | 说明     | 主动缓存场景     | 被动缓存场景           | 默认缓存数据源  |
|--------------|--------|------------|------------------|-----------------|
| `songs`      | 曲目     | 获取曲目列表     | 获取分数时依赖曲目信息 | `LXNSProvider`  |
| `aliases`    | 曲目别名 | 获取曲目列表     | 获取分数时依赖曲目信息 | `None(不获取)`  |
| `curves`     | 曲目拟合 | 获取曲目列表     | 获取分数时依赖曲目信息 | `None(不获取)`  |
| `icons`      | 头像     | 获取头像列表     | 获取分数时依赖头像     | `LXNSProvider`  |
| `nameplates` | 姓名框   | 获取姓名框列表   | 获取分数时依赖姓名框   | `LXNSProvider`  |
| `frames`     | 背景     | 获取背景列表     | 获取分数时依赖背景     | `LXNSProvider`  |
| `trophies`   | 称号     | 获取称号列表     | 获取分数时依赖称号     | `LocalProvider` |
| `charas`     | 旅行伙伴 | 获取旅行伙伴列表 | 获取分数时依赖旅行伙伴 | `LocalProvider` |
| `partners`   | 搭档     | 获取搭档列表     | 获取分数时依赖搭档     | `LocalProvider` |

当遇到缓存场景时，会先检查缓存是否存在，如果存在则直接返回缓存数据，否则会向数据源请求数据并缓存。

需要注意的是，当主动缓存场景触发时，会使用您主动指定的数据源进行缓存，同时替换默认数据源。

因此，您可以通过调用主动缓存方法来手动指定数据源，并且提前将数据进行缓存，例如：

```python
# 第一次获取分数，被动缓存曲目信息，选用默认缓存数据源(LXNSProvider, None, None)
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 再获取一次分数，因为曲目信息已经被缓存，所以不会再次请求曲目信息
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 手动获取曲目信息，触发主动缓存场景，选用数据源(DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())
# 再获取一次分数，因为曲目信息已经被缓存，所以不会再次请求曲目信息，但是此时的曲目信息包含了曲目别名和曲目拟合信息
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
```

## 缓存刷新

maimai.py 不会自动刷新缓存，但是您可以通过调用 `flush` 方法来手动刷新缓存，例如：

```python
# 手动获取曲目信息，触发主动缓存场景，选用数据源(DivingFishProvider, YuzuProvider, DivingFishProvider)
songs = await maimai.songs(provider=DivingFishProvider())

# 假设每天刷新一次缓存
async def daily_flush():
    while True:
        await maimai.flush()
        await asyncio.sleep(86400)

# 启动异步调度器
asyncio.create_task(daily_flush())
```

`flush` 方法会检查所有当前已缓存的数据，如果数据源支持刷新操作，则会调用数据源的刷新方法。

## 性能建议

请尽量减少主动缓存场景的触发次数，因为主动缓存场景会导致数据源请求数据并缓存，而数据源请求数据是一个耗时操作。

通常来说，只需要在程序启动时手动缓存一下，并且在每天的固定时间刷新一下缓存即可。

如果您正在开发Web应用，我们建议您用类似下面的方式来使用 maimai.py：

```python
from fastapi import FastAPI
import asyncio
from maimai import Maimai, DivingFishProvider

app = FastAPI()
maimai = Maimai()
maimai_songs = None # 单例对象，获取一次，到处使用

@app.on_event("startup")
async def startup_event():
    maimai_songs = await maimai.songs(provider=DivingFishProvider())
    my_scheduler = asyncio.create_task(daily_flush()) # 在每天固定时间调用 flush

@app.get("/songs/list", response_model=list[Song])
async def get_songs():
    return maimai_songs.songs # 省略了数据模型转换
```

## maimai.flush() 方法

刷新所有缓存数据，这是一个耗时的操作，不建议频繁调用。

只有 "songs", "aliases", "curves", "icons", "plates", "frames", "trophy", "chara", "partner" 这 9 类数据会被刷新。

### 参数

无参数

### 返回值

无返回值