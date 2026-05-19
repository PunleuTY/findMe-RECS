import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  "#eef7ff",
          100: "#d9ecff",
          500: "#2f80ed",
          600: "#1f6fe0",
          700: "#1b5fc0",
        },
      },
    },
  },
  plugins: [],
};

export default config;
