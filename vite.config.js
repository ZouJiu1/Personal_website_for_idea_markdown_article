import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// 后端 Django 地址（本地调试）
const djangoTarget = process.env.DJANGO_TARGET || 'http://localhost:7290'

// 接口与静态资源前缀，开发环境经 vite 代理转发到 Django，前端代码一律使用相对路径
const proxyPrefixes = [
  'csdn', 'zhihu', 'think', 'video', 'travel',
  'commonuse', 'markdown_detail', 'upload_video', 'everydayimg',
  'article', 'people', 'hls',
]

const proxy = {}
for (const prefix of proxyPrefixes) {
  proxy[`/${prefix}`] = {
    target: djangoTarget,
    changeOrigin: true,
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0',
    proxy,
    watch: {
      // people/ article/ dist/ 是运行期数据目录（用户内容、账号库、构建产物），
      // 随用户数增长会耗尽 inotify watch 配额导致 dev server 崩溃(ENOSPC)，且热更新无需监视它们
      ignored: ['**/people/**', '**/article/**', '**/dist/**', '**/node_modules/**'],
    },
  },
  build: {
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        // 拆分大型第三方库，利于浏览器缓存与高并发下的加载
        manualChunks: {
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          'katex': ['katex'],
          'vendor': ['vue', 'vue-router', 'axios', 'js-cookie'],
        },
      },
    },
  },
})
