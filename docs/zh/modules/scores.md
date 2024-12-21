# 玩家分数

## maimai.scores() 方法

从数据源获取玩家的成绩。

对于`WechatProvider`，`PlayerIdentifier`必须具有credentials属性，我们建议您使用`maimai.wechat()`方法来获取玩家标识符。同时，不应缓存`PlayerIdentifier`或将其存储在数据库中，因为`cookies`可能随时会过期。

对于`ArcadeProvider`，`PlayerIdentifier`必须具有credentials属性，这是玩家加密后的userId，可以从`maimai.qrcode()`中获得。credentials可以重复使用，因为它不会过期，同时，userId是加密的，不能在 maimai.py 之外的任何其他情况下使用。

**支持的数据源**：`DivingFishProvider`、`WechatProvider`、`ArcadeProvider`、`LXNSProvider`

### 参数

| 参数名 | 类型 | 说明 |
|-|-|-|
| identifier | PlayerIdentifier | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| kind | ScoreKind | 分数列表类型，默认为 `ScoreKind.BEST` |
| provider | IScoreProvider | 数据源，默认为 `LXNSProvider` |

### 返回值

`MaimaiScores` 对象

### 异常

| 错误名称                           | 描述                                                         |
|-----------------------------------|--------------------------------------------------------------|
| InvalidPlayerIdentifierError       | 玩家标识符对于数据源无效，或者玩家未找到                     |
| InvalidDeveloperTokenError         | 开发者令牌未提供或令牌无效                                  |
| PrivacyLimitationError            | 用户尚未接受第三方访问数据                                   |
| ArcadeError                       | 仅适用于ArcadeProvider，由于舞萌机台问题导致请求失败         |
| RequestError                      | 由于网络问题导致请求失败                                   |

## maimai.updates() 方法

更新玩家的分数到指定的数据源。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`

### 参数

| 参数名   | 类型               | 说明                                                         |
|----------|--------------------|--------------------------------------------------------------|
| identifier | `PlayerIdentifier` | 要更新分数的玩家标识符，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| scores   | `list[Score]`      | 要更新的分数，通常是从其他提供者获取的分数                     |
| provider | `IScoreProvider`   | 数据源，默认为 `LXNSProvider`                                 |

### 返回值

- 无返回值，失败时会抛出异常。

### 异常

| 异常名称                         | 描述                                                         |
|---------------------------------|--------------------------------------------------------------|
| `InvalidPlayerIdentifierError`   | 玩家标识符对于数据源无效，或者玩家未找到，或者导入令牌/密码无效 |
| `InvalidDeveloperTokenError`     | 开发者令牌未提供或令牌无效                                  |
| `PrivacyLimitationError`        | 用户尚未接受第三方访问数据                                   |
| `RequestError`                  | 由于网络问题导致请求失败                                   |

## MaimaiScores 对象

### 属性

| 字段     | 类型             | 说明                                                                |
|-----------------|------------------|---------------------------------------------------------------------|
| `scores`        | `list[Score]`     | 玩家所有成绩，当 `ScoreKind.ALL` 时返回所有成绩，否则仅返回 B50 成绩 |
| `scores_b35`    | `list[Score]`     | 玩家 B35 成绩                                                     |
| `scores_b15`    | `list[Score]`     | 玩家 B15 成绩                                                     |
| `rating`        | `int`             | 玩家总rating                                                  |
| `rating_b35`    | `int`             | 玩家 B35 的rating                                             |
| `rating_b15`    | `int`             | 玩家 B15  的rating                                            |
| `as_distinct`   | `MaimaiScores`| 获取去重后的最佳成绩。通常情况下，玩家对同一首歌和难度会有多个成绩，调用此方法将返回一个新的 `MaimaiScores` 对象，只包含每首歌和难度的最高成绩 |

### 方法

```python
def by_song(self, song_id: int) -> list[Score]:
    """获取指定歌曲的所有难度成绩。

    如果 `ScoreKind` 是 `BEST`，则只会筛选 b50 成绩。

    参数:
        song_id: 要获取成绩的歌曲ID。
    返回:
        歌曲的成绩列表，如果没有找到成绩则返回空列表。
    """

def by_level(self, song_id: int, level_index: LevelIndex) -> Score | None:
    """根据歌曲和难度索引获取成绩。

    如果 `ScoreKind` 是 `BEST`，则只会筛选 b50 成绩。

    参数:
        song_id: 要获取成绩的歌曲ID。
        level_index: 要获取成绩的难度索引。
    返回:
        如果存在成绩则返回成绩，否则返回 None。
    """

def filter(self, **kwargs) -> list[Score]:
    """根据属性筛选成绩。

    确保属性是成绩的属性，值是相同类型的。所有条件通过 AND 连接。

    如果 `ScoreKind` 是 `BEST`，则只会筛选 b50 成绩。

    参数:
        kwargs: 用于筛选成绩的属性。
    返回:
        符合所有条件的成绩列表，如果没有找到成绩则返回空列表。
    """
```