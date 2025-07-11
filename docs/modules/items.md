# 收藏品

コレクション（收藏品）是maimai でらっくす的奖励内容之一，包括头像、姓名框、背景、称号、搭档等种类。玩家可以通过多种方式获取收藏品，并通过选中特定收藏品作为玩家信息展示。

## maimai.items() 方法

通过 [`maimai.items()`](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiClient.items) 方法可以获取某一种类收藏品的封装对象，以 `MaimaiItems[Type]` 泛型的形式返回。

阅读 [MaimaiItems 定义](https://api.maimai.turou.fun/maimai_py/maimai.html#MaimaiItems)，可以了解获取单个收藏品、遍历所有收藏品等方法。

参考 [PlayerIcon 模型](../concepts/models.md#playericon)，可以了解具体数据结构。

**支持的收藏品**：`PlayerIcon`, `PlayerNamePlate`, `PlayerFrame`, `PlayerTrophy`, `PlayerChara`, `PlayerPartner`。

### 遍历所有搭档

```python
items = await maimai.items(PlayerPartner)
all_icons = [icon.name for icon in await items.get_all()]
print(all_icons)  # ['でらっくま', '乙姫', ...]
```

### 返回头像和对应图片链接

```python
resource_base = "https://assets2.lxns.net/maimai/icon/"
items = await maimai.items(PlayerPartner)
partner_images = {partner.name: resource_base + f"{partner.id}.png" for partner in await items.get_all()}
print(partner_images)  # {'デフォルト': 'https://assets2.lxns.net/maimai/icon/1.png', ...}
```