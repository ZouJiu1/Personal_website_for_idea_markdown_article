import './assets/main.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// import texme from 'texme'
// import mathjax from 'mathjax'
import katex from 'katex' // https://katex.org/docs
import renderMathInElement from 'katex/contrib/auto-render/auto-render.js'
import 'katex/dist/katex.min.css';

import { createApp } from 'vue'
import Cookies from 'js-cookie'

import App from './App.vue'
// import require from 'require'
// import axios from 'axios'
import router from './router/routers.js'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
var notrelease = false

export default notrelease

app.use(router)
app.use(notrelease)
// app.use(katex)
// app.use(Cookies)
// app.use(videojs) 
// app.prototype.$video = videojs;
app.use(ElementPlus)
// app.use(axios)
router.isReady().then(() => app.mount('#app'))
// app.mount('#app')