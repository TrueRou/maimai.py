# 游玩地区

## maimai.regions() 方法

从数据源（目前只支持机台数据源）获取玩家游玩地区的相关信息。

**支持的数据源**：`ArcadeProvider`。

### 参数

| 参数名     | 类型               | 说明                                               |
|------------|--------------------|--------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(username="turou")` |
| provider   | `IRegionProvider`  | 数据源，默认为 `ArcadeProvider`                     |

### 返回值

`list[PlayerRegion]` 对象

### 异常

| 错误名称           | 描述                                      |
|--------------------|-----------------------------------------|
| `TitleServerError` | 舞萌标题服务器的相关错误，可能是网络问题   |
| `ArcadeError`      | 舞萌 Response 非法，或者提供的玩家标识有误 |