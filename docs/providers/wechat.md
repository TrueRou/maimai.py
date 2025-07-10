# WechatProvider

舞萌服务号的舞萌DX页面，通过HTML解析获取信息。

实现：IScoreProvider, IPlayerIdentifierProvider

源站：https://maimai.wahlap.com/maimai-mobile/

## 如何提供 PlayerIdentifier

通过 [`maimai.wechat()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.wechat) 方法，您可以通过微信服务号来获取玩家的 PlayerIdentifier。

调用此方法时，如果不带任何参数，将获取到一个 URL，让玩家在启动代理的情况下访问URL。

这里的代理指的是中间人代理（如 mitmproxy），它会拦截微信服务号 tgk-wcaime.wahlap.com 的 OAuth2 认证请求。

在拦截的请求中，您可以获取到响应中的参数（r、t、code、state），这些参数是微信 OAuth2 认证的必要信息。

再次调用 `maimai.wechat()` 方法时，您可以传入这些参数（r、t、code、state）来获取 PlayerIdentifier。

::: info
参考 [proxy_updater (示例项目)](../samples/proxy_updater.md) 部分，这是一个通过代理和微信 OAuth 认证更新查分器的示例。
:::

## 已知问题

- WechatProvider 可能出现轻微内存泄露问题。