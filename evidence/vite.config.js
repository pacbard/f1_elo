import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: 'esnext', // Target modern JavaScript only
    sourcemap: false, // Disable sourcemaps in production
    minify: 'esbuild', // Enable esbuild for minification
    terserOptions: {
      compress: {
        drop_console: true, // Remove console logs for production
      },
    },
    cacheDir: '.vite', // Make sure the cache is stored in a persistent location
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return 'vendor';
          }
        },
      },
    },
  },
});
