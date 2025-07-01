# 区域

区域（日语：ちほー，中文：区域）是自 maimai でらっくす 起引入的概念，指的是游戏中的跑图区域。

区域中包含了可解锁的旅行伙伴、收藏品，以及课题曲等相关内容。

![image.png](https://s2.loli.net/2025/07/09/klCR4hJWDLoMF89.png)

## maimai.areas() 方法

通过 [`maimai.areas()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.areas) 方法可以获取区域的封装对象，以 `MaimaiAreas` 的形式返回。

阅读 [MaimaiAreas 定义](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiAreas)，可以了解获取单个区域、遍历所有区域等方法。

参考 [Area 模型](../concepts/models.md#area)，可以了解具体数据结构。

### 示例代码

#### 通过 ID 获取区域

```python
areas = await client.areas()
heaven4 = await areas.by_id("heaven4")
print(heaven4.name) # 天界ちほー4
print(heaven4.description) # ……この身は穢れ、もう天界には戻れない。
```

#### 遍历所有区域

```python
areas = await client.areas()
all_areas = [area.name for area in await areas.get_all()]
print(all_areas) # ['天界ちほー1', '天界ちほー2', '天界ちほー3', '天界ちほー4', ...]
```

### 补充说明

`maimai.areas()` 方法可以提供 `lang` 参数来指定语言，默认为 `jp` （日语），可选值包括：(`jp`, `zh`)。

目前的区域数据来自于本地 JSON 文件，如果您希望更新或贡献区域数据，请参考 [CONTRIBUTING.md](https://github.com/TrueRou/maimai.py/blob/main/.github/CONTRIBUTING.md)