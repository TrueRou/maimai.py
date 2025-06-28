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

| 错误名称                  | 描述                                           |
|---------------------------|----------------------------------------------|
| `TitleServerNetworkError` | 舞萌 官方服务器相关错误，可能是网络问题         |
| `TitleServerBlockedError` | 舞萌 官方服务器拒绝了请求，可能是因为 IP 被过滤 |
| `ArcadeIdentifierError`   | 舞萌 用户 ID 无效，或者用户未找到               |

## maimai.wechat() 方法

该方法用于通过 **微信服务号** 来获取玩家的 `PlayerIdentifier`。

调用此方法时，如果不带任何参数，将获取到一个 URL，让玩家在启动代理的情况下访问URL，代理将请求转发至 mitmproxy。

转发后，您的 mitmproxy 应该拦截到了来自 `tgk-wcaime.wahlap.com` 的响应，请使用拦截到的**响应中的参数**再次调用此方法。

当提供**响应中的参数**（r、t、code、state）后，该方法将返回用户的 `PlayerIdentifier`。

### 参数

| 参数名 | 类型 | 默认值 | 说明                |
|--------|------|--------|-------------------|
| r      | -    | `None` | 请求中的 r 参数     |
| t      | -    | `None` | 请求中的 t 参数     |
| code   | -    | `None` | 请求中的 code 参数  |
| state  | -    | `None` | 请求中的 state 参数 |

### 返回值

- 如果提供了所有参数，将返回 `PlayerIdentifier`。
- 如果不提供参数，将返回一个 URL，玩家需要访问该URL，之后再进行下一步的操作。

### 异常

| 异常名称                  | 描述                       |
|---------------------------|--------------------------|
| `WechatTokenExpiredError` | 微信Token已过期，请重新授权 |
| `httpx.HTTPError`         | 由于网络问题导致请求失败   |

## maimai.qrcode() 方法

从 **玩家二维码** 获取 `PlayerIdentifier`。

该方法从舞萌机台的接口通过玩家二维码获取玩家userId，maimai.py 解析出的userId仅能在内部使用。

### 参数

| 参数名     | 类型          | 说明                                  |
|------------|---------------|-------------------------------------|
| qrcode     | `str`         | 玩家的 QR 码，应以 SGWCMAID 开始       |
| http_proxy | `str \| None` | 代理地址，例如 `http://127.0.0.1:7890` |

### 返回值

- 玩家标识 `PlayerIdentifier`

### 异常

| 异常名称          | 描述                                              |
|-------------------|-------------------------------------------------|
| `AimeServerError` | 舞萌Aime服务器错误，可能是无效二维码或二维码已过期 |

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

### 使用说明

1. 在用户的微信客户端中访问返回的 URL
2. 使用已启用的 mitmproxy 拦截来自 tgk-wcaime.wahlap.com 的响应
3. 使用拦截到的响应参数调用 `maimai.identifiers(provider=WechatProvider, code=...)` 方法获取玩家标识

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.players
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.wechat
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.qrcode
- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.identifiers