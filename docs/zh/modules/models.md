# 数据模型

## Song

| 字段           | 类型                | 说明             |
|----------------|---------------------|----------------|
| `id`           | `int`               | 曲目 ID          |
| `title`        | `str`               | 曲名             |
| `artist`       | `str`               | 艺术家           |
| `genre`        | `str`               | 流派             |
| `bpm`          | `int`               | 曲目 BPM         |
| `map`          | `str \| None`       | 曲目所属区域     |
| `version`      | `int`               | 曲目首次出现版本 |
| `rights`       | `str \| None`       | 曲目版权信息     |
| `aliases`      | `list[str] \| None` | 曲目别名列表     |
| `disabled`     | `bool`              | 是否被禁用       |
| `difficulties` | `SongDifficulties`  | 谱面难度         |

额外方法:

| 方法名                                 | 返回值           | 说明                   |
|----------------------------------------|------------------|----------------------|
| `get_difficulty(SongType, LevelIndex)` | `SongDifficulty` | 直接获取对应的谱面难度 |

## SongDifficulties

| 字段       | 类型                        | 说明                   |
|------------|-----------------------------|----------------------|
| `standard` | `list[SongDifficulty]`      | 曲目标准谱面难度列表   |
| `dx`       | `list[SongDifficulty]`      | 曲目 DX 谱面难度列表   |
| `utage`    | `list[SongDifficultyUtage]` | 宴会场曲目谱面难度列表 |

## SongDifficulty

| 字段            | 类型                   | 说明              |
|-----------------|------------------------|-----------------|
| `type`          | `SongType`             | 谱面类型          |
| `level`         | `str`                  | 难度标级，如 `14+` |
| `level_value`   | `float`                | 难度定数          |
| `level_index`   | `LevelIndex`           | 难度索引          |
| `note_designer` | `str`                  | 谱师              |
| `version`       | `int`                  | 谱面首次出现版本  |
| `tap_num`       | `int`                  | TAP 物量          |
| `hold_num`      | `int`                  | HOLD 物量         |
| `slide_num`     | `int`                  | SLIDE 物量        |
| `touch_num`     | `int`                  | TOUCH 物量        |
| `break_num`     | `int`                  | BREAK 物量        |
| `curve`         | `CurveObject \| None ` | 相对难度数据      |

## SongDifficultyUtage

继承自 `SongDifficulty` 类。

| 额外字段      | 类型   | 说明                     |
|---------------|--------|------------------------|
| `kanji`       | `str`  | 宴铺前缀，如 `协`，`狂`    |
| `description` | `str`  | 宴谱描述                 |
| `is_buddy`    | `bool` | 是否为 BUDDY (双人) 谱面 |

## CurveObject

| 字段                 | 类型                  | 说明                     |
|----------------------|-----------------------|------------------------|
| `sample_size`        | `int`                 | 样本数量                 |
| `fit_level_value`    | `float`               | 拟合难度定数             |
| `avg_achievements`   | `float`               | 平均达成率               |
| `stdev_achievements` | `float`               | 达成率标准差             |
| `avg_dx_score`       | `float`               | 平均DX分数               |
| `rate_sample_size`   | `dict[RateType, int]` | 不同 `RateType` 样本数量 |
| `fc_sample_size`     | `dict[FCType, int]`   | 不同 `FCType` 样本数量   |



## PlayerIdentifier

| 字段          | 类型                     | 说明     |
|---------------|--------------------------|---------|
| `qq`          | `int \| None`            | QQ号     |
| `username`    | `str \| None`            | 用户名   |
| `friend_code` | `int \| None`            | 好友码   |
| `credentials` | `str \| Cookies \| None` | 玩家凭据 |

## PlayerTrophy

| 字段    | 类型  | 说明     |
|---------|-------|--------|
| `id`    | `int` | 称号ID   |
| `name`  | `str` | 称号名称 |
| `color` | `str` | 称号颜色 |

## PlayerIcon

| 字段    | 类型  | 说明     |
|---------|-------|--------|
| `id`    | `int` | 头像ID   |
| `name`  | `str` | 头像名称 |
| `genre` | `str` | 头像分类 |

## PlayerNamePlate

| 字段   | 类型  | 说明       |
|--------|-------|----------|
| `id`   | `int` | 姓名框ID   |
| `name` | `str` | 姓名框名称 |

## PlayerFrame

| 字段   | 类型  | 说明     |
|--------|-------|--------|
| `id`   | `int` | 背景ID   |
| `name` | `str` | 背景名称 |

## Player

| 字段     | 类型  | 说明       |
|----------|-------|----------|
| `name`   | `str` | 玩家名称   |
| `rating` | `int` | 玩家Rating |

## DivingFishPlayer

继承自 `Player` 类。

| 额外字段            | 类型  | 说明     |
|---------------------|-------|----------|
| `nickname`          | `str` | 玩家昵称 |
| `plate`             | `str` | 玩家牌子 |
| `additional_rating` | `int` |          |

## LXNSPlayer

继承自 `Player` 类。

| 额外字段      | 类型                      | 说明                    |
|---------------|---------------------------|-----------------------|
| `friend_code` | `int`                     | 玩家好友码              |
| `trophy`      | `PlayerTrophy`            | 玩家称号                |
| `course_rank` | `int`                     | 段位 ID                 |
| `class_rank`  | `int`                     | 阶级 ID                 |
| `star`        | `int`                     | 搭档觉醒数              |
| `icon`        | `PlayerIcon \| None`      | 头像                    |
| `name_plate`  | `PlayerNamePlate \| None` | 姓名框                  |
| `frame`       | `PlayerFrame \| None`     | 背景                    |
| `upload_time` | `str`                     | 玩家被同步时的 UTC 时间 |

## ArcadePlayer

继承自 `Player` 类。

| 额外字段     | 类型   | 说明                 |
|--------------|--------|--------------------|
| `is_login`   | `bool` | 玩家目前是否已经登录 |
| `trophy`     | `int`  | 玩家称号ID           |
| `icon`       | `int`  | 头像ID               |
| `name_plate` | `int`  | 姓名框ID             |

## Score

| 字段           | 类型             | 说明              |
|----------------|------------------|-------------------|
| `id`           | `int`            | 曲目ID            |
| `song_name`    | `str`            | 曲名              |
| `level`        | `str`            | 难度标级，如 `14+` |
| `level_index`  | `LevelIndex`     | 难度索引          |
| `achievements` | `float \| None`  | 达成率            |
| `fc`           | `FCType`         | FULL COMBO 类型   |
| `fs`           | `FSType`         | FULL SYNC 类型    |
| `dx_score`     | `int \| None`    | DX分数            |
| `dx_rating`    | `float \| None`  | DX Rating         |
| `rate`         | `RateType`       | 评级类型          |
| `type`         | `SongType`       | 谱面类型          |
| `song`         | `Song`           | 对应曲目对象      |
| `difficulty`   | `SongDifficulty` | 对应难度对象      |

## PlateObject

| 字段     | 类型                  | 说明         |
|----------|-----------------------|------------|
| `song`   | `Song`                | 歌曲         |
| `levels` | `list[LevelIndex]`    | 难度索引列表 |
| `score`  | `list[Score] \| None` | 成绩列表     |

## PlayerRegion

| 字段          | 类型       | 说明           |
|---------------|------------|--------------|
| `region_id`   | `int`      | 地区ID         |
| `region_name` | `str`      | 地区名称       |
| `play_count`  | `int`      | 游玩次数       |
| `created_at`  | `datetime` | 第一次游玩时间 |