import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "maimai.py",
  description: "maimai.py docs",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/get-started' },
      { text: 'API', link: 'https://maimai-py.pages.dev/' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'Get Started', link: '/get-started' },
          { text: 'Try Examples', link: '/examples' }
        ]
      },
      {
        text: 'Modules',
        items: [
          { text: 'Core Concepts', link: '/modules/concepts' },
          { text: 'Songs', link: '/modules/songs' },
          { text: 'Players', link: '/modules/players' },
          { text: 'Scores', link: '/modules/scores' },
          { text: 'Plates', link: '/modules/plates' },
          { text: 'Models', link: '/modules/models' },
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
    }
  }
})
