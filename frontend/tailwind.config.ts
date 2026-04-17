import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#ffffff",
          dark: "#0a0a0a",
        },
        panel: {
          DEFAULT: "#f8f9fa",
          dark: "#111111",
        },
        border: {
          DEFAULT: "#e5e7eb",
          dark: "#2a2a2a",
        },
        fg: {
          DEFAULT: "#0a0a0a",
          dark: "#ededed",
        },
        muted: {
          DEFAULT: "#6b7280",
          dark: "#888888",
        },
        accent: {
          DEFAULT: "#00A867",
          dark: "#00DC82",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
