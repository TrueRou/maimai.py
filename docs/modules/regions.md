# 游玩地区

## maimai.regions() 方法

从数据源获取玩家游玩地区的相关信息。

**支持的数据源**：`ArcadeProvider`。

### 参数

| 参数名     | 类型               | 说明                                               |
|------------|--------------------|--------------------------------------------------|
| identifier | `PlayerIdentifier` | 玩家标识，例如 `PlayerIdentifier(username="turou")` |
| provider   | `IRegionProvider`  | 数据源，默认为 `ArcadeProvider`                     |

### 返回值

`list[PlayerRegion]` 对象

### 异常

| 错误名称                  | 描述                                           |
|---------------------------|----------------------------------------------|
| `TitleServerNetworkError` | 舞萌 官方服务器相关错误，可能是网络问题         |
| `TitleServerBlockedError` | 舞萌 官方服务器拒绝了请求，可能是因为 IP 被过滤 |
| `ArcadeIdentifierError`   | 舞萌 用户 ID 无效，或者用户未找到               |

## API 文档

- https://api.maimai.turou.fun/maimai_py.html#MaimaiClient.regions