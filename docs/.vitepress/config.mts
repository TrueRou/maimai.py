import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "maimai.py",
  description: "用于舞萌DX相关开发的最佳Python工具库, 封装水鱼/落雪查分器常用函数.",
  themeConfig: {
    nav: [
      { text: '主页', link: '/zh' },
      { text: '指南', link: '/get-started' },
      { text: 'API', link: 'https://api.maimai.turou.fun/' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'MIT License',
      copyright: 'Copyright © 2019-2025 TrueRou'
    },

    sidebar: [
      {
        text: '介绍',
        items: [
          { text: '开始', link: '/get-started' },
          { text: '例子', link: '/examples' },
          { text: '客户端', link: '/client' }
        ]
      },
      {
        text: '概念',
        items: [
          { text: '核心概念', link: '/modules/concepts' },
          { text: '数据模型', link: '/modules/models' },
          { text: '缓存策略', link: '/modules/caches' }
        ]
      },
      {
        text: '功能',
        items: [
          { text: '曲目', link: '/modules/songs' },
          { text: '玩家', link: '/modules/players' },
          { text: '分数', link: '/modules/scores' },
          { text: '牌子', link: '/modules/plates' },
          { text: '区域', link: '/modules/areas' },
          { text: '收藏品', link: '/modules/items' },
          { text: '途径省份', link: '/modules/regions' },
        ]
      },
      {
        text: '数据源',
        items: [
          { text: 'DivingFish', link: '/providers/divingfish' },
          { text: 'LXNS', link: '/providers/lxns' },
          { text: 'Wechat', link: '/providers/wechat' },
          { text: 'Arcade', link: '/providers/arcade' }
        ]
      },
      {
        text: '开发',
        items: [
          { text: '参与开发', link: '/dev/participation' },
          { text: '示例项目', link: '/dev/samples' },
        ]
      }
    ],

    docFooter: {
      prev: '上一页',
      next: '下一页'
    },

    outline: {
      label: '本页内容',
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/TrueRou/maimai.py' }
    ]
  }
})
