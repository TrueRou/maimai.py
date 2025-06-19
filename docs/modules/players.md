# 玩家

## maimai.players() 方法

从数据源获取玩家数据。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`、`ArcadeProvider`。

### 参数

| 参数名     | 类型               | 说明                                               |
|------------|--------------------|--------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(username="turou")` |
| provider   | `IPlayerProvider`  | 数据源，默认为 `LXNSProvider`                       |

### 返回值

`Player` 对象

可强转为 `DivingFishPlayer` 或 `LXNSPlayer` 或 `ArcadePlayer` 对象

### 异常

| 错误名称                       | 描述                                  |
|--------------------------------|-------------------------------------|
| `InvalidPlayerIdentifierError` | 数据源不支持该玩家标识，或者玩家未找到 |
| `InvalidDeveloperTokenError`   | 未提供开发者令牌或令牌无效            |
| `PrivacyLimitationError`       | 用户尚未同意第三方开发者访问数据      |
| `httpx.HTTPError`              | 由于网络问题导致请求失败              |

只有使用 `ArcadeProvider` 才可能触发的异常:

| 错误名称           | 描述                                      |
|--------------------|-----------------------------------------|
| `TitleServerError` | 舞萌标题服务器的相关错误，可能是网络问题   |
| `ArcadeError`      | 舞萌 Response 非法，或者提供的玩家标识有误 |


## maimai.identifiers() 方法

该方法用于从数据源获取玩家标识。

玩家标识是加密的 userId，仅能在 maimai.py 内部使用。

**支持的数据源**：`WechatProvider`、`ArcadeProvider`。

### 参数

| 参数名   | 类型                  | 说明                                                             |
|----------|-----------------------|----------------------------------------------------------------|
| code     | `str` 或 `dict`       | 获取玩家标识的代码，可以是字符串或包含 r、t、code 和 state 键的字典 |
| provider | `IIdentifierProvider` | 数据源，默认为 `ArcadeProvider`                                   |

### 返回值

玩家标识 `PlayerIdentifier`

### 异常

| 错误名称                  | 描述                                              |
|---------------------------|-------------------------------------------------|
| `InvalidWechatTokenError` | 微信Token已过期，请重新授权                        |
| `AimeServerError`         | 舞萌Aime服务器错误，可能是无效二维码或二维码已过期 |
| `httpx.HTTPError`         | 由于网络问题导致请求失败                          |


## maimai.wechat() 方法

从华立微信公众号获取微信 OAuth URL。

该方法获取用于授权的微信 URL，用户需通过微信访问该 URL 并配合 mitmproxy 拦截响应数据。

### 参数

此方法没有参数。

### 返回值

- `str` 获取玩家标识的 URL

### 使用说明

1. 在用户的微信客户端中访问返回的 URL
2. 使用已启用的 mitmproxy 拦截来自 tgk-wcaime.wahlap.com 的响应
3. 使用拦截到的响应参数调用 `maimai.identifiers(provider=WechatProvider, code=...)` 方法获取玩家标识

### 异常

| 错误名称          | 描述                     |
|-------------------|------------------------|
| `httpx.HTTPError` | 由于网络问题导致请求失败 |

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.players
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.identifiers
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.wechat