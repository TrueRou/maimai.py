# 分数

## maimai.scores() 方法

从数据源获取玩家的所有成绩。

对于 `WechatProvider` 和 `ArcadeProvider`，玩家标识必须具有 `credentials` 属性。具体可以阅读对应数据源的文档。

**支持的数据源**：`DivingFishProvider`、`WechatProvider`、`ArcadeProvider`、`LXNSProvider`

### 参数

| 参数名     | 类型               | 说明                                                          |
|------------|--------------------|-------------------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| provider   | `IScoreProvider`   | 数据源，默认为 `LXNSProvider`                                  |

### 返回值

`MaimaiScores` 对象

### 异常

| 错误名称                       | 描述                                  |
|--------------------------------|-------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到 |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效            |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据      |
| `httpx.HTTPError`              | 由于网络问题导致请求失败              |

只有使用 `ArcadeProvider` 才可能触发的异常:

| 错误名称                  | 描述                                           |
|---------------------------|----------------------------------------------|
| `TitleServerNetworkError` | 舞萌 官方服务器相关错误，可能是网络问题         |
| `TitleServerBlockedError` | 舞萌 官方服务器拒绝了请求，可能是因为 IP 被过滤 |
| `ArcadeIdentifierError`   | 舞萌 用户 ID 无效，或者用户未找到               |

## maimai.updates() 方法

更新玩家的分数到指定的数据源。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`

### 参数

| 参数名     | 类型                   | 说明                                                          |
|------------|------------------------|-------------------------------------------------------------|
| identifier | `PlayerIdentifier`     | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| scores     | `list[Score]`          | 分数列表，通常是从其他数据源获取的分数                         |
| provider   | `IScoreUpdateProvider` | 数据源，默认为 `LXNSProvider`                                  |

### 返回值

无返回值，失败时会抛出异常。

### 异常

| 异常名称                       | 描述                                                              |
|--------------------------------|-----------------------------------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到，或者 Import-Token/密码 无效 |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效                                        |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据                                  |
| `httpx.HTTPError`              | 由于网络问题导致请求失败                                          |

## MaimaiScores 对象

| 字段         | 类型          | 说明                                                               |
|--------------|---------------|------------------------------------------------------------------|
| `scores`     | `list[Score]` | 玩家所有成绩，当 `ScoreKind.ALL` 时返回所有成绩，否则仅返回 B50 成绩 |
| `scores_b35` | `list[Score]` | 玩家 B35 成绩                                                      |
| `scores_b15` | `list[Score]` | 玩家 B15 成绩                                                      |
| `rating`     | `int`         | 玩家 总 Rating                                                     |
| `rating_b35` | `int`         | 玩家 B35 Rating                                                    |
| `rating_b15` | `int`         | 玩家 B15 Rating                                                    |

```python
async def configure(self, scores: list[Score]) -> "MaimaiScores":
    """通过分数列表初始化分数对象。
    
    此方法将根据分数的 dx_rating、dx_score 和 achievements 进行排序，并将其分为 b35 和 b15 分数。
    
    参数:
        scores: 要初始化的分数列表。
    返回值:
        初始化后的 MaimaiScores 对象。
    """

async def get_distinct(self) -> "MaimaiScores":
    """获取去重后的分数。

    通常情况下，玩家在同一首歌曲和难度上会有多个分数记录，此方法会返回一个新的 `MaimaiScores` 对象，
    其中包含每首歌曲和难度的最高分数。

    此方法不会修改原始分数对象，而是返回一个新对象。

    返回值:
        包含去重分数的新 `MaimaiScores` 对象。
    """

async def get_scores(self) -> list[tuple[Song, SongDifficulty, Score]]:
    """获取所有分数及其对应的歌曲信息。

    此方法将返回一个元组列表，每个元组包含一首歌曲、其对应的难度和分数。

    如果找不到歌曲或难度，相应的元组将从结果中排除。

    返回值:
        一个元组列表，每个元组包含（歌曲、难度、分数）。
    """

def by_song(
    self, song_id: int, song_type: Union[SongType, _UnsetSentinel] = UNSET, level_index: Union[LevelIndex, _UnsetSentinel] = UNSET
) -> list[Score]:
    """获取指定歌曲 ID、类型和难度等级的分数。

    如果未提供 song_type 或 level_index，则不会按该属性进行过滤。

    参数:
        song_id: 要获取分数的歌曲 ID。
        song_type: 要获取分数的歌曲类型，默认为 None。
        level_index: 要获取分数的难度等级，默认为 None。
    返回值:
        匹配歌曲 ID、类型和难度等级的分数列表。如果找不到分数，将返回空列表。
    """

def filter(self, **kwargs) -> list[Score]:
    """根据属性过滤分数。

    确保属性是分数对象的属性，且值的类型与属性类型一致。所有条件通过 AND 连接。

    参数:
        kwargs: 用于过滤分数的属性。
    返回值:
        符合所有条件的分数列表。
    """
```

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.scores
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.updates
- https://api.maimai.turou.fun/maimai_py/maimai#MaimaiScores