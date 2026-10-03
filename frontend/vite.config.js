import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        // 可通过环境变量覆盖后端地址（如 VITE_API_TARGET=http://127.0.0.1:5098）
        target: process.env.VITE_API_TARGET || 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
