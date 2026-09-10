import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import path from 'node:path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // 代理所有 API 请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      // 代理认证相关请求
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // 代理课程相关请求
      '/courses': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // 代理聊天相关请求
      '/chat': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
