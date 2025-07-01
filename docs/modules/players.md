# 玩家

## maimai.players() 方法

如果你只需要获取玩家的基本信息（用户名，Rating等信息），可以使用 [`maimai.players()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.players) 方法。

针对不同的数据源，`maimai.py` 会返回不同类型的玩家对象，例如 `DivingFishPlayer`、`LXNSPlayer` 或 `ArcadePlayer`，但是他们都统一继承自 `Player` 类。

### 示例代码

#### 从水鱼获取玩家信息

返回的 Player 对象是 [`DivingFishPlayer`](../concepts/models.md#divingfishplayer) 类型。

```python
divingfish = DivingFishProvider(developer_token="your_developer_token")
player = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
print(f"玩家用户名: {player.username}, Rating: {player.rating}")
```

#### 从 LXNS 获取玩家信息

返回的 Player 对象是 [`LXNSPlayer`](../concepts/models.md#lxnsplayer) 类型。

```python
lxns = LXNSProvider(developer_token="your_developer_token")
player = await maimai.players(PlayerIdentifier(friend_code=664994421382429), provider=lxns)
print(f"玩家用户名: {player.username}, Rating: {player.rating}, )
```

#### 从 机台✨ 获取玩家信息

返回的 Player 对象是 [`ArcadePlayer`](../concepts/models.md#arcadeplayer) 类型。

```python
player = await maimai.players(PlayerIdentifier(credentials="EncryptedUserId"), provider=ArcadeProvider())
print(f"玩家用户名: {player.username}, Rating: {player.rating}, 是否已登录: {player.is_login}")
```

### 注意事项
- `maimai.players()` 方法可以接受多种类型的玩家标识符（`PlayerIdentifier`），请参考对应 Provider 的文档来了解如何正确提供。
- 返回的玩家对象类型取决于所使用的数据源（如 `DivingFishProvider`、`LXNSProvider` 或 `ArcadeProvider`）。
- 如果你需要获取更详细的玩家信息（如游玩地区、游玩成绩等），可以使用其他方法，如 `maimai.regions()` 或 `maimai.scores()`。

## 你是否在找 PlayerIdentifier？

本页面所指的 `Player` 是指玩家对象，而不是 `PlayerIdentifier`。如果你需要了解如何创建和使用 `PlayerIdentifier`，请参考 [开始 章节](../get-started.md#玩家标识)。

如果你不清楚数据源应该如何提供 `PlayerIdentifier`，可以参考对应的数据源章节：

- [DivingFishProvider](../providers/divingfish.md)
- [LXNSProvider](../providers/lxns.md)
- [ArcadeProvider](../providers/arcade.md)
- [WeChatProvider](../providers/wechat.md)