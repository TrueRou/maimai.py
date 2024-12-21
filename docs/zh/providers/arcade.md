# ArcadeProvider

从舞萌机台的接口通过玩家二维码获取玩家userId，进而获取分数信息

实现：IPlayerProvider, IScoreProvider

源站：WahlapAimeServer、WahlapTitleServer

PyPi: https://pypi.org/project/maimai-ffi

## 关于开源

这部分的 `maimai.py` 是不开源的，我们仅在PyPi上分发编译后的二进制包。

如果你使用的设备或者架构不受支持，请联系我们或者在Github上开Issues，我们将尽快解决您的问题。

## 关于安全性

将userId贸然提供给开发者进行保存是不安全的，我们希望 maimai.py 解析出的userId仅能在内部使用。

我们对玩家的userId进行了AES加密，在调用方法时进行解密，尽可能保证了玩家userId的安全。

有更多安全性建议可以联系我们，我们致力于保证玩家数据的安全，致力于维护舞萌机台服务器的安全。

## 免责声明

风险告知：
本服务需要连接至华立科技AIME和标题服务器，且默认的通讯协议及相关混淆原理均来源于Github开源仓库，开发者未使用软件逆向等数据和工具对任何游戏文件进行分析。本服务可能存在未知的逻辑错误，可能会导致潜在的风险如数据丢失、系统崩溃等，由用户自行决定是否下载、使用本服务。

本服务本身不提供任何侵入、修改、抓取其他应用内存及网络数据的功能，仅整合了各大开源项目提供的服务供用户自行选择，方便安全分析人员使用，减少用户的重复性劳动以及管理成本。用户只可使用本服务进行正规的学习研究或是经过合法授权的应用分析、测试等行为，若用户在使用该软件服务的过程中违背以上原则对第三方造成损失，一切责任由该用户自行承担。

任何单位或个人因下载使用本服务而产生的任何意外、疏忽、合约毁坏、诽谤、版权或知识产权侵犯及其造成的损失 (包括但不限于直接、间接、附带或衍生的损失等)，开发者不承担任何法律责任。您可以将本服务用于商业用途，但仅限于通过本服务提供的功能、接口或相关服务进行衍生功能扩展或产品开发。您同意，不得将本服务及其相关服务或接口用于任何违反当地法律法规，或从事损害他人利益的行为。