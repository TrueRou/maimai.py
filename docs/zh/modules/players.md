# 玩家数据

## maimai.players() 方法

从数据源获取玩家数据。

**支持的数据源**：`DivingFishProvider`、`LXNSProvider`。

### 参数

| 参数名 | 类型 | 说明 |
|-|-|-|
| identifier | PlayerIdentifier | 玩家标识，例如 `PlayerIdentifier(username="turou")` |
| provider | IPlayerProvider | 数据源，默认为 `LXNSProvider` |

### 返回值

`DivingFishPlayer` 或 `LXNSPlayer` 对象

### 异常

| 错误名称                           | 描述                                                         |
|-----------------------------------|--------------------------------------------------------------|
| InvalidPlayerIdentifierError       | 玩家标识符对于数据源无效，或者玩家未找到。                     |
| InvalidDeveloperTokenError         | 开发者令牌未提供或令牌无效。                                  |
| PrivacyLimitationError            | 用户尚未接受第三方访问数据。                                   |
| RequestError                      | 由于网络问题导致请求失败。                                   |

## maimai.wechat() 方法

该方法用于获取微信服务号玩家的玩家标识符

调用此方法时，如果不带任何参数，将获取到一个 URL，然后将用户重定向到该 URL（需要启用 mitmproxy）。

您的 mitmproxy 应该拦截来自 tgk-wcaime.wahlap.com 的响应，然后使用拦截到的响应参数再次调用此方法。

如果使用特定用户的响应参数，该方法将返回用户的播放器标识符。

切勿缓存或存储玩家标识符，因为 cookies 可能随时会过期。

### 参数

| 参数名 | 类型     | 默认值 | 说明         |
|--------|----------|--------|------------|
| r      | -        | None   | 请求中的 r 参数 |
| t      | -        | None   | 请求中的 t 参数 |
| code   | -        | None   | 请求中的 code 参数 |
| state  | -        | None   | 请求中的 state 参数 |

### 返回值

- 如果提供了所有参数，返回玩家标识符 PlayerIdentifier。
- 否则，返回用于获取标识符的 URL。

### 异常

| 异常名称             | 描述                         |
|---------------------|------------------------------|
| `WechatTokenExpiredError` | 当微信 token 过期时，请重新授权。 |
| `RequestError`       | 由于网络问题导致请求失败。       |

## maimai.qrcode() 方法

从 Wahlap 玩家二维码获取玩家标识符。

该方法通过玩家的 QR 码获取玩家标识符，这个标识符是加密后的 userId，不能在 maimai.py 之外的任何其他情况下使用。

### 参数

| 参数名 | 类型   | 说明                 |
|--------|--------|----------------------|
| qrcode | str    | 玩家的 QR 码，应以 SGWCMAID 开始 |

### 返回值

- 玩家标识符 `PlayerIdentifier`

### 异常

| 异常名称             | 描述                         |
|---------------------|------------------------------|
| `QRCodeFormatError`  | QR 码无效，请检查格式。         |
| `QRCodeExpiredError` | QR 码已过期，请重新生成 QR 码。 |
| `ArcadeError`       | 来自舞萌机台的其他未知错误。     |
| `RequestError`      | 由于网络问题导致请求失败。       |