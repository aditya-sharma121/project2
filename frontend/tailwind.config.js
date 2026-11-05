/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080D18",
        surface: "#111B2B",
        surfaceHover: "#162236",
        borderDark: "#1E293B",
        primary: {
          DEFAULT: "#22D3EE",
          dark: "#0891B2",
          light: "#67E8F9"
        },
        success: "#22C55E",
        warning: "#F59E0B",
        critical: "#EF4444",
        foreground: "#F8FAFC",
        muted: "#94A3B8"
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      }
    },
  },
  plugins: [],
};
