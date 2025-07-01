import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "maimai.py",
  description: "用于舞萌DX相关开发的最佳Python工具库, 封装水鱼/落雪查分器常用函数.",
  themeConfig: {
    nav: [
      { text: '主页', link: '/' },
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
        text: '开始',
        link: '/get-started'
      },
      {
        text: '功能',
        items: [
          { text: '曲目', link: '/modules/songs' },
          { text: '成绩', link: '/modules/scores' },
          { text: '玩家', link: '/modules/players' },
          { text: '牌子', link: '/modules/plates' },
          { text: '区域', link: '/modules/areas' },
          { text: '收藏品', link: '/modules/items' },
          { text: '游玩地区', link: '/modules/regions' },
        ]
      },
      {
        text: '概念',
        items: [
          { text: '数据模型', link: '/concepts/models' },
          { text: '缓存策略', link: '/concepts/caches' },
          { text: '单元用例', link: '/concepts/examples' },
          { text: 'RESTful 客户端', link: '/concepts/client' }
        ]
      },
      {
        text: '数据源',
        items: [
          { text: 'DivingFish', link: '/providers/divingfish' },
          { text: 'LXNS', link: '/providers/lxns' },
          { text: 'Arcade', link: '/providers/arcade' },
          { text: 'Wechat', link: '/providers/wechat' },
          { text: 'Local', link: '/providers/local' },
        ]
      },
      {
        text: '示例项目',
        items: [
          { text: 'proxy_updater', link: '/samples/proxy_updater' },
          { text: 'simple_prober', link: '/samples/simple_prober' },
        ]
      },
      {
        text: '更新日志',
        link: '/changelog'
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
