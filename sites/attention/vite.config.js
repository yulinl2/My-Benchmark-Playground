import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base: './' makes built asset paths relative, so the static bundle works when
// served from a subpath (e.g. GitHub Pages project site) or opened locally.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: { outDir: 'dist', sourcemap: false },
})
