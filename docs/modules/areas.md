# 区域

## maimai.areas() 方法

获取跑图区域相关信息

**支持的数据源**：`LocalProvider`。

### 参数

| 参数名   | 类型                  | 说明                          |
|----------|-----------------------|-----------------------------|
| lang     | `Literal['ja', 'zh']` | 数据的本地化语言，默认为`ja`   |
| provider | `IAreaProvider`       | 数据源，默认为 `LocalProvider` |

### 返回值

`MaimaiAreas` 对象

### 异常

| 错误名称            | 描述                 |
|---------------------|--------------------|
| `FileNotFoundError` | 无法找到本地数据文件 |

## MaimaiAreas 对象

```python
async def get_all(self) -> list[Area]:
    """获取所有区域，以列表返回。

    此方法将遍历缓存中的所有区域。除非您确实需要遍历所有区域，否则应该使用 `by_id` 或 `by_name` 代替。

    返回值:
        一个列表，包含所有区域。
    """

async def get_batch(self, ids: Iterable[str]) -> list[Area]:
    """通过ID批量获取区域。

    参数:
        ids: 区域的ID列表。
    返回值:
        一个列表，包含存在的区域，如果没有匹配的区域则返回空列表。
    """

async def by_id(self, id: str) -> Area | None:
    """通过ID获取区域。

    参数:
        id: 区域的ID。
    返回值:
        如果区域存在则返回该区域，否则返回None。
    """

async def by_name(self, name: str) -> Area | None:
    """通过名称获取区域，区分语言。

    参数:
        name: 区域的名称。
    返回值:
        如果区域存在则返回该区域，否则返回None。
    """
```

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.areas
- https://api.maimai.turou.fun/maimai_py/maimai#MaimaiAreas