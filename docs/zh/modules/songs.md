# 歌曲

## maimai.songs() 方法

从数据源获取所有歌曲。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`。

### 参数

| 参数名         | 类型             | 说明                                                  |
|----------------|------------------|-----------------------------------------------------|
| flush          | `bool`           | 是否刷新缓存，默认为 `False`                           |
| provider       | `ISongProvider`  | 覆写默认数据源，默认为 `LXNSProvider`                  |
| alias_provider | `IAliasProvider` | 覆写默认别名数据源，默认为 `YuzuProvider`              |
| curve_provider | `ICurveProvider` | 覆写默认相对难度曲线数据源，默认为`DivingFishProvider` |

### 返回值

`MaimaiSongs` 对象

### 异常

| 错误名称       | 描述                     |
|----------------|------------------------|
| `RequestError` | 由于网络问题导致请求失败 |

## MaimaiSongs 对象

### 属性

| 字段    | 类型         | 说明           |
|---------|--------------|--------------|
| `songs` | `list[Song]` | 所有歌曲的列表 |

### 方法

```python
def by_id(self, id: int) -> Song | None:
    """通过曲目ID获取歌曲。

    参数:
        id: 歌曲的ID，总是小于 `10000` (如果大于的话应该 `% 10000`)。
    返回:
        如果存在则返回歌曲，否则返回 None。
    """

def by_title(self, title: str) -> Song | None:
    """通过曲名获取歌曲。

    参数:
        title: 歌曲的标题。
    返回:
        如果存在则返回歌曲，否则返回 None。
    """

def by_alias(self, alias: str) -> Song | None:
    """通过别名获取歌曲。

    参数:
        alias: 歌曲的其中一个的别名。
    返回:
        如果存在则返回歌曲，否则返回 None。
    """

def by_artist(self, artist: str) -> list[Song]:
    """通过艺术家获取歌曲，区分大小写。

    参数:
        artist: 歌曲的艺术家。
    返回:
        匹配艺术家的歌曲列表，如果没有找到则返回空列表。
    """

def by_genre(self, genre: str) -> list[Song]:
    """通过流派获取歌曲，区分大小写。

    参数:
        genre: 歌曲的流派。
    返回:
        匹配流派的歌曲列表，如果没有找到则返回空列表。
    """

def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
    """通过BPM获取歌曲。

    参数:
        minimum: 最小（包含）BPM的歌曲。
        maximum: 最大（包含）BPM的歌曲。
    返回:
        匹配BPM范围的歌曲列表，如果没有找到则返回空列表。
    """

def by_versions(self, versions: Version) -> list[Song]:
    """通过版本获取歌曲，版本是模糊匹配的大版本更新，例如，`24000` 会匹配舞萌2024的所有曲目。

    参数:
        versions: 歌曲的版本。
    返回:
        匹配版本的歌曲列表，如果没有找到则返回空列表。
    """

def by_keywords(self, keywords: str) -> list[Song]:
    """通过关键词获取歌曲，关键词会匹配歌曲标题、艺术家和别名。

    参数:
        keywords: 用于匹配歌曲的关键词。
    返回:
        匹配关键词的歌曲列表，如果没有找到则返回空列表。
    """

def filter(self, **kwargs) -> list[Song]:
    """根据属性筛选歌曲。

    请确保属性存在，并且类型匹配。所有条件通过 AND 连接。

    参数:
        kwargs: 用于筛选歌曲的属性。
    返回:
        匹配所有条件的歌曲列表，如果没有找到则返回空列表。
    """
```
