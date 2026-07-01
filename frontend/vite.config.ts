import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In docker-compose the API is reachable at http://backend:8000 (set via
// VITE_PROXY_TARGET). For local `npm run dev` outside docker it defaults to
// localhost. Either way the browser only ever talks to /api.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
