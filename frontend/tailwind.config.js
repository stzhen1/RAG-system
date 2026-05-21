/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#1a1a1a',
        surface: '#242424',
        border: '#333333',
        accent: '#f0a500',
        'accent-dim': '#8b6f1a',
        text: '#e8e4dd',
        muted: '#8a8578',
      },
      fontFamily: {
        mono: ['"DM Mono"', 'monospace'],
        serif: ['"Crimson Text"', 'Georgia', 'serif'],
      },
      animation: {
        'pulse-cursor': 'pulse 1s ease-in-out infinite',
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
