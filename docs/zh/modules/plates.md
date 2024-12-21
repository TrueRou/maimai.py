# 玩家徽章成就

## maimai.plates() 方法

获取给定玩家和徽章的成就。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`。

### 参数

| 参数名 | 类型 | 说明 |
|-|-|-|
| identifier | PlayerIdentifier | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| plate | str | 徽章名称，例如 "樱将", "真舞舞" |
| provider | IScoreProvider | 数据源，默认为 `LXNSProvider` |

### 返回值

`MaimaiPlates` 对象

### 异常

| 错误名称                           | 描述                                                         |
|-----------------------------------|--------------------------------------------------------------|
| InvalidPlayerIdentifierError       | 玩家标识符对于数据源无效，或者玩家未找到。                     |
| InvalidPlateError                 | 提供的版本或徽章无效。                                       |
| InvalidDeveloperTokenError         | 开发者令牌未提供或令牌无效。                                  |
| PrivacyLimitationError            | 用户尚未接受第三方访问数据。                                   |
| RequestError                      | 由于网络问题导致请求失败。                                   |

## MaimaiPlates 对象

### 属性

| 字段     | 类型             | 说明                                                                |
|-----------------|------------------|---------------------------------------------------------------------|
| `scores`        | `list[Score]`     | 匹配徽章版本和种类的成绩。                                                     |
| `songs`         | `list[Song]`      | 匹配徽章版本和种类的歌曲。                                                     |
| `version`       | `str`             | 徽章的版本，例如 "真", "舞"。                                               |
| `kind`          | `str`             | 徽章的种类，例如 "将", "神"。                                               |

### 方法

```python
@cached_property
def no_remaster(self) -> bool:
    """是否需要在徽章中玩 ReMASTER 等级。

    只有 舞 和 霸 徽章需要 ReMASTER 等级，其他不需要。
    """

@cached_property
def remained(self) -> list[PlateObject]:
    """获取玩家在该徽章上剩余的歌曲。

    如果玩家在一首歌曲上还有剩余的等级，那么这首歌曲和剩余的 `levels_index` 将被包含在结果中，否则不会。

    没有满足徽章要求的不同的分数将被包含在结果中，完成的分数不会。
    """

@cached_property
def cleared(self) -> list[PlateObject]:
    """获取玩家在该徽章上已通关的歌曲。

    如果玩家在一首歌曲上有一个或多个等级满足要求，那么这首歌曲和通关的 `level_index` 将被包含在结果中，否则不会。

    满足徽章要求的不同分数将被包含在结果中，未完成的分数不会。
    """

@cached_property
def played(self) -> list[PlateObject]:
    """获取玩家在该徽章上已玩的歌曲。

    如果玩家曾经玩过一首歌曲的等级，无论是否满足要求，那么这首歌曲和已玩的 `levels_index` 将被包含在结果中。

    所有不同的分数都将被包含在结果中。
    """

@cached_property
def all(self) -> list[PlateObject]:
    """获取该徽章上的所有歌曲，通常用于徽章的统计。

    所有歌曲都将被包含在结果中，包含所有等级，无论是否满足要求。

    结果中不会包含分数，使用 played, cleared, remained 来获取分数。
    """

@cached_property
def played_num(self) -> int:
    """获取该徽章上已玩等级的数量。"""

@cached_property
def cleared_num(self) -> int:
    """获取该徽章上已通关等级的数量。"""

@cached_property
def remained_num(self) -> int:
    """获取该徽章上剩余等级的数量。"""

@cached_property
def all_num(self) -> int:
    """获取该徽章上所有等级的数量。

    这个徽章上所有等级的总数，应该等于 `cleared_num + remained_num`。
    """
```