/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#ed701d',
          light: '#fdf0e7',
          dark: '#e65c00',
          foreground: '#ffffff',
        },
        background: {
          DEFAULT: '#f9f7f6',
          light: '#f9f7f6',
          secondary: '#eeeff2',
          tertiary: '#f1f0ee',
        },
        foreground: {
          DEFAULT: '#151c28',
        },
        card: {
          DEFAULT: '#ffffff',
          foreground: '#151c28',
        },
        muted: {
          DEFAULT: '#f1f0ee',
          foreground: '#6a7181',
        },
        accent: {
          DEFAULT: '#fdf0e7',
          foreground: '#a54a0d',
        },
        secondary: {
          DEFAULT: '#eeeff2',
          foreground: '#151c28',
        },
        border: {
          DEFAULT: '#e2e4e9',
          primary: '#e2e4e9',
          secondary: '#e2e4e9',
        },
        input: '#e2e4e9',
        ring: '#ed701d',
        destructive: {
          DEFAULT: '#dc2828',
          foreground: '#ffffff',
        },
        success: {
          DEFAULT: '#21c45d',
          foreground: '#ffffff',
        },
        warning: {
          DEFAULT: '#f59f0a',
          foreground: '#ffffff',
        },
        info: {
          DEFAULT: '#1485f5',
          foreground: '#ffffff',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
