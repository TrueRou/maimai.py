# 迁移指南：1.5.2 → 1.6.0（DivingFish OAuth）

本文档面向 AI Agent 与开发者，提供从 1.5.2 迁移到当前版本的完整路径。本次更新引入了**破坏性更改**，核心是将 DivingFishProvider 的认证体系从开发者 Token / 密码 / Import-Token 迁移到水鱼账号 OAuth。

## 1. 破坏性更改总览

| 变更点 | 旧代码（1.5.2） | 新代码（1.6.0） |
|---|---|---|
| **Provider 构造** | `DivingFishProvider(developer_token="...")` | `DivingFishProvider(client_id="...", client_secret="...")` |
| **玩家标识（OAuth）** | `PlayerIdentifier(credentials="ref:9a1b2c3d...")` | `PlayerIdentifier(ref="external-id")` 或 `PlayerIdentifier(sub=12345)`（credentials 透传仍支持） |
| **玩家标识（用户名查询）** | `PlayerIdentifier(username="turou")` | 不变，但配置了 OAuth 凭据后行为改变（见 §4） |
| **密码登录** | `PlayerIdentifier(username="X", credentials="密码")` | 不变，但优先级规则改变（见 §4） |
| **Import-Token** | `PlayerIdentifier(credentials="token")` | 不变 |
| **RESTful API 配置** | `MaimaiRoutes(divingfish_token=...)` / `--divingfish-token` | `divingfish_client_id`/`divingfish_client_secret` 参数与 CLI 选项（旧参数已移除） |
| **开发者 Token** | `developer_token` 参数 + `DIVINGFISH_DEVELOPER_TOKEN` 环境变量 | **已移除**，代码中不再存在 |
| **新增异常** | 无 | `PlayerNotAuthorizedError`、`RateLimitError` |

## 2. 迁移前置条件

在修改代码之前，必须完成水鱼账号 OAuth 的应用登记：

1. 登录 [开发者控制台](https://auth.diving-fish.com/console)；
2. 补全应用信息（名称、描述、主页地址、接入方式、需要的 scope）；
3. 生成 `client_secret`（**只显示一次**，立即保存到服务端配置）；
4. 引导用户完成一次绑定（设备码或授权码方式），建立授权记录与标识映射。

> 若你的应用是从开发者 Token 迁移而来，过去 90 天内查询过的用户的授权记录已自动补齐，无需重新授权。

## 3. 代码迁移路径

### 3.1 Provider 构造

```python
# 旧代码（已移除）
from maimai_py import DivingFishProvider
divingfish = DivingFishProvider(developer_token="your_token_here")

# 新代码
divingfish = DivingFishProvider(client_id="your_client_id", client_secret="your_client_secret")
```

`developer_token` 参数已从 `DivingFishProvider.__init__` 中移除，传入会抛出 `TypeError`。所有 `/dev/*` 端点调用已从代码中删除。

### 3.2 PlayerIdentifier 的破坏性更改

`PlayerIdentifier` 新增了两个字段：

```python
@dataclass
class PlayerIdentifier:
    qq: Optional[int] = None
    username: Optional[str] = None
    friend_code: Optional[int] = None
    credentials: Union[str, MutableMapping[str, Any], None] = None
    ref: Optional[str] = None      # 新增：DivingFish OAuth 外部用户 ID
    sub: Optional[int] = None      # 新增：DivingFish OAuth 水鱼用户 ID
```

**非破坏部分**：在 `credentials` 中直接放入完整的 subject 字符串（`ref:<已算好的摘要>`、`sub:<id>`、`username:<name>`）仍然支持——Provider 会原样透传、不做二次哈希。如果你自行管理摘要计算（例如跨服务共享），可以继续用这种方式；但更推荐迁移到 `ref`/`sub` 字段，由 Provider 实时拼装，避免 client_id 耦合泄漏到业务代码。

### 3.3 查询成绩（`maimai.scores()`）

```python
# 旧代码：开发者 Token + username/qq
scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
scores = await maimai.scores(PlayerIdentifier(qq=123456789), provider=divingfish)

# 新代码：OAuth + ref/sub（推荐）
scores = await maimai.scores(PlayerIdentifier(ref="your-external-user-id"), provider=divingfish)
scores = await maimai.scores(PlayerIdentifier(sub=12345), provider=divingfish)

# 新代码：OAuth + 裸 username（不带 credentials）
# 配置了 client_id/client_secret 后，username 会拼装为 username:turou 换票
scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
```

### 3.4 上传成绩（`maimai.updates()`）

```python
# 旧代码：密码登录或 Import-Token
await maimai.updates(PlayerIdentifier(username="X", credentials="密码"), scores, provider=divingfish)
await maimai.updates(PlayerIdentifier(credentials="import-token"), scores, provider=divingfish)

# 新代码：OAuth（需要 prober.records.write scope）
await maimai.updates(PlayerIdentifier(ref="your-external-user-id"), scores, provider=divingfish)
```

### 3.5 查询 B50（`maimai.bests()`）

```python
# 旧代码：公开接口，无需授权
bests = await maimai.bests(PlayerIdentifier(username="turou"), provider=divingfish)

# 新代码：OAuth 模式下自动回退
# 公开 /query/player 端点不接受 OAuth subject，库会自动改为拉取全量成绩后本地裁剪 B50
bests = await maimai.bests(PlayerIdentifier(ref="your-external-user-id"), provider=divingfish)
```

### 3.6 查询玩家信息（`maimai.players()`）与牌子（`maimai.plates()`）

这两个方法走公开接口 `/query/player`，**不接受 OAuth subject**。必须使用 `username` 或 `qq`：

```python
# 可用
player = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
plates = await maimai.plates(PlayerIdentifier(username="turou"), "舞将", provider=divingfish)

# 不可用：会抛出 InvalidPlayerIdentifierError
player = await maimai.players(PlayerIdentifier(ref="..."), provider=divingfish)
```

## 4. 标识解析优先级与陷阱

`_oauth_subject` 的判定顺序为 `credentials` 透传 > `ref` > `sub` > `username`（裸 username 才生效）：

```python
# 优先级 1：credentials 直接放完整的 subject 字符串，原样透传、不再哈希（最优先）
PlayerIdentifier(credentials="ref:9a1b2c3d...")   # → ref:9a1b2c3d...（须自行 sha256）
PlayerIdentifier(credentials="sub:12345")         # → sub:12345
PlayerIdentifier(credentials="username:turou")    # → username:turou

# 优先级 2：ref 字段
PlayerIdentifier(ref="external-id")  # → ref:<sha256(client_id:external-id)>

# 优先级 3：sub 字段
PlayerIdentifier(sub=12345)          # → sub:12345

# 优先级 4：裸 username（不带 credentials，且 Provider 配置了 OAuth 凭据）
PlayerIdentifier(username="turou")   # → username:turou

# 陷阱：username + 普通 credentials 同时给出时，回到密码登录分支
PlayerIdentifier(username="X", credentials="密码")  # → POST /login，不是 OAuth
```

**关键陷阱**：在配置了 OAuth 凭据的 Provider 下，以下写法**不会**走 OAuth：

```python
# 不会走 OAuth！credentials 非空且不带 subject 前缀，回到密码登录分支
PlayerIdentifier(username="turou", credentials="some-password")
```

**注意**：`credentials` 透传要求字符串以 `ref:`/`sub:`/`username:` 开头，否则会被当作密码或 Import-Token。其中 `ref:` 后的摘要必须由调用方自行按 `sha256(f"{client_id}:{external_id}")` 算好——Provider 对透传的 subject 不做任何加工。

## 5. RESTful API 迁移

### 5.1 MaimaiRoutes 构造

```python
# 旧代码
routes = MaimaiRoutes(client, divingfish_token="your_token")

# 新代码
routes = MaimaiRoutes(
    client,
    divingfish_client_id="your_client_id",
    divingfish_client_secret="your_client_secret",
)
```

### 5.2 CLI 启动

```bash
# 旧方式
python -m maimai_py.api --divingfish-token your_token

# 新方式
python -m maimai_py.api --divingfish-client-id your_id --divingfish-client-secret your_secret
```

### 5.3 环境变量

```bash
# 新增环境变量
DIVINGFISH_CLIENT_ID=your_client_id
DIVINGFISH_CLIENT_SECRET=your_client_secret
```

### 5.4 API 请求参数

`_dep_divingfish_player` 现在暴露 `ref` 和 `sub` 查询参数：

```
GET /divingfish/scores?ref=your-external-user-id
GET /divingfish/scores?sub=12345
```

`UpdatesChainRequest` 的示例中，divingfish target 现在使用 `{"ref": "your-external-user-id"}`。

## 6. 异常处理迁移

新增两个异常类，需要从 `maimai_py.exceptions` 导入：

```python
from maimai_py.exceptions import PlayerNotAuthorizedError, RateLimitError

try:
    scores = await maimai.scores(PlayerIdentifier(ref="..."), provider=divingfish)
except PlayerNotAuthorizedError as e:
    # 用户未授权应用，或 access token 缺少 scope
    # 消息中包含缺失的 scope 名称（如 prober.records.write）
    print(f"需要用户授权：{e}")
except RateLimitError as e:
    # 超出每日配额或换票限流
    print(f"请求超限：{e}")
```

### 6.1 旧异常映射变化

| 场景 | 旧异常（1.5.2） | 新异常（1.6.0） |
|---|---|---|
| 用户未授权 OAuth 应用 | 无此概念 | `PlayerNotAuthorizedError` |
| 缺少 scope（如 write） | `PrivacyLimitationError` | `PlayerNotAuthorizedError`（消息含 scope 名） |
| 超出每日配额 | 无此概念 | `RateLimitError` |
| 换票限流（slow_down） | 无此概念 | `RateLimitError` |
| 传入 `developer_token` 参数 | 正常使用 | `TypeError`（参数已移除） |
| 用户未同意用户协议 | `PrivacyLimitationError` | `PrivacyLimitationError`（不变） |

## 7. 令牌缓存机制

OAuth access token 有效期为 5 分钟，库会自动通过 `MaimaiClient` 的全局缓存复用：

```python
# 默认：内存缓存（SimpleMemoryCache）
maimai = MaimaiClient()

# 可选：Redis 缓存（跨进程共享）
from aiocache import RedisCache
from aiocache.serializers import PickleSerializer

redis_cache = RedisCache(serializer=PickleSerializer(), endpoint="localhost", port=6379)
maimai = MaimaiClient(cache=redis_cache)
```

**注意**：不要手动缓存或持久化 access token，库已处理。换票接口每小时限 60 次/用户，缓存缺失会导致触发限流。

## 8. 完整迁移示例

### 8.1 迁移前（1.5.2）

```python
import asyncio
from maimai_py import MaimaiClient, DivingFishProvider, PlayerIdentifier

maimai = MaimaiClient()
divingfish = DivingFishProvider(developer_token="legacy-token")

async def main():
    # 查询成绩
    scores = await maimai.scores(PlayerIdentifier(username="turou"), provider=divingfish)
    # 查询 B50
    bests = await maimai.bests(PlayerIdentifier(username="turou"), provider=divingfish)
    # 上传成绩（密码）
    await maimai.updates(PlayerIdentifier(username="X", credentials="密码"), scores.scores, provider=divingfish)

asyncio.run(main())
```

### 8.2 迁移后（当前版本）

```python
import asyncio
from maimai_py import MaimaiClient, DivingFishProvider, PlayerIdentifier
from maimai_py.exceptions import PlayerNotAuthorizedError, RateLimitError

maimai = MaimaiClient()
divingfish = DivingFishProvider(client_id="your_client_id", client_secret="your_client_secret")

async def main():
    # 查询成绩：使用 ref（你的外部用户 ID）
    scores = await maimai.scores(PlayerIdentifier(ref="user-12345"), provider=divingfish)
    # 查询 B50：OAuth 自动回退为全量拉取 + 本地裁剪
    bests = await maimai.bests(PlayerIdentifier(ref="user-12345"), provider=divingfish)
    # 查询玩家信息：仍需 username（公开接口）
    player = await maimai.players(PlayerIdentifier(username="turou"), provider=divingfish)
    # 上传成绩：OAuth（需 prober.records.write scope）
    try:
        await maimai.updates(PlayerIdentifier(ref="user-12345"), scores.scores, provider=divingfish)
    except PlayerNotAuthorizedError as e:
        print(f"用户未授权或缺少 write scope：{e}")

asyncio.run(main())
```

## 9. 常见问题排查

| 现象 | 原因 | 解决 |
|---|---|---|
| `InvalidDeveloperTokenError: OAuth client_id is required to hash the ref external id` | 使用了 `ref` 但未配置 `client_id` | 在 Provider 构造时传入 `client_id` |
| `InvalidDeveloperTokenError: OAuth client_id/client_secret is required...` | 使用了 `ref`/`sub` 但未配置完整凭据 | 同时传入 `client_id` 和 `client_secret` |
| `PlayerNotAuthorizedError: the player has not consented` | 用户未授权应用，或 `ref` 摘要计算错误 | 引导用户完成设备码绑定；检查 `sha256(client_id:external_id)` 计算是否正确 |
| `PlayerNotAuthorizedError: ...缺少权限：prober.records.write` | 上传成绩时缺少 write scope | 在控制台申请 `prober.records.write` 并等待人工审核 |
| `RateLimitError` | 超出每日配额或换票限流 | 检查是否缓存了 token；确认配额是否满足业务需求 |
| `TypeError: unexpected keyword argument 'developer_token'` | 仍在传入 `developer_token` 参数 | 移除该参数，改用 `client_id`/`client_secret` |

## 10. 参考链接

- [从 Developer-Token 迁移到水鱼账号 OAuth（官方）](https://maimai.diving-fish.com/manual/docs/developer/oauth-migration)
- [水鱼账号 OAuth 接口文档（官方）](https://maimai.diving-fish.com/manual/docs/developer/oauth-api-document)
- [DivingFishProvider 文档](./providers/divingfish.md)
