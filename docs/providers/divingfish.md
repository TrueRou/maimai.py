# DivingFishProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider, IScoreUpdateProvider, ICurveProvider

源站：https://www.diving-fish.com/maimaidx/prober/

开发者文档：https://github.com/Diving-Fish/maimaidx-prober/blob/main/database/zh-api-document.md

开发者交流群：605800479

## PlayerIdentifier

在上传成绩时，使用个人Import-Token：`PlayerIdentitifer(credentials="Import-Token")`，将使用个人API。

在上传成绩时，使用水鱼用户名和密码：`PlayerIdentitifer(username="Username", credentials="Password")`，将使用个人API。

在获取成绩时，`PlayerIdentitifer` 可以使用 `username` 或 `qq`，将使用开发者API。

在获取玩家时，`PlayerIdentitifer` 可以使用 `username` 或 `qq`，将使用开发者API。

## 关于开发者Token

申请开发者Token：登录 - 编辑个人资料 - 点击 “这里” 按钮 - 申请新Token

在使用开发者API时，必须提供 `developer_token` 参数。

## 关于相对难度曲线数据源

水鱼提供基于所有玩家数据的相对难度（包含拟合定数），可以在调用 `maimai.songs()` 时获取。

## 已知问题

- 水鱼 UTAGE 曲目不包含 `notes` 信息，如果需要，推荐使用 `LXNSProvider`。