# WechatProvider

舞萌服务号的舞萌DX页面，通过HTML解析获取信息。

实现：IScoreProvider, IPlayerIdentifierProvider

源站：https://maimai.wahlap.com/maimai-mobile/

## PlayerIdentifier

- 在获取成绩时，使用微信OAuth认证：`PlayerIdentifier(credentials={...})`，可以通过 `maimai.wechat()` 方法获取。

## 使用方法

参考 [proxy_updater (示例项目)](../samples/proxy_updater.md) 部分。


## 已知问题

- WechatProvider 可能出现轻微内存泄露问题。