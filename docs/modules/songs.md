# 曲目

## maimai.songs() 方法

通过 [`maimai.songs()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.songs) 方法可以获取曲目的封装对象，以 `MaimaiSongs` 的形式返回。

调用后，默认会从 LXNSProvider 获取歌曲，并且从 YuzuProvider 获取别名。如果您需要拟合难度，可以通过 `curve_provider` 参数传入一个实现了 `ICurveProvider` 接口的对象，默认只有 `DivingFishProvider` 提供了相对难度曲线数据。

阅读 [MaimaiSongs 定义](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiSongs)，可以了解通过各种条件筛选曲目、获取单个曲目、遍历曲目等方法。

### 通过 ID 或者别名获取曲目

很容易想到的，maimai.py 的单个曲目可能包含 SD、DX、宴会等不同版本的谱面，maimai.py 通过 `Song` 对象来封装这些曲目。

```python
songs = await maimai.songs(provider=divingfish, curve_provider=divingfish)
song1 = await songs.by_id(1231)
song2 = await songs.by_alias("不知死活")

print(song1.title)  # 输出: 生命不詳
print(song1.difficulties.dx[3].note_designer) # 输出: はっぴー
assert song1.difficulties.dx[3].curve is not None
assert song1.difficulties.dx[3].curve.sample_size > 10000
print(song2.id == song1.id)  # 输出: True
```

::: warning
同样的，曲目 ID 遵循：同一首曲目的标准、DX 谱面、宴会谱面的 曲目ID 一致，不存在大于 10000 的 曲目ID（如有，均会对 10000 / 100000 取余处理）。

如果您对此有疑问，请参考 [开始 章节](../get-started.md#曲目id)。
:::

在上述例子中，通过 `song.difficulties` 可以获取 `SongDifficulties` 对象，包含了所有谱面的难度信息。例如： `song.difficulties.dx` 是 DX 谱面的难度列表。

这种封装方式可能对您动态的获取曲目难度造成困扰，所以我们为 [`Song`](../concepts/models.md#song) 对象提供了一些工具方法：

| 方法名                                    | 返回值                 | 说明                           |
|-------------------------------------------|------------------------|------------------------------|
| `get_difficulty(SongType, LevelIndex)`    | `SongDifficulty`       | 获取对应的难度                 |
| `get_difficulties(SongType)`              | `list[SongDifficulty]` | 获取对应的难度列表             |
| `get_divingfish_id(SongType, LevelIndex)` | `int`                  | 获取歌曲对应难度的 水鱼ID      |
| `get_divingfish_ids(SongType)`            | `set[int]`             | 获取歌曲对应类型的 水鱼ID 集合 |

通过工具方法，您可以轻松获取曲目的难度信息，如果需要的话，还可以解析为对应的水鱼ID。

## MaimaiSongs 对象

`MaimaiSongs` 对象提供了多种方法来获取和过滤歌曲。以下是一些常用的方法：

```python
async def get_all(self) -> list[Song]:
    """
    获取所有歌曲，以列表返回。

    此方法将遍历缓存中的所有歌曲，并逐一生成每首歌曲。除非您确实需要遍历所有歌曲，否则应使用 `by_id` 或 `filter` 方法代替。

    返回值:
        一个列表，包含缓存中的所有歌曲。
    """

async def get_batch(self, ids: list[int]) -> list[Song]:
    """
    通过 ID 列表批量获取歌曲。

    参数:
        ids: 歌曲的 ID 列表。
    返回值:
        一个列表，包含所有找到的歌曲。如果没有找到任何歌曲，则返回空列表。
    """

async def by_id(self, id: int) -> Song | None:
    """
    通过 ID 获取歌曲。

    参数:
        id: 歌曲的 ID，始终小于 `10000`，如有必要应使用 (`% 10000`)。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_title(self, title: str) -> Song | None:
    """
    通过标题获取歌曲。

    参数:
        title: 歌曲的标题。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_alias(self, alias: str) -> Song | None:
    """
    通过可能的别名获取歌曲。

    参数:
        alias: 歌曲的一个可能别名。
    返回值:
        如果歌曲存在则返回歌曲，否则返回 None。
    """

async def by_artist(self, artist: str) -> list[Song]:
    """
    通过艺术家获取歌曲，区分大小写。

    参数:
        artist: 歌曲的艺术家。
    返回值:
        一个列表，包含与艺术家匹配的所有歌曲。
    """

async def by_genre(self, genre: Genre) -> list[Song]:
    """
    通过流派获取歌曲，区分大小写。

    参数:
        genre: 歌曲的流派。
    返回值:
        一个列表，包含与流派匹配的所有歌曲。
    """

async def by_bpm(self, minimum: int, maximum: int) -> list[Song]:
    """
    通过 BPM 获取歌曲。

    参数:
        minimum: 歌曲的最小（包含）BPM。
        maximum: 歌曲的最大（包含）BPM。
    返回值:
        一个列表，包含 BPM 在指定范围内的所有歌曲。
    """

async def by_versions(self, versions: Version) -> list[Song]:
    """
    通过版本获取歌曲，版本是 maimai 主要版本的模糊匹配版本。

    参数:
        versions: 歌曲的版本。
    返回值:
        一个列表，包含与版本匹配的所有歌曲。
    """

async def by_keywords(self, keywords: str) -> list[Song]:
    """
    通过关键词获取歌曲，关键词与歌曲标题、艺术家和别名匹配。

    参数:
        keywords: 用于匹配歌曲的关键词。
    返回值:
        一个列表，包含与关键词匹配的所有歌曲。
    """

async def filter(self, **kwargs) -> list[Song]:
    """
    通过属性过滤歌曲。

    确保属性是歌曲的属性，并且值是相同类型的。所有条件通过 AND 连接。

    参数:
        kwargs: 用于过滤歌曲的属性。
    返回值:
        一个列表，包含所有匹配条件的歌曲。
    """
```