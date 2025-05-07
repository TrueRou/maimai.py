# 歌曲

## maimai.songs() 方法

从数据源获取所有歌曲。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`。

### 参数

| 参数名         | 类型             | 说明                                                  |
|----------------|------------------|-----------------------------------------------------|
| provider       | `ISongProvider`  | 覆写默认数据源，默认为 `LXNSProvider`                  |
| alias_provider | `IAliasProvider` | 覆写默认别名数据源，默认为 `YuzuProvider`              |
| curve_provider | `ICurveProvider` | 覆写默认相对难度曲线数据源，默认为`DivingFishProvider` |

### 返回值

`MaimaiSongs` 对象

### 异常

| 错误名称          | 描述                     |
|-------------------|------------------------|
| `httpx.HTTPError` | 由于网络问题导致请求失败 |

## MaimaiSongs 对象

```python
async def iter_songs(self) -> AsyncGenerator[Song, None]:
    """所有歌曲作为异步生成器。

    此方法将遍历缓存中的所有歌曲，并逐一生成每首歌曲。除非您确实需要遍历所有歌曲，否则应使用 `by_id` 或 `filter` 方法代替。

    返回值:
        一个异步生成器，生成缓存中的所有歌曲。
    """

async def by_id(self, id: int) -> Song | None:
    """通过 ID 获取歌曲。

    参数:
        id: 歌曲的 ID，始终小于 `10000`，如有必要应使用 (`% 10000`)。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_title(self, title: str) -> Song | None:
    """通过标题获取歌曲。

    参数:
        title: 歌曲的标题。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_alias(self, alias: str) -> Song | None:
    """通过可能的别名获取歌曲。

    参数:
        alias: 歌曲的一个可能别名。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_artist(self, artist: str) -> AsyncGenerator[Song, None]:
    """通过艺术家获取歌曲，区分大小写。

    参数:
        artist: 歌曲的艺术家。
    返回值:
        一个异步生成器，生成与艺术家匹配的歌曲。
    """

async def by_genre(self, genre: Genre) -> AsyncGenerator[Song, None]:
    """通过流派获取歌曲，区分大小写。

    参数:
        genre: 歌曲的流派。
    返回值:
        一个异步生成器，生成与流派匹配的歌曲。
    """

async def by_bpm(self, minimum: int, maximum: int) -> AsyncGenerator[Song, None]:
    """通过 BPM 获取歌曲。

    参数:
        minimum: 歌曲的最小（包含）BPM。
        maximum: 歌曲的最大（包含）BPM。
    返回值:
        一个异步生成器，生成与 BPM 匹配的歌曲。
    """

async def by_versions(self, versions: Version) -> AsyncGenerator[Song, None]:
    """通过版本获取歌曲，版本是 maimai 主要版本的模糊匹配版本。

    参数:
        versions: 歌曲的版本。
    返回值:
        一个异步生成器，生成与版本匹配的歌曲。
    """

async def by_keywords(self, keywords: str) -> AsyncGenerator[Song, None]:
    """通过关键词获取歌曲，关键词与歌曲标题、艺术家和别名匹配。

    参数:
        keywords: 用于匹配歌曲的关键词。
    返回值:
        一个异步生成器，生成与关键词匹配的歌曲。
    """

async def filter(self, **kwargs) -> AsyncGenerator[Song, None]:
    """通过属性过滤歌曲。

    确保属性是歌曲的属性，并且值是相同类型的。所有条件通过 AND 连接。

    参数:
        kwargs: 用于过滤歌曲的属性。
    返回值:
        一个异步生成器，生成满足所有条件的歌曲。
    """
```

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.songs
- https://api.maimai.turou.fun/maimai_py/maimai#MaimaiSongs
