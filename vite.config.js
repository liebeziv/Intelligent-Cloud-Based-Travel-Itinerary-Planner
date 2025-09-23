import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  root: 'frontend',
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://travelplan.us-east-1.elasticbeanstalk.com',
        changeOrigin: true
      }
    }
  }
})

