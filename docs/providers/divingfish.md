# DivingFishProvider

实现：ISongProvider, IPlayerProvider, IScoreProvider

源站：https://www.diving-fish.com/maimaidx/prober/

开发者文档：https://github.com/Diving-Fish/maimaidx-prober/blob/main/database/zh-api-document.md

开发者交流群：605800479

## 关于开发者Token

申请开发者Token：登录 - 编辑个人资料 - 点击 “这里” 按钮 - 申请新Token

水鱼的开发者Token仅在以下场景是必须提供的：

- 获取玩家的所有成绩 (ScoreKind.ALL)

## 关于相对难度曲线数据源

水鱼提供基于所有玩家数据的相对难度（包含拟合定数），可以在调用 `maimai.songs()` 时获取。

## 关于上传成绩

水鱼在上传成绩时，有两种方式

- 使用水鱼用户名和密码：`PlayerIdentitifer(username="Username", credentials="Password")`
- 使用Import-Token：`PlayerIdentitifer(credentials="Import-Token")`