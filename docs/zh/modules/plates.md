# 牌子

## maimai.plates() 方法

获取玩家牌子

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`、`ArcadeProvider`。

### 参数

| 参数名     | 类型               | 说明                                                          |
|------------|--------------------|-------------------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(friend_code=664994421382429)` |
| plate      | `str`              | 牌子名称，例如 "樱将", "真舞舞"                                |
| provider   | `IScoreProvider`   | 数据源，默认为 `LXNSProvider`                                  |

### 返回值

`MaimaiPlates` 对象

### 异常

| 错误名称                       | 描述                                  |
|--------------------------------|-------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到 |
| `InvalidPlateError`            | 提供的牌子名称无效                    |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效            |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据      |
| `RequestError`                 | 由于网络问题导致请求失败              |

## MaimaiPlates 对象

### 属性

| 字段      | 类型          | 说明                         |
|-----------|---------------|----------------------------|
| `scores`  | `list[Score]` | 与当前牌子名称相关的所有成绩 |
| `songs`   | `list[Song]`  | 与当前牌子名称相关的所有歌曲 |
| `version` | `str`         | 牌子的版本，例如 "真", "舞"   |
| `kind`    | `str`         | 牌子的种类，例如 "将", "神"   |

### 方法

```python
@cached_property
def no_remaster(self) -> bool:
    """获取该牌子是否需要游玩 ReMASTER 难度。

    只有 舞 和 霸 牌子需要游玩 ReMASTER 难度。
    """

@cached_property
def remained(self) -> list[PlateObject]:
    """获取玩家在该牌子上剩余的歌曲和成绩。

    如果玩家在某歌曲上还有剩余的难度未完成，那么这首歌曲和剩余难度的 `level_index` 将被包含在结果中。

    如果玩家有成绩，未达成要求的成绩将被包含在结果中，已经达到要求的成绩则不会包含进来。
    """

@cached_property
def cleared(self) -> list[PlateObject]:
    """获取玩家在该牌子上已达成的歌曲和成绩。

    如果玩家在某歌曲上有一个或多个难度满足要求，那么这首歌曲和已完成难度的 `level_index` 将被包含在结果中，否则不会。

    如果玩家有成绩，已经达到要求的成绩将被包含在结果中，未达到要求的成绩则不会包含进来。
    """

@cached_property
def played(self) -> list[PlateObject]:
    """获取玩家在该牌子上游玩过的歌曲和成绩。

    如果玩家曾经玩过一首歌曲的任何难度，无论是否满足要求，那么这首歌曲和玩过的 `level_index` 将被包含在结果中。

    所有的成绩都将被包含在结果中。
    """

@cached_property
def all(self) -> list[PlateObject]:
    """获取该牌子上的所有歌曲，通常用于查询牌子信息。

    所有相关的歌曲都将被包含在结果中，包含所有难度。

    结果中不会包含成绩，请使用 `played`, `cleared`, `remained` 属性来获取玩家成绩。
    """

@cached_property
def played_num(self) -> int:
    """获取该牌子上已玩难度的数量。"""

@cached_property
def cleared_num(self) -> int:
    """获取该牌子上已达成难度的数量。"""

@cached_property
def remained_num(self) -> int:
    """获取该牌子上剩余难度的数量。"""

@cached_property
def all_num(self) -> int:
    """获取该牌子上所有难度的数量。

    这个牌子上所有难度的总数，应该等于 `cleared_num + remained_num`。
    """
```