/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        display: ['"Syne"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        primary: {
          50:  '#eef3ff',
          100: '#dce8ff',
          200: '#c0d3ff',
          300: '#97b5ff',
          400: '#6c9eff',
          500: '#4a7ff5',
          600: '#2d5eea',
          700: '#2449d7',
          800: '#223cae',
          900: '#213689',
        },
        accent: {
          purple: '#BDB2FF',
          teal:   '#A8DADC',
          pink:   '#FFB3C6',
          amber:  '#FFD166',
        },
        surface: {
          light: '#F8FAFC',
          card:  'rgba(255,255,255,0.7)',
          dark:  '#0F172A',
          'dark-card': 'rgba(15,23,42,0.8)',
        },
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        glass: '0 8px 32px 0 rgba(31,38,135,0.15)',
        'glass-dark': '0 8px 32px 0 rgba(0,0,0,0.4)',
        neon: '0 0 20px rgba(108,158,255,0.4)',
        'neon-purple': '0 0 20px rgba(189,178,255,0.4)',
      },
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-up': 'fadeUp 0.4s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        fadeUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 10px rgba(108,158,255,0.3)' },
          '100%': { boxShadow: '0 0 25px rgba(108,158,255,0.7)' },
        },
      },
    },
  },
  plugins: [],
}
