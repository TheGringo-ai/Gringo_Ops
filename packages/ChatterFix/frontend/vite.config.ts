import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: '.',           // ensures root is current folder
  publicDir: 'public', // ensures public assets are used
  build: {
    outDir: 'dist',    // Firebase expects production output here
    emptyOutDir: true  // cleans the output folder before building
  }
})
