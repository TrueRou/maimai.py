# ArcadeProvider

来自舞萌机台的接口，通过玩家二维码获取玩家加密 userId，进而获取分数等信息

实现：IPlayerProvider, IScoreProvider, IRegionProvider, IPlayerIdentifierProvider

源站：AimeServer、MaimaiTitleServer

PyPi: https://pypi.org/project/maimai-ffi

## 如何提供 PlayerIdentifier

调用 [`maimai.qrcode()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.qrcode) 方法可以获取机台玩家的 PlayerIdentifier。

调用方法时，需要提供仍在有效期的玩家二维码，二维码应该以 `SGWCMAID` 开头。返回的 `PlayerIdentifier` 对象将包含**加密的**用户 ID，该加密用户 ID 仅能在 maimai.py 内部使用。

此外，由于用户 ID 不会过期，你可以将其序列化并保存（只需保存 `identifier.credentials` 字段内容即可），以便后续使用。

## 关于开源

这部分的 `maimai.py` 是不开源的，我们仅在 PyPi 上分发编译后的二进制包。

如果你使用的设备或者架构不受支持，请联系我们或者在 Github 上开 Issues，我们将尽快解决你的问题。

## 关于安全性

将 userId 贸然提供给开发者进行保存是不安全的，我们希望 maimai.py 解析出的 userId 仅能在内部使用。

我们对玩家的 userId 进行了 AES 加密，在调用方法时进行解密，尽可能保证了玩家 userId 的安全。

有更多安全性建议可以联系我们，我们致力于保证玩家数据的安全，致力于维护舞萌机台服务器的安全。

# 关于代理

由于网络环境的原因，一些用户可能需要使用代理来访问舞萌机台服务器。我们在构造函数中提供了一个 http_proxy 参数来支持代理的使用。

```python
from maimai import ArcadeProvider

provider = ArcadeProvider(http_proxy="http://127.0.0.1:7890")
```

## 免责声明

风险告知：

本服务需要连接至华立科技 AIME 和标题服务器，且默认的通讯协议及相关混淆原理均来源于 Github 开源仓库，开发者未使用软件逆向等数据和工具对任何游戏文件进行分析。本服务可能存在未知的逻辑错误，可能会导致潜在的风险如数据丢失、系统崩溃等，由用户自行决定是否下载、使用本服务。

本服务本身不提供任何侵入、修改、抓取其他应用内存及网络数据的功能，仅整合了各大开源项目提供的服务供用户自行选择，方便安全分析人员使用，减少用户的重复性劳动以及管理成本。用户只可使用本服务进行正规的学习研究或是经过合法授权的应用分析、测试等行为，若用户在使用该软件服务的过程中违背以上原则对第三方造成损失，一切责任由该用户自行承担。

任何单位或个人因下载使用本服务而产生的任何意外、疏忽、合约毁坏、诽谤、版权或知识产权侵犯及其造成的损失（包括但不限于直接、间接、附带或衍生的损失等），开发者不承担任何法律责任。你可以将本服务用于商业用途，但仅限于通过本服务提供的功能、接口或相关服务进行衍生功能扩展或产品开发。你同意，不得将本服务及其相关服务或接口用于任何违反当地法律法规，或从事损害他人利益的行为。

## 已知问题

- [The server responded with a status of 200 (TitleServerBlockedError)](https://github.com/TrueRou/maimai.py/issues/21)