# LXNSProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, IAliasProvider, IItemListProvider

源站：https://maimai.lxns.net/

开发者文档：https://maimai.lxns.net/docs/api/maimai

开发者交流群：991669419

## 如何提供 PlayerIdentifier

- 使用个人 API 密钥：`PlayerIdentifier(credentials="API-Secret")`，将使用个人 API。
- 使用好友代码：`PlayerIdentifier(friend_code="123456789")`，将使用开发者 API。
- 使用 QQ 号：`PlayerIdentifier(qq="123456789")`，将使用开发者 API。

## 关于开发者 API

申请开发者 Token：https://maimai.lxns.net/developer

在使用开发者 API 时，必须提供 `developer_token` 参数。

## 已知问题

- 通过落雪开发者 API 获取或上传信息时，需要玩家同意落雪的隐私设置，否则会抛出隐私异常。
- 新用户第一次使用落雪时，需要使用落雪官方代理上传一次，才能正常使用落雪 API。