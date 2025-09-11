import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3005,
    host: "0.0.0.0",
    allowedHosts: ["litex.zecyel.xyz"]
  }
}) 
