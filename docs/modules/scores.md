# 成绩

在一次游玩后，玩家当次游戏的达成率与评级会显示于画面中央，也会显示与历史最好成绩的差距。若当次游戏的达成率超过历史最好成绩，将会提示达成新记录（NEW RECORD）。

在 maimai.py 中，我们提供了获取玩家 BEST50 成绩、所有成绩的方法，以及更新玩家成绩到指定数据源的功能。

::: info
注意：与其他查分器相似地，我们仅能查询到您在曲目游玩的最终成绩，而无法查询到您在游玩过程中每个阶段的成绩。

例如：针对 Oshama Scramble! 的 DX MASTER 谱面，如果您先后达成了 100.0000% FC 和 100.5000% 非 FC 成绩，maimai.py 将返回 100.5000% FC 的成绩。
:::

## maimai.scores() 方法

调用 [`maimai.scores()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.scores) 方法可以获取对应玩家在指定数据源的所有成绩，以 [`MaimaiScores`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiScores) 的形式返回。

MaimaiScores 封装了多个方法，您可以通过这些方法获取玩家的 BEST50 成绩，遍历所有成绩，计算总 Rating 等：

| 字段 / 方法             | 类型 / 返回值                              | 说明                                   |
|-------------------------|--------------------------------------------|--------------------------------------|
| `scores`                | `list[ScoreExtend]`                        | 玩家所有成绩                           |
| `scores_b35`            | `list[ScoreExtend]`                        | 玩家 B35 成绩                          |
| `scores_b15`            | `list[ScoreExtend]`                        | 玩家 B15 成绩                          |
| `rating`                | `int`                                      | 玩家 总 Rating                         |
| `rating_b35`            | `int`                                      | 玩家 B35 Rating                        |
| `rating_b15`            | `int`                                      | 玩家 B15 Rating                        |
| `configure(...)`        | `MaimaiScores`                             | 手动填充并初始化 MaimaiScores 对象     |
| `get_mapping()`         | `list[tuple[Song, SongDifficulty, Score]]` | 获取一个 曲目 + 难度 + 成绩 的映射元组 |
| `by_song(...)`          | `list[Score]`                              | 获取指定细分条件下的分数列表           |
| `get_player_bests(...)` | `PlayerBests`                              | 直接转换为玩家的 BEST 成绩对象         |

其中 `configure(...)` 和 `get_mapping()` 会在下文的例子中详细介绍。

### 示例代码

#### 获取玩家在水鱼的所有成绩

```python
divingfish = DivingFishProvider(developer_token="your_token_here")
my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
score = my_scores.by_song(1231, level_index=LevelIndex.MASTER)[0]
print("兔肉在 生命不詳(1231) MASTER 的 达成度:", score.achievement)

sssp_count = len([s for s in my_scores.scores if s.rate == RateType.SSSP])
sss_count = len([s for s in my_scores.scores if s.rate == RateType.SSS])
all_count = sssp_count + sss_count
percentage = sssp_count / all_count if all_count > 0 else 0
print(f"兔肉的 鸟加 / 总鸟 比例: {sssp_count} / {all_count} = {percentage:.2%}, 总 Rating: {my_scores.rating}")")
```

#### 遍历成绩对象

时常会遇到需要遍历所有成绩，并且需要携带关联的元数据的情况，maimai.py 提供了 `get_mapping()` 方法来简化这一过程。

```python
divingfish = DivingFishProvider(developer_token="your_token_here")
my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
for song, diff, score in await my_scores.get_mapping():
    print(f"曲目: {song.name}, 难度: {diff.type}, 等级: {score.rate}, 达成度: {score.achievement}")
```

结合下文的 `maimai.bests()` 方法，您可以轻松获取玩家的 BEST50 成绩，并使用 Pillow 等库生成成绩预览图。

::: info
如果您不需要携带关联的元数据，可以直接使用 `my_scores.scores` 来获取成绩列表。

在使用 `maimai.updates()` 方法更新查分器时，就可以直接传入 `my_scores.scores` 列表。
:::

## maimai.bests() 方法

上文的 `maimai.scores()` 方法可以获取玩家的所有成绩，但如果您只关心玩家的 BEST50 成绩，可以使用 [`maimai.bests()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.bests) 方法。

使用 `maimai.bests()` 方法只会获取必要的成绩资源，尽量节约请求时间和对查分器的压力。同样的，返回值也是一个 [`MaimaiScores`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiScores) 对象，但只包含玩家的 50 个成绩。

::: info
如果您查询的数据源没有原生提供 BEST50 成绩的接口，maimai.py 会获取所有成绩并自动筛选出 BEST50 成绩。
:::

## maimai.minfo() 方法

您可能使用过机器人或其他工具来查询单个曲目的成绩预览图，类似于 `/minfo 牛奶` 的命令。延续这种用法，maimai.py 提供了 [`maimai.minfo()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.minfo) 方法来查询单个曲目的信息，以及玩家关联的成绩。

使用 `maimai.minfo()` 方法只会获取必要的成绩资源，尽量节约请求时间和对查分器的压力。返回值是一个 [`PlayerSong`](../concepts/models.md#playersong) 对象，包含了曲目的信息和玩家的成绩列表。

传入的 `song` 参数可以是曲目的 ID、曲目对象、或者是曲目关键词（如曲目名称、别名、艺术家等）。如果传入的是关键词，maimai.py 会自动查询匹配的曲目并返回第一个结果。

::: info
如果您查询的数据源没有原生提供单曲成绩的接口，maimai.py 会获取所有成绩并自动筛选出对应曲目的成绩。
:::

::: warning
同样的，曲目 ID 遵循：同一首曲目的标准、DX 谱面、宴会谱面的 曲目ID 一致，不存在大于 10000 的 曲目ID（如有，均会对 10000 / 100000 取余处理）。

如果您对此有疑问，请参考 [开始 章节](../get-started.md#曲目id)。
:::

## maimai.updates() 方法

调用 [`maimai.updates()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.updates) 方法可以更新玩家的成绩到指定数据源（查分器）。

### 示例代码

#### 从 机台✨ 获取成绩并更新到查分器

```python
my_account = await maimai.qrcode("SGWCMAID241218124023A51D36BFBF65DB955DEB72905905D6A12D8056371E0499C74CD3592FCXXXXXXX")
scores = await maimai.scores(my_account, provider=ArcadeProvider())
asyncio.gather(
    maimai.updates(PlayerIdentifier(username="turou"), scores.scores, provider=divingfish),
    maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
)
```

#### 从 数据库🚀 获取成绩并更新查分器

借由 [数据源](../get-started.md#数据源) 机制，您可以创建自己的数据源实现，然后从 maimai.py 的规范化接口中获益。

下面是来自 [UsagiCard](https://uc.turou.fun/) 的示例代码，展示了如何从本地数据库获取成绩并更新到查分器。

```python
class UsagiCardProvider(IScoreProvider):
    async def get_scores_all(self, identifier: PlayerIdentifier, client: MaimaiClient) -> list[Score]:
        async with async_session_ctx() as session:
            stmt = UsagiCardProvider._deser_identifier(select(MaimaiScore), identifier)
            scores = await session.exec(stmt)
            return [score.as_mpy() for score in scores]

    async def get_scores_one(self, identifier: PlayerIdentifier, song: Song, client: MaimaiClient) -> list[Score]:
        async with async_session_ctx() as session:
            stmt = UsagiCardProvider._deser_identifier(select(MaimaiScore).where(col(MaimaiScore.song_id) == song.id), identifier)
            scores = await session.exec(stmt)
            return [score.as_mpy() for score in scores]

    @staticmethod
    def _ser_identifier(qq: str | None = None, uuid: str | None = None):
        credentials = {"qq": qq or "", "uuid": uuid or ""}
        return PlayerIdentifier(credentials=credentials)

    @staticmethod
    def _deser_identifier(stmt: SelectOfScalar[T], identifier: PlayerIdentifier) -> SelectOfScalar[T]:
        assert isinstance(identifier.credentials, dict), "Identifier credentials should be a dictionary."
        stmt = stmt.join(Card, onclause=col(MaimaiScore.card_id) == col(Card.id))
        if uuid := identifier.credentials.get("uuid"):
            return stmt.where(Card.uuid == uuid)
        return stmt

async def main():
    my_account = UsagiCardProvider._ser_identifier(uuid="your-uuid-here")
    my_scores = await maimai.scores(my_account, provider=UsagiCardProvider())
    await asyncio.gather(
        maimai.updates(PlayerIdentifier(username="turou"), my_scores.scores, provider=divingfish),
        maimai.updates(PlayerIdentifier(friend_code=664994421382429), my_scores.scores, provider=lxns)
    )
```

::: info
示例中的 `score.as_mpy()` 方法是将 数据库 的成绩对象转换为 maimai.py 的规范化 `Score` 对象。您可以根据自己的数据模型实现类似的方法。
:::

借由类似的操作，您可以实现一套完整的 数据源 机制，进而享受 maimai.py 提供的各种接口，甚至包含使用 MaimaiRoutes 直接创建对应的路由。

更多信息请参考 [集成 FastAPI 路由](../concepts/client.md#集成-fastapi-路由)。