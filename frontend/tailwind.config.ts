import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        slatebase: "#f7f4ef",
        ink: "#1c1f2a",
        accent: "#0b7a75",
        warm: "#d96f32"
      }
    }
  },
  plugins: []
};

export default config;
