import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "maimai.py",
  description: "The definitive python wrapper for MaimaiCN related development, wrapping the common functions and models.",
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/get-started' },
      { text: 'API', link: 'https://api.maimai.turou.fun/' }
    ],

    search: {
      provider: 'local'
    },

    footer: {
      message: 'MIT License',
      copyright: 'Copyright © 2019-2024 TrueRou'
    },

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'Get Started', link: '/get-started' },
          { text: 'Try Examples', link: '/examples' }
        ]
      },
      {
        text: 'Concepts',
        items: [
          { text: 'Core Concepts', link: '/modules/concepts' },
          { text: 'All Models', link: '/modules/models' },
          { text: 'Cache Strategy', link: '/modules/caches' }
        ]
      },
      {
        text: 'Modules',
        items: [
          { text: 'Songs', link: '/modules/songs' },
          { text: 'Players', link: '/modules/players' },
          { text: 'Scores', link: '/modules/scores' },
          { text: 'Plates', link: '/modules/plates' },
          { text: 'Models', link: '/modules/models' },
          { text: 'Items', link: '/modules/items' },
          { text: 'Passby Regions', link: '/modules/regions' },
        ]
      },
      {
        text: 'Providers',
        items: [
          { text: 'DivingFish', link: '/providers/divingfish' },
          { text: 'LXNS', link: '/providers/lxns' },
          { text: 'Wechat', link: '/providers/wechat' },
          { text: 'Arcade', link: '/providers/arcade' }
        ]
      },
      {
        text: 'Development',
        items: [
          { text: 'Participation', link: '/dev/participation' },
          { text: 'Samples', link: '/dev/samples' },
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/TrueRou/maimai.py' }
    ]
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en'
    },
    zh: {
      label: '简体中文',
      lang: 'zh',
      description: "用于国服舞萌相关开发的最佳Python工具库, 封装水鱼/落雪查分器常用函数. ",
      themeConfig: {
        nav: [
          { text: '主页', link: '/zh' },
          { text: '指南', link: '/zh/get-started' },
          { text: 'API', link: 'https://api.maimai.turou.fun/' }
        ],

        sidebar: [
          {
            text: '介绍',
            items: [
              { text: '开始', link: '/zh/get-started' },
              { text: '例子', link: '/zh/examples' }
            ]
          },
          {
            text: '概念',
            items: [
              { text: '核心概念', link: '/zh/modules/concepts' },
              { text: '数据模型', link: '/zh/modules/models' },
              { text: '缓存策略', link: '/zh/modules/caches' }
            ]
          },
          {
            text: '功能',
            items: [
              { text: '曲目', link: '/zh/modules/songs' },
              { text: '玩家', link: '/zh/modules/players' },
              { text: '分数', link: '/zh/modules/scores' },
              { text: '牌子', link: '/zh/modules/plates' },
              { text: '收藏品', link: '/zh/modules/items' },
              { text: '途径省份', link: '/zh/modules/regions' },
            ]
          },
          {
            text: '数据源',
            items: [
              { text: 'DivingFish', link: '/zh/providers/divingfish' },
              { text: 'LXNS', link: '/zh/providers/lxns' },
              { text: 'Wechat', link: '/zh/providers/wechat' },
              { text: 'Arcade', link: '/zh/providers/arcade' }
            ]
          },
          {
            text: '开发',
            items: [
              { text: '参与开发', link: '/zh/dev/participation' },
              { text: '示例项目', link: '/zh/dev/samples' },
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
      },
    }
  }
})
