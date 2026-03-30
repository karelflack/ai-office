import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  className?: string
}

/**
 * Eyebrow badge — used above section headlines to provide context.
 * Background: accent-subtle, text: accent, 12px / 500 weight.
 */
export function Badge({ children, className = '' }: BadgeProps) {
  return (
    <span
      className={`inline-block text-xs font-medium px-[10px] py-1 rounded-badge tracking-wide ${className}`}
      style={{ backgroundColor: 'var(--accent-subtle)', color: 'var(--accent)' }}
    >
      {children}
    </span>
  )
}
