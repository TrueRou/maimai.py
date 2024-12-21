# WechatProvider

Get the score information from the Maimai DX page of the Maimai OffiAccount via HTML parsing.

Implementation: IPlayerProvider, IScoreProvider

Source: https://maimai.wahlap.com/maimai-mobile/

## About IScoreProvider

`IScoreProvider` only supports getting scores, not uploading scores.

## How to use

To use WechatProvider, you need to use a proxy, please refer to the Sample Projects section for examples.

## How it works

The principle refers to [Bakapiano program](https://github.com/bakapiano/maimaidx-prober-proxy-updater), here is the quote from Bakapiano:

> Modify the redirect_uri link in WeChat OAuth2 authentication, change https://example.com to http://example.com and intercept it via HTTP proxy. After that, the server will get the maimai DX score data through the authentication information. Theoretically, all platforms are supported, as long as the built-in WeChat browser on the corresponding platform uses the global HTTP proxy.

We provide `maimai.wechat()` method and `maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())` method to wrap the above principle, which is convenient for developers to call.