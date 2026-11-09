/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // STYLE 4 – PREMIUM ENTERPRISE EXACT SYSTEM PALETTE
        surface: {
          white: '#FFFFFF',
          grey: '#F5F7FA',
          subtle: '#EFF5FF',
          border: '#DCE3EC',
        },
        brand: {
          blue: '#1769D2',
          'blue-hover': '#1258B3',
          'blue-light': '#EFF5FF',
          navy: '#172B4D',
          grey: '#64748B',
          border: '#DCE3EC',
        },
        status: {
          success: '#16A36A',
          'success-bg': '#ECFDF3',
          'success-border': '#A6F4C5',
          warning: '#E5A000',
          'warning-bg': '#FEFBE8',
          'warning-border': '#FDE047',
          error: '#DC4545',
          'error-bg': '#FEF2F2',
          'error-border': '#FCA5A5',
        },
      },
    },
  },
  plugins: [],
}
