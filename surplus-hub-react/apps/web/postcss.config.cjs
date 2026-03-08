module.exports = {
  plugins: {
    "nativewind/postcss": {
      output: "nativewind-output.css",
      isProd: process.env.NODE_ENV === "production",
    },
    tailwindcss: {},
    autoprefixer: {},
    "postcss-css-variables": {},
  },
};
