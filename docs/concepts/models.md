# 数据模型

## [Song](https://api.maimai.turou.fun/maimai_py/models.html#Song)

| 字段           | 类型                | 说明             |
|----------------|---------------------|----------------|
| `id`           | `int`               | 曲目 ID          |
| `title`        | `str`               | 曲名             |
| `artist`       | `str`               | 艺术家           |
| `genre`        | `Genre`             | 流派             |
| `bpm`          | `int`               | 曲目 BPM         |
| `map`          | `str \| None`       | 曲目所属区域     |
| `version`      | `int`               | 曲目首次出现版本 |
| `rights`       | `str \| None`       | 曲目版权信息     |
| `aliases`      | `list[str] \| None` | 曲目别名列表     |
| `disabled`     | `bool`              | 是否被禁用       |
| `difficulties` | `SongDifficulties`  | 谱面难度         |

额外方法:

| 方法名                                           | 返回值                 | 说明                           |
|--------------------------------------------------|------------------------|------------------------------|
| `get_difficulty(SongType, LevelIndex \| int)`    | `SongDifficulty`       | 获取对应的难度                 |
| `get_difficulties(SongType)`                     | `list[SongDifficulty]` | 获取对应的难度列表             |
| `get_divingfish_id(SongType, LevelIndex \| int)` | `int`                  | 获取歌曲对应难度的 水鱼 ID      |
| `get_divingfish_ids(SongType)`                   | `set[int]`             | 获取歌曲对应类型的 水鱼 ID 集合 |

## [SongDifficulties](https://api.maimai.turou.fun/maimai_py/models.html#SongDifficulties)

| 字段       | 类型                        | 说明                   |
|------------|-----------------------------|----------------------|
| `standard` | `list[SongDifficulty]`      | 曲目标准谱面难度列表   |
| `dx`       | `list[SongDifficulty]`      | 曲目 DX 谱面难度列表   |
| `utage`    | `list[SongDifficultyUtage]` | 宴会场曲目谱面难度列表 |

## [SongDifficulty](https://api.maimai.turou.fun/maimai_py/models.html#SongDifficulty)

| 字段             | 类型                   | 说明              |
|------------------|------------------------|-----------------|
| `type`           | `SongType`             | 谱面类型          |
| `level`          | `str`                  | 难度标级，如 `14+` |
| `level_value`    | `float`                | 难度定数          |
| `level_index`    | `LevelIndex`           | 难度索引          |
| `level_dx_score` | `int`                  | 难度最大 DX 分数  |
| `note_designer`  | `str`                  | 谱师              |
| `version`        | `int`                  | 谱面首次出现版本  |
| `tap_num`        | `int`                  | TAP 物量          |
| `hold_num`       | `int`                  | HOLD 物量         |
| `slide_num`      | `int`                  | SLIDE 物量        |
| `touch_num`      | `int`                  | TOUCH 物量        |
| `break_num`      | `int`                  | BREAK 物量        |
| `curve`          | `CurveObject \| None ` | 相对难度数据      |

## [SongDifficultyUtage](https://api.maimai.turou.fun/maimai_py/models.html#SongDifficultyUtage)

继承自 `SongDifficulty` 类。

| 额外字段      | 类型   | 说明                     |
|---------------|--------|------------------------|
| `kanji`       | `str`  | 宴铺前缀，如 `协`，`狂`    |
| `description` | `str`  | 宴谱描述                 |
| `diff_id`     | `int`  | 宴谱难度 ID              |
| `is_buddy`    | `bool` | 是否为 BUDDY（双人）谱面 |

## [CurveObject](https://api.maimai.turou.fun/maimai_py/models.html#CurveObject)

| 字段                 | 类型                  | 说明                     |
|----------------------|-----------------------|------------------------|
| `sample_size`        | `int`                 | 样本数量                 |
| `fit_level_value`    | `float`               | 拟合难度定数             |
| `avg_achievements`   | `float`               | 平均达成率               |
| `stdev_achievements` | `float`               | 达成率标准差             |
| `avg_dx_score`       | `float`               | 平均 DX 分数               |
| `rate_sample_size`   | `dict[RateType, int]` | 不同 `RateType` 样本数量 |
| `fc_sample_size`     | `dict[FCType, int]`   | 不同 `FCType` 样本数量   |

## [PlayerIdentifier](https://api.maimai.turou.fun/maimai_py/models.html#PlayerIdentifier)

| 字段          | 类型                                      | 说明     |
|---------------|-------------------------------------------|---------|
| `qq`          | `int \| None`                             | QQ 号     |
| `username`    | `str \| None`                             | 用户名   |
| `friend_code` | `int \| None`                             | 好友码   |
| `credentials` | `str \| MutableMapping[str, Any] \| None` | 玩家凭据 |

## [Score](https://api.maimai.turou.fun/maimai_py/models.html#Score)

| 字段           | 类型            | 说明              |
|----------------|-----------------|-------------------|
| `id`           | `int`           | 成绩 ID            |
| `level`        | `str`           | 难度标级，如 `14+` |
| `level_index`  | `LevelIndex`    | 难度索引          |
| `achievements` | `float \| None` | 达成率            |
| `fc`           | `FCType`        | FULL COMBO 类型   |
| `fs`           | `FSType`        | FULL SYNC 类型    |
| `dx_score`     | `int \| None`   | DX 分数            |
| `dx_rating`    | `float \| None` | DX Rating         |
| `play_count`   | `int \| None`   | 游玩次数          |
| `rate`         | `RateType`      | 评级类型          |
| `type`         | `SongType`      | 谱面类型          |

## [ScoreExtend](https://api.maimai.turou.fun/maimai_py/models.html#ScoreExtend)

继承自 `Score` 类。

| 字段             | 类型         | 说明             |
|------------------|--------------|----------------|
| `title`          | `int`        | 曲目标题         |
| `level_value`    | `LevelIndex` | 难度定数         |
| `level_dx_score` | `LevelIndex` | 难度最大 DX 分数 |

## [PlateObject](https://api.maimai.turou.fun/maimai_py/models.html#PlateObject)

| 字段     | 类型                | 说明     |
|----------|---------------------|--------|
| `song`   | `Song`              | 歌曲     |
| `levels` | `list[LevelIndex]`  | 关联难度 |
| `scores` | `list[ScoreExtend]` | 成绩列表 |

## [PlayerSong](https://api.maimai.turou.fun/maimai_py/models.html#PlayerSong)

| 字段     | 类型                | 说明     |
|----------|---------------------|--------|
| `song`   | `Song`              | 歌曲     |
| `scores` | `list[ScoreExtend]` | 成绩列表 |

## [PlayerBests](https://api.maimai.turou.fun/maimai_py/models.html#PlayerBests)

| 字段         | 类型                | 说明              |
|--------------|---------------------|-----------------|
| `rating`     | `int`               | 玩家 Rating       |
| `rating_b35` | `int`               | 玩家 B35 Rating   |
| `rating_b15` | `int`               | 玩家 B15 Rating   |
| `scores`     | `list[ScoreExtend]` | 玩家 分数列表     |
| `scores_b35` | `list[ScoreExtend]` | 玩家 B35 分数列表 |
| `scores_b15` | `list[ScoreExtend]` | 玩家 B15 分数列表 |

## [PlayerTrophy](https://api.maimai.turou.fun/maimai_py/models.html#PlayerTrophy)

| 字段    | 类型  | 说明     |
|---------|-------|--------|
| `id`    | `int` | 称号 ID   |
| `name`  | `str` | 称号名称 |
| `color` | `str` | 称号颜色 |

## [PlayerIcon](https://api.maimai.turou.fun/maimai_py/models.html#PlayerIcon)

| 字段          | 类型          | 说明     |
|---------------|---------------|--------|
| `id`          | `int`         | 头像 ID   |
| `name`        | `str`         | 头像名称 |
| `description` | `str \| None` | 头像描述 |
| `genre`       | `str \| None` | 头像分类 |

## [PlayerNamePlate](https://api.maimai.turou.fun/maimai_py/models.html#PlayerNamePlate)

| 字段          | 类型          | 说明       |
|---------------|---------------|----------|
| `id`          | `int`         | 姓名框 ID   |
| `name`        | `str`         | 姓名框名称 |
| `description` | `str \| None` | 姓名框描述 |
| `genre`       | `str \| None` | 姓名框分类 |

## [PlayerFrame](https://api.maimai.turou.fun/maimai_py/models.html#PlayerFrame)

| 字段          | 类型          | 说明     |
|---------------|---------------|--------|
| `id`          | `int`         | 背景 ID   |
| `name`        | `str`         | 背景名称 |
| `description` | `str \| None` | 背景描述 |
| `genre`       | `str \| None` | 背景分类 |

## [PlayerPartner](https://api.maimai.turou.fun/maimai_py/models.html#PlayerPartner)

| 字段   | 类型  | 说明         |
|--------|-------|------------|
| `id`   | `int` | 旅行伙伴 ID   |
| `name` | `str` | 旅行伙伴名称 |

## [PlayerChara](https://api.maimai.turou.fun/maimai_py/models.html#PlayerChara)

| 字段   | 类型  | 说明     |
|--------|-------|--------|
| `id`   | `int` | 角色 ID   |
| `name` | `str` | 角色名称 |

## [Player](https://api.maimai.turou.fun/maimai_py/models.html#Player)

| 字段     | 类型  | 说明       |
|----------|-------|----------|
| `name`   | `str` | 玩家名称   |
| `rating` | `int` | 玩家Rating |

## [DivingFishPlayer](https://api.maimai.turou.fun/maimai_py/models.html#DivingFishPlayer)

继承自 `Player` 类。

| 额外字段            | 类型  | 说明     |
|---------------------|-------|----------|
| `nickname`          | `str` | 玩家昵称 |
| `plate`             | `str` | 玩家牌子 |
| `additional_rating` | `int` |          |

## [LXNSPlayer](https://api.maimai.turou.fun/maimai_py/models.html#LXNSPlayer)

继承自 `Player` 类。

| 额外字段      | 类型                      | 说明                    |
|---------------|---------------------------|-----------------------|
| `friend_code` | `int`                     | 玩家好友码              |
| `course_rank` | `int`                     | 段位 ID                 |
| `class_rank`  | `int`                     | 阶级 ID                 |
| `star`        | `int`                     | 搭档觉醒数              |
| `frame`       | `PlayerFrame \| None`     | 背景                    |
| `icon`        | `PlayerIcon \| None`      | 头像                    |
| `trophy`      | `PlayerTrophy`            | 玩家称号                |
| `name_plate`  | `PlayerNamePlate \| None` | 姓名框                  |
| `upload_time` | `str`                     | 玩家被同步时的 UTC 时间 |

## [ArcadePlayer](https://api.maimai.turou.fun/maimai_py/models.html#ArcadePlayer)

继承自 `Player` 类。

| 额外字段     | 类型   | 说明                 |
|--------------|--------|--------------------|
| `is_login`   | `bool` | 玩家目前是否已经登录 |
| `trophy`     | `int`  | 玩家称号 ID           |
| `icon`       | `int`  | 头像 ID               |
| `name_plate` | `int`  | 姓名框 ID             |

## [PlayerRegion](https://api.maimai.turou.fun/maimai_py/models.html#PlayerRegion)

| 字段          | 类型       | 说明           |
|---------------|------------|--------------|
| `region_id`   | `int`      | 地区 ID         |
| `region_name` | `str`      | 地区名称       |
| `play_count`  | `int`      | 游玩次数       |
| `created_at`  | `datetime` | 第一次游玩时间 |

## [AreaCharacter](https://api.maimai.turou.fun/maimai_py/models.html#AreaCharacter)

| 字段           | 类型             | 说明             |
|----------------|------------------|----------------|
| `name`         | `str`            | 角色名称         |
| `illustrator`  | `str`            | 插画师           |
| `description1` | `str`            | 角色衬线字体描述 |
| `description2` | `str`            | 角色详细描述     |
| `team`         | `str`            | 角色队伍         |
| `props`        | `dict[str, str]` | 角色属性         |

## [AreaSong](https://api.maimai.turou.fun/maimai_py/models.html#AreaSong)

| 字段          | 类型          | 说明     |
|---------------|---------------|--------|
| `id`          | `int`         | 曲目ID   |
| `title`       | `str`         | 曲名     |
| `artist`      | `str`         | 艺术家   |
| `description` | `str`         | 曲目描述 |
| `illustrator` | `str \| None` | 插画师   |
| `movie`       | `str \| None` | 视频来源 |

## [Area](https://api.maimai.turou.fun/maimai_py/models.html#Area)

| 字段          | 类型                  | 说明              |
|---------------|-----------------------|-----------------|
| `id`          | `str`                 | 区域ID            |
| `name`        | `str`                 | 区域名称          |
| `comment`     | `str`                 | 区域评论          |
| `description` | `str`                 | 区域描述          |
| `video_id`    | `str`                 | 区域 Youtube 视频 ID |
| `characters`  | `list[AreaCharacter]` | 角色列表          |
| `songs`       | `list[AreaSong]`      | 曲目列表          |