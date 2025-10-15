import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/risk': 'http://localhost:8000',
      '/explain': 'http://localhost:8000',
      '/frames': 'http://localhost:8000',
      '/spread': 'http://localhost:8000',
    }
  }
})
