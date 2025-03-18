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

### 属性

| 字段     | 类型         | 说明     |
|----------|--------------|--------|
| `values` | `list[Area]` | 区域列表 |

### 方法

```python
def by_id(self, id: str) -> Area | None:
    """通过ID获取区域。

    参数:
        id: 区域的ID。
    返回:
        如果存在则返回对应区域，否则返回 None。
    """

def by_name(self, name: str) -> Area | None:
    """通过名称获取区域。

    参数:
        name: 区域的名称。
    返回:
        如果存在则返回对应区域，否则返回 None。
    """
```