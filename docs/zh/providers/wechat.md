# WechatProvider

从舞萌服务号的舞萌DX页面，通过HTML解析获取分数信息。

实现：IPlayerProvider, IScoreProvider

源站：https://maimai.wahlap.com/maimai-mobile/

## 关于IScoreProvider

`IScoreProvider` 仅支持获取成绩，不支持上传成绩。

## 如何使用

使用 WechatProvider 需要配合代理，具体使用例子可以查看 示例项目 部分。

## 实现原理

原理参考了[Bakapiano方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)，这里引用Bakapiano的原话：

> 修改微信 OAuth2 认证中的 redirect_uri 链接，将 https://example.com 修改为 http://example.com 并通过 HTTP 代理截获。之后服务器通过认证信息获取舞萌 DX 成绩数据。理论上全平台支持，只要对应平台下的微信内置浏览器走全局 HTTP 代理

我们提供 `maimai.wechat()` 方法，以及 `maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())` 方法，将上述原理封装，方便开发者调用。