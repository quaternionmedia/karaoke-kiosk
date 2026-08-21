import { defineConfig } from "vite";

// Two entries: the kiosk and the admin dashboard.
export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: new URL("./index.html", import.meta.url).pathname,
        admin: new URL("./admin.html", import.meta.url).pathname,
      },
    },
  },
});
