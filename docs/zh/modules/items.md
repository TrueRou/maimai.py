# 收藏品

## maimai.items() 方法

获取收藏品列表

**支持的收藏品**：`PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`。

**支持的数据源**：`LXNSProvider`、`LocalProvider`。

### 参数

| 参数名   | 类型               | 说明                                                                |
|----------|--------------------|-------------------------------------------------------------------|
| item     | `Type[CachedType]` | 要获取的收藏品类型，例如 `PlayerIcon`                                |
| flush    | `bool`             | 是否刷新缓存，默认为 `False`                                         |
| provider | `IScoreProvider`   | 覆盖默认的收藏品列表数据源，默认为 `LXNSProvider` 和 `LocalProvider` |


### 返回值

`MaimaiItems[CachedType]` 泛型对象

### 异常

| 错误名称            | 描述                     |
|---------------------|------------------------|
| `FileNotFoundError` | 无法找到本地数据文件     |
| `RequestError`      | 由于网络问题导致请求失败 |

## MaimaiItems 对象

### 属性

| 字段     | 类型               | 说明       |
|----------|--------------------|----------|
| `values` | `list[CachedType]` | 收藏品列表 |

### 方法

```python
def by_id(self, id: int) -> CachedType | None:
    """通过ID获取收藏品。

    参数:
        id: 收藏品的ID。
    返回:
        如果存在则返回对应收藏品，否则返回 None。
    """

def filter(self, **kwargs) -> list[CachedType]:
    """根据属性筛选收藏品。

    请确保属性存在，并且类型匹配。所有条件通过 AND 连接。

    参数:
        kwargs: 用于筛选收藏品的属性。
    返回:
        匹配所有条件的收藏品列表，如果没有找到则返回空列表。
    """
```