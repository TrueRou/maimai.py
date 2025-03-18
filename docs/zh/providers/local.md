# LocalProvider

实现：IItemListProvider, IAreaProvider

鉴于部分收藏品数据没有开放API提供，我们提供了一个本地的收藏品数据源，用于存放一些无法通过API获取的收藏品数据。

## 关于收藏品

目前包含的收藏品有：

`PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`

# 关于跑图区域

本地数据源提供了一些跑图区域的数据，提供日语原版的区域名称和中文翻译。

中文翻译文件可能不完成或过时，欢迎提交 PR 来帮助我们完善这些数据。