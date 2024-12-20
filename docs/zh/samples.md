# 示例项目

针对部分较为复杂的功能，我们提供了交互式的示例项目以供开发者测试和参考。

注意，下面这些项目仅供进阶开发者使用，如果您只是想使用`maimai.py`的基础功能，可以不用阅读这部分内容。

运行示例项目前，请先按照下面的说明来配置 maimai.py 开发环境：

1. 下载并进入项目根目录: `git clone https://github.com/TrueRou/maimai.py.git && cd maimai.py`
2. 创建并启用Poetry环境: `pip install poetry && poetry install && poetry shell`
3. 进入对应示例目录: `cd examples && cd proxy_updater`
4. 运行示例项目: `python main.py`

至此，示例项目的环境配置已经完成，您可以体验下面这些示例项目了

- **proxy_updater**: 针对 `maimai.wechat()` 和 `WechatProvider()` 的示例程序

## proxy_updater

### 配置

示例 proxy_updater 是利用代理和微信OAuth认证更新查分器的示例，类似于 bakapiano / UsagiPass 的方案。

在第一次运行`python main.py`后，在目录中会生成`config.json`和`proxy.yaml`，分别对应项目的配置文件和代理的配置文件。

您可以修改`config.json`和`proxy.yaml`中定义的IP和端口，以适应你的工作区环境。

> `proxy.yaml` 是 **Clash** 的配置文件，可以导入到任何支持 Clash 配置的代理工具中

配置文件中，可以开启或关闭水鱼和落雪查分器的上传。水鱼查分器上传需提供账号密码、落雪需提供好友代码和开发者Token

> 水鱼查分器上传可以使用`Import-Token`，只需要将用户名留空，`credentials`填入`Import-Token`就可以了

在修改配置文件后，重新启动程序，即可正常使用并测试示例项目

### 使用

程序启动后，会提示点击回车键来生成一个`Wechat URL`，用户点击回车后，程序会生成一个微信验证链接。

将链接复制到**运行了代理**的设备的微信中打开，即可开始进行导入过程。

> 由于微信验证机制，验证链接的失效速度很快，一旦失效可以在CLI看到错误信息，只需重新生成即可。

### 原理

原理参考了[Bakapiano方案](https://github.com/bakapiano/maimaidx-prober-proxy-updater)，这里引用Bakapiano的原话：

> 修改微信 OAuth2 认证中的 redirect_uri 链接，将 https://example.com 修改为 http://example.com 并通过 HTTP 代理截获。之后服务器通过认证信息获取舞萌 DX 成绩数据。理论上全平台支持，只要对应平台下的微信内置浏览器走全局 HTTP 代理

我们提供了 `maimai.wechat()` 方法，以及 `maimai.scores(wx_player, ScoreKind.ALL, WechatProvider())` 方法，将上述原理封装，方便开发者调用。

具体实现可参考示例项目中的 `updater.py` 文件