import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: [
    './app/**/*.{vue,js,ts}',
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.{vue,js,ts}',
    './pages/**/*.{vue,js,ts}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        // Warm coral/terracotta brand palette (matching remotifex.com)
        brand: {
          50:  '#fef4f0',
          100: '#fee4db',
          200: '#fcc8b6',
          300: '#faa385',
          400: '#f67a55',
          500: '#ec5a2d',
          600: '#d44520',
          700: '#af381c',
          800: '#8c301c',
          900: '#73291b',
          950: '#3e120b',
        },
        // Semantic theme tokens (CSS custom properties)
        page:         'rgb(var(--c-page) / <alpha-value>)',
        surface: {
          DEFAULT:    'rgb(var(--c-surface) / <alpha-value>)',
          hover:      'rgb(var(--c-surface-hover) / <alpha-value>)',
          active:     'rgb(var(--c-surface-active) / <alpha-value>)',
        },
        inset:        'rgb(var(--c-inset) / <alpha-value>)',
        heading:      'rgb(var(--c-text) / <alpha-value>)',
        sub:          'rgb(var(--c-text-sub) / <alpha-value>)',
        muted:        'rgb(var(--c-text-muted) / <alpha-value>)',
        faint:        'rgb(var(--c-text-faint) / <alpha-value>)',
        edge: {
          DEFAULT:    'rgb(var(--c-border) / <alpha-value>)',
          subtle:     'rgb(var(--c-border-subtle) / <alpha-value>)',
        },
        'brand-soft': 'rgb(var(--c-brand-soft) / <alpha-value>)',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-soft': 'pulseSoft 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(10px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
} satisfies Config
