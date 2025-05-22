# HybridProvider

实现：ISongProvider

源站：

- https://maimai.lxns.net/
- https://www.diving-fish.com/maimaidx/prober/

## 关于混合数据源

落雪提供了更新较快的歌曲数据源，但是缺少歌曲的 Notes 相关信息

水鱼提供了较全的歌曲信息，但是 UTAGE 曲目和部分新曲缺少数据

如果您需要更新较快的歌曲数据源，并且需要 Notes 相关信息，可以使用 `HybridProvider`，它会同时从落雪和水鱼获取数据。