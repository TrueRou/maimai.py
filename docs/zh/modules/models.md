# 音乐和玩家数据模型

## SongDifficulty 数据类

### 属性

| 字段             | 类型                 | 说明                     |
|------------------|----------------------|------------------------|
| `type`          | `SongType`           | 难度类型。               |
| `difficulty`    | `LevelIndex`         | 难度等级。               |
| `level`         | `str`                | 难度等级名称。           |
| `level_value`   | `float`              | 难度等级数值。           |
| `note_designer` | `str`                | 谱面设计者。             |
| `version`       | `int`                | 版本号。                 |
| `tap_num`       | `int`                | 敲击数。                 |
| `hold_num`      | `int`                | 长按数。                 |
| `slide_num`     | `int`                | 滑键数。                 |
| `touch_num`     | `int`                | 触摸数。                 |
| `break_num`     | `int`                | 断连数。                 |

## SongDifficultyUtage 数据类

### 属性

| 字段           | 类型                 | 说明                     |
|----------------|----------------------|------------------------|
| `kanji`        | `str`                | 日文名。                 |
| `description`  | `str`                | 描述。                   |
| `is_buddy`     | `bool`               | 是否为好友谱面。         |
| `tap_num`      | `int`                | 敲击数。                 |
| `hold_num`     | `int`                | 长按数。                 |
| `slide_num`    | `int`                | 滑键数。                 |
| `touch_num`    | `int`                | 触摸数。                 |
| `break_num`    | `int`                | 断连数。                 |

## SongDifficulties 数据类

### 属性

| 字段         | 类型                     | 说明                     |
|-------------|--------------------------|------------------------|
| `standard`   | `list[SongDifficulty]`    | 标准难度列表。           |
| `dx`        | `list[SongDifficulty]`    | DX难度列表。             |
| `utage`     | `list[SongDifficultyUtage]`| Utage难度列表。          |

## Song 数据类

### 属性

| 字段             | 类型                 | 说明                     |
|------------------|----------------------|------------------------|
| `id`             | `int`                | 歌曲ID。                 |
| `title`          | `str`                | 歌曲标题。               |
| `artist`         | `str`                | 艺术家。                |
| `genre`          | `str`                | 流派。                  |
| `bpm`            | `int`                | 每分钟节拍数。           |
| `map`            | `str | None`         | 谱面映射。               |
| `version`        | `int`                | 版本号。                 |
| `rights`         | `str | None`         | 版权信息。               |
| `aliases`        | `list[str] | None`   | 别名列表。               |
| `disabled`       | `bool`               | 是否禁用。               |
| `difficulties`   | `SongDifficulties`    | 难度信息。               |

### 方法

```python
def get_levels(self, exclude_remaster: bool = False) -> list[LevelIndex]:
    """获取歌曲的等级索引。

    参数:
        exclude_remaster: 是否排除ReMASTER等级索引。
    返回:
        歌曲的等级索引列表。
    """

def get_diff(self, type: SongType, level_index: LevelIndex) -> SongDifficulty | None:
    """通过类型和等级索引获取歌曲的难度。

    参数:
        type: 难度类型，例如 `SongType.DX`。
        level_index: 等级索引，例如 `LevelIndex.MASTER`。
    返回:
        难度信息，如果不存在则返回 None。
    """
```

## PlayerIdentifier 数据类

### 属性

| 字段             | 类型                     | 说明                     |
|------------------|--------------------------|------------------------|
| `qq`             | `int | None`             | QQ号。                   |
| `username`       | `str | None`             | 用户名。                 |
| `friend_code`    | `int | None`             | 好友码。                 |
| `credentials`    | `str | Cookies | None` | 凭证。                  |

### 方法

## ArcadeResponse 数据类

### 属性

| 字段             | 类型                 | 说明                     |
|------------------|----------------------|------------------------|
| `errno`          | `int | None`         | 错误代码。               |
| `errmsg`         | `str | None`         | 错误信息。               |
| `data`           | `dict[str, Any] | bytes | list[Any] | None` | 数据。 |

## PlayerTrophy 数据类

### 属性

| 字段     | 类型             | 说明                     |
|-----------------|------------------|------------------------|
| `id`         | `int`           | 奖杯ID。                 |
| `name`       | `str`           | 奖杯名称。               |
| `color`      | `str`           | 奖杯颜色。               |

## PlayerIcon 数据类

### 属性

| 字段     | 类型             | 说明                     |
|-----------------|------------------|------------------------|
| `id`         | `int`           | 图标ID。                 |
| `name`       | `str`           | 图标名称。               |
| `genre`      | `str`           | 图标流派。               |

## PlayerNamePlate 数据类

### 属性

| 字段     | 类型             | 说明                     |
|-----------------|------------------|------------------------|
| `id`         | `int`           | 名牌ID。                 |
| `name`       | `str`           | 名称名称。               |

## PlayerFrame 数据类

### 属性

| 字段     | 类型             | 说明                     |
|-----------------|------------------|------------------------|
| `id`         | `int`           | 框架ID。                 |
| `name`       | `str`           | 框架名称。               |

## Player 数据类

### 属性

| 字段     | 类型             | 说明                     |
|-----------------|------------------|------------------------|
| `name`       | `str`           | 玩家名称。               |
| `rating`     | `int`           | 玩家评分。               |

## DivingFishPlayer 数据类

继承自 `Player` 类。

### 属性

| 字段           | 类型             | 说明                     |
|----------------|------------------|------------------------|
| `nickname`     | `str`           | 玩家昵称。               |
| `plate`        | `str`           | 玩家徽章。               |
| `additional_rating` | `int` | 玩家额外评分。          |

## LXNSPlayer 数据类

继承自 `Player` 类。

### 属性

| 字段             | 类型                     | 说明                     |
|------------------|--------------------------|------------------------|
| `friend_code`    | `int`                    | 玩家好友码。             |
| `trophy`        | `PlayerTrophy`           | 玩家奖杯。               |
| `course_rank`    | `int`                    | 玩家课程排名。           |
| `class_rank`     | `int`                    | 玩家班级排名。           |
| `star`           | `int`                    | 玩家星级。               |
| `icon`          | `PlayerIcon | None`       | 玩家图标。               |
| `name_plate`     | `PlayerNamePlate | None` | 玩家名牌。              |
| `frame`          | `PlayerFrame | None`     | 玩家框架。              |
| `upload_time`    | `str`                   | 玩家数据上传时间。        |

## SongAlias 数据类

### 属性

| 字段           | 类型             | 说明                     |
|----------------|------------------|------------------------|
| `song_id`      | `int`           | 歌曲ID。                 |
| `aliases`      | `list[str]`      | 别名列表。               |

## Score 数据类

### 属性

| 字段             | 类型                 | 说明                     |
|------------------|----------------------|------------------------|
| `id`             | `int`                | 分数ID。                 |
| `song_name`      | `str`                | 歌曲名称。               |
| `level`          | `str`                | 等级名称。               |
| `level_index`    | `LevelIndex`         | 等级索引。               |
| `achievements`   | `float | None`       | 成就值。                 |
| `fc`             | `FCType`             | FC类型。                 |
| `fs`             | `FSType`             | FS类型。                 |
| `dx_score`       | `int | None`         | DX分数。                 |
| `dx_rating`      | `float | None`       | DX评分。                 |
| `rate`           | `RateType`           | 评分。                   |
| `type`           | `SongType`           | 类型。                   |

### 方法

```python
def compare(self, other: "Score") -> "Score":
    """比较两个分数，返回更好的分数。"""
```

## PlateObject 数据类

### 属性

| 字段     | 类型                     | 说明                     |
|-----------------|------------------|------------------------|
| `song`       | `Song`           | 歌曲对象。               |
| `levels`      | `list[LevelIndex]` | 等级索引列表。           |
| `score`       | `list[Score] | None` | 分数列表。               |

