# 游玩地区

通过**机台✨**接口，我们可以获取玩家游玩过的地区。这些信息包括玩家在哪些省份游玩过，游玩的次数等等。

## maimai.regions() 方法

调用 [`maimai.regions()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.regions) 方法，会返回对应玩家的 [`PlayerRegion`](../concepts/models.md#playerregion) 对象列表。

### 获取玩家游玩地区

```python
identifier = "encrypt:player:userId:1234567890"
regions = await maimai.regions(identifier)
for region in regions:
    print(f"省份: {region.region_name}, 游玩次数: {region.play_count}")
```