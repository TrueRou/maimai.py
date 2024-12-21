---
# https://vitepress.dev/reference/default-theme-home-page
layout: home

hero:
  name: "maimai.py"
  text: "舞萌Python工具库"
  tagline: 用于国服舞萌相关开发的最佳Python工具库，封装水鱼/落雪查分器常用函数。
  actions:
    - theme: brand
      text: 开始使用
      link: /zh/get-started
    - theme: alt
      text: Demo 演示
      link: /zh/examples
    - theme: alt
      text: ⭐
      link: https://github.com/TrueRou/maimai.py

features:
  - title: 统一模型
    details: 提供了基于日服舞萌标准的数据模型和接口，为水鱼、落雪、华立分别做了数据源实现。
  - title: 查询信息
    details: 支持从数据源查询歌曲、谱面、玩家信息、分数、Rating、姓名框、牌子进度。
  - title: 上传数据
    details: 支持将玩家成绩上传至数据源：目前支持上传至水鱼和落雪查分器。
  - title: 扩展查分
    details: 特别的，我们支持从华立获取玩家成绩：目前支持通过微信代理或玩家二维码来查询成绩。
---

