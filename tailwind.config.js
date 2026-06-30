/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17211d",
        panel: "#f7f8f5",
        line: "#dce3dc",
        moss: "#536f56",
        clay: "#9a6048",
        bluegray: "#526b7a",
      },
      boxShadow: {
        soft: "0 1px 2px rgba(23, 33, 29, 0.08), 0 12px 30px rgba(23, 33, 29, 0.08)",
      },
    },
  },
  plugins: [],
};
