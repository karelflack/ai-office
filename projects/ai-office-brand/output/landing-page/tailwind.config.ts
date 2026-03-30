import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  // Class-based dark mode — driven by data-theme="dark" on <html> via next-themes
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        // Dark mode base palette
        'bg-base': '#09090F',
        'bg-surface': '#101018',
        'bg-border': '#1C1C2E',
        'text-primary': '#F0F0F8',
        'text-secondary': '#8888A4',
        'text-muted': '#44445A',
        // Brand accent — electric blue, distinct from Neutral's violet
        accent: '#2563EB',
        'accent-hover': '#3B82F6',
        'accent-subtle': 'rgba(37, 99, 235, 0.1)',
        // Semantic colors
        success: '#22C55E',
        warning: '#F59E0B',
        destructive: '#EF4444',
        // Light mode overrides
        'light-bg-base': '#F8F8FC',
        'light-bg-surface': '#FFFFFF',
        'light-bg-border': '#E2E2F0',
        'light-text-primary': '#09090F',
        'light-text-secondary': '#525270',
        'light-text-muted': '#9898B4',
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
