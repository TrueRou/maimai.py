import { type Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import './styles/vars.css'
import './styles/layout.css'

const theme: Theme = {
    ...DefaultTheme,
}

export default theme