# LXNSProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, IAliasProvider, IItemListProvider

源站：https://maimai.lxns.net/

开发者文档：https://maimai.lxns.net/docs/api/maimai

开发者交流群：991669419

## PlayerIdentifier

使用个人API密钥：`PlayerIdentitifer(credentials="API-Secret")`，将使用个人API。

使用好友代码：`PlayerIdentitifer(friend_code="")`，将使用开发者API。

使用QQ号：`PlayerIdentitifer(qq="")`，将使用开发者API。

## 关于开发者Token

申请开发者Token：https://maimai.lxns.net/developer

在使用开发者API时，必须提供 `developer_token` 参数。

建议始终提供落雪的开发者Token，落雪的大部分操作都需要开发者Token。

## 已知问题

- 通过落雪开发者API获取或上传信息时，需要玩家同意落雪的隐私设置，否则会抛出隐私异常。
- 新用户第一次使用落雪时，需要使用落雪官方代理上传一次，才能正常使用落雪API。