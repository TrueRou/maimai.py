# 分数

## maimai.scores() 方法

从数据源获取玩家的成绩。

对于 `WechatProvider` 和 `ArcadeProvider`，玩家标识必须具有 `credentials` 属性。具体做法可以阅读对应数据源的文档。

**支持的数据源**：`DivingFishProvider`、`WechatProvider`、`ArcadeProvider`、`LXNSProvider`

### 参数

| 参数名     | 类型               | 说明                                                          |
|------------|--------------------|-------------------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| kind       | `ScoreKind`        | 分数列表类型，默认为 `ScoreKind.BEST`                          |
| provider   | `IScoreProvider`   | 数据源，默认为 `LXNSProvider`                                  |

### 返回值

`MaimaiScores` 对象

### 异常

| 错误名称                       | 描述                                  |
|--------------------------------|-------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到 |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效            |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据      |
| `RequestError`                 | 由于网络问题导致请求失败              |

只有使用 `ArcadeProvider` 才可能触发的异常:

| 错误名称           | 描述                                      |
|--------------------|-----------------------------------------|
| `TitleServerError` | 舞萌标题服务器的相关错误，可能是网络问题   |
| `ArcadeError`      | 舞萌 Response 非法，或者提供的玩家标识有误 |

## maimai.updates() 方法

更新玩家的分数到指定的数据源。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`

### 参数

| 参数名     | 类型               | 说明                                                          |
|------------|--------------------|-------------------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| scores     | `list[Score]`      | 分数列表，通常是从其他数据源获取的分数                         |
| provider   | `IScoreProvider`   | 数据源，默认为 `LXNSProvider`                                  |

### 返回值

- 无返回值，失败时会抛出异常。

### 异常

| 异常名称                       | 描述                                                              |
|--------------------------------|-----------------------------------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到，或者 Import-Token/密码 无效 |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效                                        |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据                                  |
| `RequestError`                 | 由于网络问题导致请求失败                                          |

## MaimaiScores 对象

### 属性

| 字段          | 类型           | 说明                                                               |
|---------------|----------------|------------------------------------------------------------------|
| `scores`      | `list[Score]`  | 玩家所有成绩，当 `ScoreKind.ALL` 时返回所有成绩，否则仅返回 B50 成绩 |
| `scores_b35`  | `list[Score]`  | 玩家 B35 成绩                                                      |
| `scores_b15`  | `list[Score]`  | 玩家 B15 成绩                                                      |
| `rating`      | `int`          | 玩家 总 Rating                                                     |
| `rating_b35`  | `int`          | 玩家 B35 Rating                                                    |
| `rating_b15`  | `int`          | 玩家 B15 Rating                                                    |
| `as_distinct` | `MaimaiScores` | 对成绩进行去重，只保留最佳的那一个成绩。                             |

### 方法

```python
def by_song(self, song_id: int, song_type: SongType = None, level_index: LevelIndex = None) -> list[Score]:
    """获取指定歌曲在某歌曲类型和难度下面所有的成绩。

    如果未提供 `song_type` 或 `level_index`，则将返回该歌曲的所有分数。

    参数:
        song_id: 要获取成绩的歌曲ID。
        song_type: 筛选的谱面类型, 默认为 None.
        level_index: 筛选的难度, 默认为 None.
    返回:
        歌曲的成绩列表，如果没有找到成绩则返回空列表。
    """

def filter(self, **kwargs) -> list[Score]:
    """根据属性筛选成绩。

    请确保属性存在，并且类型匹配。所有条件通过 AND 连接。

    参数:
        kwargs: 用于筛选成绩的属性。
    返回:
        符合所有条件的成绩列表，如果没有找到成绩则返回空列表。
    """
```