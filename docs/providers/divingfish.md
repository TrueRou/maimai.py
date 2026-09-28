# DivingFishProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ICurveProvider

源站：https://www.diving-fish.com/maimaidx/prober/

开发者文档：https://github.com/Diving-Fish/maimaidx-prober/blob/main/database/zh-api-document.md

开发者交流群：605800479

## 如何提供 PlayerIdentifier

- 使用水鱼账号 OAuth：`PlayerIdentifier(ref="external-id")` 或 `PlayerIdentifier(sub=12345)` 或 `PlayerIdentifier(username="username")` ，需要 Provider 配置 `client_id`/`client_secret`。

::: info
特别的，在更新查分器时：

- 使用水鱼用户名和密码：`PlayerIdentifier(username="Username", credentials="Password")`。
- 使用水鱼账号 OAuth：`PlayerIdentifier(ref=...)` 或 `PlayerIdentifier(sub=...)`，需要 `prober.records.write` scope。
:::

## 水鱼账号 OAuth

水鱼账号 OAuth 是访问查分器玩家数据的授权体系。用户逐个授权你的应用，查询对象由令牌决定，请求中不再需要 `qq` / `username` 参数。

1. 在 [开发者控制台](https://auth.diving-fish.com/console) 登记并补全应用信息，生成 `client_secret`；
2. 引导用户完成一次绑定（设备码或授权码方式），用户授权记录与标识的映射即告建立；
3. 用应用的 `client_id` / `client_secret` 构造 Provider，并通过 `ref` / `sub` 指定玩家：

```python
from maimai_py import DivingFishProvider, MaimaiClient, PlayerIdentifier

divingfish = DivingFishProvider(client_id="your_client_id", client_secret="your_client_secret")
maimai = MaimaiClient()

# ref: 你自己一侧的用户标识，Provider 会实时拼装为 ref:<sha256(client_id:ref)> 换票，推荐
scores = await maimai.scores(PlayerIdentifier(ref="your-external-user-id"), provider=divingfish)
# sub: 水鱼用户 ID，拼装为 sub:<id>
scores = await maimai.scores(PlayerIdentifier(sub=12345), provider=divingfish)
# 配置了 client_id/client_secret 时，裸 username（不带 credentials）也会通过 OAuth（拼装为 username:<name>）访问成绩
scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
# 或者把已经算好的 subject 字符串直接放入 credentials，Provider 原样使用、不做二次哈希
scores = await maimai.scores(PlayerIdentifier(credentials="ref:<sha256(client_id:external_id)>"), provider=divingfish)
```

### 玩家标识的优先级

| 标识                                  | 拼装出的 subject                      | 说明                                  |
|---------------------------------------|---------------------------------------|---------------------------------------|
| `credentials="ref:<已算好的摘要>"` 等 | 原样透传，不再哈希                     | 自行管理 subject 时的入口，优先级最高  |
| `ref="external_id"`                   | `ref:<sha256(client_id:external_id)>` | 你自己一侧的用户体系，推荐             |
| `sub=12345`                           | `sub:12345`                           | 水鱼用户 ID                           |
| `username="turou"`（不带 credentials）  | `username:turou`                      | 仅在 Provider 配置了 OAuth 凭据时生效 |

四者按 `credentials` 透传 > `ref` > `sub` > `username` 取第一个。`ref` 摘要中混入了 `client_id`，同一个用户在不同应用中的标识互不相同。注意 `username` 与不带 subject 前缀的 `credentials` 同时给出时始终表示密码登录，不会被当作 OAuth 标识。

### scope 与令牌缓存

- 读取成绩需要 `prober.records.read` scope；上传成绩（`maimai.updates()`）需要 `prober.records.write` scope（需人工审核）。
- 换来的 access token 有效期为 5 分钟，本库会通过 `MaimaiClient` 的全局缓存复用到临近过期，Redis 缓存后端下可跨进程共享。
- 用户未授权你的应用（或用户不存在）时抛出 `PlayerNotAuthorizedError`；超出每日配额时抛出 `RateLimitError`。

## 已知问题

- 水鱼 UTAGE 曲目不包含 `notes` 信息，如果需要，推荐使用 `LXNSProvider`。
- `maimai.players()` 走公开接口，无法使用 `ref`/`sub` 标识查询。
