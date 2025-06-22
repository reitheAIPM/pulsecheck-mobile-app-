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
      'process.env.BUILDER_API_KEY': JSON.stringify('93b18bce96bf4218884de91289488848'),
    },
    build: {
      outDir: "dist",
      // Ensure the build generates static assets that work with HashRouter
      assetsDir: "assets",
      // Generate clean URLs
      sourcemap: false,
    },
    server: {
      port: 5173,
      open: true,
    },
  };
});
