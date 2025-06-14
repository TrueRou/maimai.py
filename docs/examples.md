# 例子

所有的函数都可以提供 `provider` 参数，可以根据需求传入不同的数据源，可以通过文档或代码提示查看具体支持的 `provider` 。

## 创建 MaimaiClient 实例

歌曲缓存基于 `MaimaiClient` 实例，**切勿创建多个实例**。

```python
# 全局创建 MaimaiClient 实例
maimai = MaimaiClient()
divingfish = DivingFishProvider(developer_token="your_token_here")
lxns = LXNSProvider(developer_token="your_token_here")
```

## 获取歌曲信息

```python
# 获取歌曲数据，因为用不到拟合难度，所以传入 curve_provider=None
songs = await maimai.songs(curve_provider=None)
# songs = await maimai.songs(provider=DivingFishProvider()) # 可以手动指定水鱼数据源

# 从ID查询歌曲
song1 = await songs.by_id(1231)  # 生命不詳
assert song1.title == "生命不詳"
assert song1.difficulties.dx[3].note_designer == "はっぴー"

# 从别名查询歌曲
song2 = await songs.by_alias("不知死活")
assert song2.id == song1.id
```

## 获取玩家信息

```python
# 从落雪获取 664994421382429 玩家的信息
player1 = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
assert player1.rating > 10000

# 从水鱼获取 turou 玩家的信息
player2 = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
assert player2.rating > 10000
```

## 获取成绩信息

```python
# 从落雪获取 664994421382429 玩家的所有成绩
my_scores = await maimai.scores(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
# 返回了一个成绩列表对象，可以计算类似rating、rating_b35、rating_b15这些信息
assert my_scores.rating_b35 > 10000
# 也可以通过 by_song 获取 1231 这首歌 MASTER 的成绩
assert my_scores.by_song(1231, SongType.DX, LevelIndex.MASTER).dx_rating  # 生命不詳 MASTER SSS+
# 获取谱面难度对象，查询谱面定数
assert my_scores.by_song(1231, SongType.DX, LevelIndex.MASTER).difficulty.level_value == 13.7

# 从水鱼获取数据，做类似的事情
my_scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
assert my_scores.rating > 15000
```

### 从机台获取成绩

```python
# 这里的QRCode填写微信的玩家二维码解析后的内容
my_account = await maimai.qrcode("SGWCMAID241218124023A51D36BFBF65DB955DEB72905905D6A12D8056371E0499C74CD3592FCXXXXXXX")
scores = await maimai.scores(my_account, provider=ArcadeProvider())
await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
```

### 通过代理获取成绩

```python
wx_player = await maimai.wechat(r, t, code, state)
scores = await maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())
diving_player = PlayerIdentifier(username=config["diving_fish"]["username"], credentials=config["diving_fish"]["credentials"])
lxns_player = PlayerIdentifier(friend_code=config["lxns"]["friend_code"])

tasks = [
    asyncio.create_task(maimai.updates(diving_player, scores.scores, provider=divingfish)),
    asyncio.create_task(maimai.updates(lxns_player, scores.scores, provider=lxns))
]

await asyncio.gather(*tasks)
```

::: info
阅读 [示例项目](./dev/samples.md) 了解更多
:::

## 获取牌子信息

```python
# 从落雪获取 664994421382429 玩家的舞将达成情况
my_plate = await maimai.plates(PlayerIdentifier(friend_code=664994421382429), "舞将", provider=lxns)
assert my_plate.cleared_num + my_plate.remained_num == my_plate.all_num

# 打印一下游玩了，但是没达成目标的成绩信息
for plate_object in my_plate.remained:
    message = f"您在 舞将 牌子的 {plate_object.song.title} 歌的目标未达成，您游玩了，但是未满足条件的成绩为："
    for score in plate_object.scores:
        message += f"{score.level}难度：{score.dx_rating} %\n"
```

## 更新成绩到数据源

```python
# 从水鱼拉取成绩，并且上传到落雪 （有点怪怪的，这里只是举个例子，正常来说应该从微信源或者机台源获取，然后上传到查分器才对）
scores = await maimai.scores(PlayerIdentifier(username="turou"), kind=ScoreKind.ALL, provider=divingfish)
await maimai.updates(PlayerIdentifier(friend_code=664994421382429), scores.scores, provider=lxns)
```
