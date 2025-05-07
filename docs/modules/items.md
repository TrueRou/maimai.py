# 收藏品

## maimai.items() 方法

获取收藏品列表

**支持的收藏品**：`PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`。

**支持的数据源**：`LXNSProvider`、`LocalProvider`。

### 参数

| 参数名   | 类型               | 说明                                                                |
|----------|--------------------|-------------------------------------------------------------------|
| item     | `Type[CachedType]` | 要获取的收藏品类型，例如 `PlayerIcon`                                |
| provider | `IScoreProvider`   | 覆盖默认的收藏品列表数据源，默认为 `LXNSProvider` 和 `LocalProvider` |


### 返回值

`MaimaiItems[CachedType]` 泛型对象, 例如 `MaimaiItems[PlayerIcon]`。

### 异常

| 错误名称            | 描述                     |
|---------------------|------------------------|
| `FileNotFoundError` | 无法找到本地数据文件     |
| `httpx.HTTPError`   | 由于网络问题导致请求失败 |

## MaimaiItems 对象

```python
async def get_all(self) -> list[PlayerItemType]:
    """获取所有收藏品，以列表返回。

    此方法将遍历缓存中的所有收藏品，并逐个生成每个收藏品。除非您确实需要遍历所有收藏品，否则应使用 `by_id` 或 `filter` 方法。

    返回值:
        一个列表，包含所有收藏品。
    """

async def by_id(self, id: int) -> PlayerItemType | None:
    """通过ID获取收藏品。

    参数:
        id: 收藏品的ID。
    返回值:
        如果收藏品存在则返回该收藏品，否则返回 None。
    """

async def filter(self, **kwargs) -> AsyncGenerator[PlayerItemType, None]:
    """通过属性筛选收藏品。

    确保属性属于收藏品本身，且值的类型相同。所有条件通过 AND 连接。

    参数:
        kwargs: 用于筛选收藏品的属性。
    返回值:
        一个异步生成器，生成符合所有条件的收藏品，如果没有找到则不生成任何内容。
    """
```

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.items
- https://api.maimai.turou.fun/maimai_py/maimai#MaimaiItems