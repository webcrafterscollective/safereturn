/* Vite configuration for Preact SPA served from FastAPI root path. */
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";

export default defineConfig({
  base: "/",
  plugins: [preact()],
  resolve: {
    alias: {
      react: "preact/compat",
      "react-dom": "preact/compat",
      "react/jsx-runtime": "preact/jsx-runtime",
      "react/jsx-dev-runtime": "preact/jsx-dev-runtime",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: true,
  },
});

