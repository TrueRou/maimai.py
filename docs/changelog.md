# 更新日志

## 1.3.2 (2025-07-10)

Features:
  - 完全重构文档 -> [#33](https://github.com/TrueRou/maimai.py/issues/33)

Bugfixes:
  - 修复使用 Redis 缓存时，初始化空成绩列表时抛出异常的问题
  - 修复别名异常覆盖的问题 -> [#34](https://github.com/TrueRou/maimai.py/issues/34)

## 1.3.1 (2025-06-29)

Features:
  - 引入 MaimaiClientMultithreading 来保证单例 -> [#29](https://github.com/TrueRou/maimai.py/pull/29)
  - 在静态数据类型中添加更多功能方法 -> [#28](https://github.com/TrueRou/maimai.py/issues/28)

Bugfixes:
  - 修复误以为国服存在 `maimai でらっくす PLUS` 的 20000 版本号问题
  - 使用 Arcade 数据源获取分数时有时会抛出 ValueError 异常 -> [#25](https://github.com/TrueRou/maimai.py/issues/25)
  - `maimai.bests()` 可能返回超过50个成绩 -> [#32](https://github.com/TrueRou/maimai.py/issues/32)
  - dataclasses 没有正确使用 __slots__ -> [02f6189](https://github.com/TrueRou/maimai.py/commit/02f61892144ff6ac7eea3181452c9aefd4514bc3)

**Breaking Changes**:
  - MaimaiScores 的 `by_song()`, `filter()` 直接返回列表，不再是迭代器
  - `maimai.minfo()` 现在返回一个结构化的 PlayerSong 对象，不再是元组
  - `maimai_scores.get_distinct()` 被删除，因为它的功能已经被 `maimai_scores.configure()` 替代

## 1.3.0 (2025-06-19)

Features:
  - **开始支持 Python 3.9**
  - 暴露全新的 MaimaiRoutes 作为 API 拓展 -> [982a2ff](https://github.com/TrueRou/maimai.py/commit/982a2ff32edadc2e71be8ff8505a8152467cfd49)
  - 修复被机台封锁后返回 200 的问题 -> [3bc7830](https://github.com/TrueRou/maimai.py/commit/3bc7830fa5ca047cd2567badc747825ae2bba28e)
  - 添加 maimai.bests() 方法来获取 B50 成绩
  - 添加 maimai.minfo() 方法来获取 歌曲 + 歌曲成绩
  - 机台数据源获取分数时会携带 `play_count` 游玩次数数据

Bugfixes:
  - 基于状态码识别的特殊处理异常无法正常抛出 -> [#22](https://github.com/TrueRou/maimai.py/issues/22)

**Breaking Changes**:
  - MaimaiItems 的 `filter()` 直接返回列表，不再是迭代器
  - MaimaiSongs 的 `by_artist()`, `by_genre()`, `by_bpm()`, `by_versions()`, `by_keywords()`, `filter()` 直接返回列表，不再是迭代器
  - PlateObject 的结构更改为 `song: Song, levels: set[LevelIndex], scores: list[Score]` 而不再是单独的 PlateSong 和 PlateScore