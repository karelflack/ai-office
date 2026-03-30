'use client'

import { useTheme } from 'next-themes'
import { Moon, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'

/**
 * Theme toggle button — switches between dark and light mode.
 * Uses a mounted guard to avoid hydration mismatch (theme is unknown on server).
 */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  // Only render after mount to prevent SSR hydration mismatch
  useEffect(() => setMounted(true), [])

  if (!mounted) {
    return <div className="w-8 h-8" />
  }

  const isDark = theme === 'dark'

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
      className="w-8 h-8 flex items-center justify-center rounded-button transition-colors"
      style={{ color: 'var(--text-secondary)' }}
    >
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  )
}
