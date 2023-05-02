/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        body: ["'Sawarabi Gothic'", "sans-serif"],
        display: ["'Varela Round'", "sans-serif"],
      },
    },
  },
  plugins: [require("daisyui")],
}
