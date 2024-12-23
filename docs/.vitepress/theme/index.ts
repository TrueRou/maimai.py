import { type Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import Layout from './layout.vue'
import './styles/vars.css'
import './styles/layout.css'

const theme: Theme = {
    extends: DefaultTheme,
    Layout: Layout,
}

export default theme