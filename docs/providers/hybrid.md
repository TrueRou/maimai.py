# HybridProvider

实现：ISongProvider

源站：

- https://maimai.lxns.net/
- https://www.diving-fish.com/maimaidx/prober/

## 关于混合数据源

水鱼 UTAGE 曲目不包含 `notes` 信息，落雪数据源批量获取歌曲不包含 `notes` 数量

为了解决相互的问题，可以使用 `HybridProvider`，它会同时从落雪和水鱼获取数据。