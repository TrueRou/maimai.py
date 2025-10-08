# WechatProvider

舞萌服务号的舞萌 DX 玩家专页，通过 HTML 解析获取信息。

实现：IScoreProvider, IPlayerIdentifierProvider, IPlayerProvider

源站：https://maimai.wahlap.com/maimai-mobile/

## 如何提供 PlayerIdentifier

通过 [`maimai.wechat()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.wechat) 方法，你可以通过微信服务号来获取玩家的 PlayerIdentifier。

调用此方法时，如果不带任何参数，将获取到一个 URL，让玩家在启动代理的情况下访问URL。

这里的代理指的是中间人代理（如 mitmproxy），它会拦截微信服务号 `tgk-wcaime.wahlap.com` 的 OAuth2 认证请求。

在拦截的请求中，你可以获取到响应中的参数（r、t、code、state），这些参数是微信 OAuth2 认证的必要信息。

再次调用 `maimai.wechat()` 方法时，你可以传入这些参数（r、t、code、state）来获取 PlayerIdentifier。

::: info
参考 [proxy_updater（示例项目）](../samples/proxy_updater.md)部分，这是一个通过代理和微信 OAuth 认证更新查分器的示例。
:::

## 关于 Rival（对手）

通过 NET 的隐藏接口，你可以修改到玩家的对手信息。

```python
wechat = WechatProvider()
identifier = await maimai.wechat(r="r", t="t", code="code", state="state")
friends = await wechat.get_friends(identifier, maimai) # 需要主动传入 MaimaiClient 实例
await wechat.set_rival_on(identifier, friends[0], maimai) # 设置第一个好友为对手
```

鉴于接口原因，我们无法查询玩家已有的对手信息，只能开启和关闭对手。