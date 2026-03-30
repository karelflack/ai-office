import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  // Class-based dark mode — driven by data-theme="dark" on <html> via next-themes
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Dark mode base palette
        'bg-base': '#0A0A0B',
        'bg-surface': '#111113',
        'bg-border': '#1E1E22',
        'text-primary': '#F2F2F3',
        'text-secondary': '#8A8A96',
        'text-muted': '#4A4A56',
        // Brand accent — single variable for easy swapping
        accent: '#7C6FFF',
        'accent-hover': '#9589FF',
        'accent-subtle': 'rgba(124, 111, 255, 0.1)',
        // Semantic colors
        success: '#22C55E',
        warning: '#F59E0B',
        destructive: '#EF4444',
        // Light mode overrides (used with dark: prefix)
        'light-bg-base': '#FAFAFA',
        'light-bg-surface': '#FFFFFF',
        'light-bg-border': '#E4E4E7',
        'light-text-primary': '#0A0A0B',
        'light-text-secondary': '#52525B',
        'light-text-muted': '#A1A1AA',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace'],
      },
      borderRadius: {
        card: '12px',
        button: '8px',
        badge: '6px',
      },
      letterSpacing: {
        tight: '-0.02em',
        tighter: '-0.03em',
      },
    },
  },
  plugins: [],
}

export default config
