import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current directory.
  // Set the third parameter to '' to load all env regardless of the `VITE_` prefix.
  const env = loadEnv(mode, process.cwd(), '');
  
  return {
    plugins: [react()],
    // Remove specific base path - let Vercel handle it
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    define: {
      // Environment variables for client-side use
    },
    build: {
      outDir: "dist",
      // Ensure the build generates static assets that work with HashRouter
      assetsDir: "assets",
      // Generate clean URLs
      sourcemap: false,
      // Fix chunk size warnings by splitting large dependencies
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-tabs'],
            // UI components
          }
        }
      },
      chunkSizeWarningLimit: 1000
    },
    server: {
      port: 5173,
      open: true,
    },
  };
});
