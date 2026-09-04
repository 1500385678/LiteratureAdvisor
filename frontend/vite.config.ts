import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// LiteratureAdvisor · Phase 1 第 5 步
// FastAPI 8000 后端 · Vite 5173 前端 · /api 代理打通
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
