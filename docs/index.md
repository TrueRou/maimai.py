---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "maimai.py"
  text: "舞萌相关开发的最佳Python工具库"
  tagline: 用于国服舞萌相关开发的最佳Python工具库。支持水鱼、落雪、机台等数据源。支持曲目、玩家、分数、牌子等各类信息的查询。
  image:
    src: https://s2.loli.net/2024/12/23/jOngPm1bECdSw5N.png
  actions:
    - theme: brand
      text: 开始使用
      link: /get-started
    - theme: alt
      text: Demo 演示
      link: /examples
    - theme: alt
      text: ⭐
      link: https://github.com/TrueRou/maimai.py

features:
  - title: 统一模型
    details: 提供了基于日服舞萌标准的数据模型和接口。另外，我们还提供了基于RESTful范式的客户端，您可以使用任何语言来调用。
  - title: 查询信息
    details: 支持从数据源查询歌曲、谱面、玩家信息、分数、Rating、姓名框、牌子进度、旅行区域、收藏品。
  - title: 上传数据
    details: 支持将玩家成绩上传至数据源：目前支持上传分数至水鱼和落雪查分器。
  - title: 扩展查分
    details: 特别的，我们支持从机台数据源获取成绩：目前支持通过微信代理或玩家二维码来查询成绩。
---

