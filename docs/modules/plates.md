# 牌子

这里我们提到的牌子，指的是版本姓名框。版本姓名框是一种对应游戏版本，在对应版本全曲达到相应条件才能获得的姓名框。因为获取难度较高，版本姓名框通常被视为玩家实力与精力的象征。

![image.png](https://s2.loli.net/2025/07/09/7JF4HLwEczqBhkV.png)

## maimai.plates() 方法

在 maimai.py 中，[`maimai.plates()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.plates) 方法用于获取玩家在特定牌子上的成绩和歌曲信息。该方法返回一个 [`MaimaiPlates`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiPlates) 对象，提供了多种方法来查询玩家在该牌子上的成绩和歌曲。

根据牌子不同的达成状态，`MaimaiPlates` 对象提供了以下方法：

- `get/count_remained()`：获取玩家在该牌子上剩余的歌曲和成绩。
- `get/count_cleared()`：获取玩家在该牌子上已达成的歌曲和成绩。
- `get/count_played()`：获取玩家在该牌子上游玩过的歌曲和成绩。
- `get/count_all()`：获取该牌子上的所有歌曲和成绩。

这些 `get` 方法的返回值是一个列表，包含了 `PlateObject` 对象，每个对象代表一首歌曲及其相关成绩和难度，具体结构可以参考 [PlateObject 模型](../concepts/models.md#plateobject)。

::: info
**注意**：如果你想要获取广义的姓名框 NamePlate，请使用 `maimai.items(PlayerNamePlate)` 方法。
:::

很容易想到的，`maimai.plates()` 是 `maimai.scores()` 的一个特例，专门用于处理牌子相关的成绩查询，对于 Provider 和 PlayerIdentifier 的处理方式与 `maimai.scores()` 类似，参考 [分数 章节](./scores.md) 了解更多细节。

### 获取桃将完成度

```python
my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "桃将", provider=lxns)
cleared_num = await my_plate.count_cleared()
remained_num = await my_plate.count_remained()
percentage = cleared_num / (cleared_num + remained_num) * 100
print(f"桃将完成度: {percentage:.2f}%，已完成 {cleared_num} 难度，剩余 {remained_num} 难度")
```

### 获取舞将剩余的所有成绩

```python
my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "舞将", provider=lxns)
remained_obj = await my_plate.get_remained()
for plate_obj in remained_obj:
    print(f"歌曲: {plate_obj.song.title}")
    for score in plate_obj.scores:
        print(f"  - 难度: {score.level_index}, 分数: {score.rate.name}")
```

### 绘制牌子完成情况图表

```python
async def draw_plate_completion(plate: MaimaiPlates):
    import matplotlib.pyplot as plt

    plt.rcParams["font.family"] = ["Hei", "Arial", "Helvetica", "Times New Roman"]

    # 获取已完成和剩余的成绩
    cleared = await plate.get_cleared()
    remained = await plate.get_remained()

    # 准备数据
    cleared_names = [obj.song.title for obj in cleared]
    cleared_levels = [sum(score.level_index.value for score in obj.scores) for obj in cleared]
    remained_names = [obj.song.title for obj in remained]
    remained_levels = [sum(score.level_index.value for score in obj.scores) for obj in remained]

    # 绘制图表
    plt.bar(cleared_names, cleared_levels, label="已完成", color="green")
    plt.bar(remained_names, remained_levels, label="剩余", color="red", bottom=cleared_levels)

    plt.xlabel("歌曲")
    plt.ylabel("难度等级")
    plt.title(f"桃将 完成情况")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "桃将", provider=lxns)
await draw_plate_completion(my_plate)
```

### 补充说明

关于何种成绩和难度会被包含在 `PlateObject` 中，可以参考以下方法的文档：

```python
@dataclass
class PlateObject:
    song: Song
    levels: set[LevelIndex]
    scores: list[ScoreExtend]

async def get_remained(self) -> list[PlateObject]:
    """
    获取玩家在该牌子上剩余的歌曲和成绩。

    如果玩家在某歌曲上还有剩余的难度未完成，那么这首歌曲和剩余难度的 `level_index` 将被包含在结果中。

    如果玩家有成绩，未达成要求的成绩将被包含在结果中，已经达到要求的成绩则不会包含进来。
    """

async def get_cleared(self) -> list[PlateObject]:
    """
    获取玩家在该牌子上已达成的歌曲和成绩。

    如果玩家在某歌曲上有一个或多个难度满足要求，那么这首歌曲和已完成难度的 `level_index` 将被包含在结果中，否则不会。

    如果玩家有成绩，已经达到要求的成绩将被包含在结果中，未达到要求的成绩则不会包含进来。
    """

async def get_played(self) -> list[PlateObject]:
    """
    获取玩家在该牌子上游玩过的歌曲和成绩。

    如果玩家曾经玩过一首歌曲的任何难度，无论是否满足要求，那么这首歌曲和玩过的 `level_index` 将被包含在结果中。

    所有的成绩都将被包含在结果中。
    """

async def get_all(self) -> list[PlateObject]:
    """
    获取该牌子上的所有歌曲和成绩，通常用于牌子的整体统计。

    所有歌曲都将被包含在结果中，包括已玩过的 `level_index`，无论是否达成要求。

    所有不同的成绩都将被包含在结果中。
    """
```