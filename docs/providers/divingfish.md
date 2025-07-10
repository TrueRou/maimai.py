# DivingFishProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ICurveProvider

源站：https://www.diving-fish.com/maimaidx/prober/

开发者文档：https://github.com/Diving-Fish/maimaidx-prober/blob/main/database/zh-api-document.md

开发者交流群：605800479

## 如何提供 PlayerIdentifier

- 使用水鱼用户名：`PlayerIdentifier(username="username")`，将使用开发者API。
- 使用QQ号：`PlayerIdentifier(qq="123456789")`，将使用开发者API。

::: info
特别的，在更新查分器时：

- 使用个人Import-Token：`PlayerIdentifier(credentials="Import-Token")`，将使用个人API。
- 使用水鱼用户名和密码：`PlayerIdentifier(username="Username", credentials="Password")`，将使用个人API。
:::

## 关于开发者API

申请开发者Token：登录 - 编辑个人资料 - 点击 “这里” 按钮 - 申请新Token。

在使用开发者API时，必须提供 `developer_token` 参数。

## 已知问题

- 水鱼 UTAGE 曲目不包含 `notes` 信息，如果需要，推荐使用 `LXNSProvider`。