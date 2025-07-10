# proxy_updater

**proxy_updater** 是针对 `maimai.wechat()` 和 `WechatProvider()` 的示例程序。

示例中提供了一个通过 `mitmproxy` 代理来更新玩家分数的脚本，允许用户通过微信 OAuth 认证来更新查分器数据，这种方式类似于 [Bakapiano方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)，是无风险的更新方式。

## 配置

示例 proxy_updater 是利用代理和微信OAuth认证更新查分器的示例，类似于 bakapiano / UsagiPass 的方案。

1. 首先，您需要确保已经全局安装了 `poetry` 包管理工具：`pip install poetry`。
2. 进入 `examples` 目录，然后运行 `poetry install` 来安装依赖。
3. 接下来，您需要配置环境变量，请根据 `.env.example` 文件创建一个 `.env` 文件，并根据您的环境修改其中的配置。
4. 最后，您可以运行 `poetry run python proxy_updater/main.py` 来启动代理服务器。

为了将流量导向代理服务器，您需要在您的设备上配置代理，下面是一个 Clash 代理配置示例：

```yaml
mixed-port: 7890
mode: rule
log-level: info

proxies:
  - name: maimai.py
    server: 127.0.0.1
    port: 8080
    type: http
    
rules:
  - DOMAIN,tgk-wcaime.wahlap.com,maimai.py
  - MATCH,DIRECT
```

根据实际环境修改服务器地址和绑定的端口号。

## 使用

程序启动后，会提示点击回车键来生成一个`Wechat URL`，用户点击回车后，程序会生成一个微信验证链接。

将链接复制到**运行了代理**的设备的微信中打开，即可开始进行导入过程。

::: tip
由于微信验证机制，验证链接的失效速度很快，一旦失效可以在CLI看到错误信息，只需重新生成即可。
:::

## 原理

原理参考了[Bakapiano方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)，这里引用Bakapiano的原话：

> 修改微信 OAuth2 认证中的 redirect_uri 链接，将 https://example.com 修改为 http://example.com 并通过 HTTP 代理截获。之后服务器通过认证信息获取舞萌 DX 成绩数据。理论上全平台支持，只要对应平台下的微信内置浏览器走全局 HTTP 代理

我们提供了 `maimai.wechat()` 方法，以及 `maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())` 方法，将上述原理封装，方便开发者调用，具体实现可参考示例项目中的 `updater.py` 文件。