import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  interactive?: boolean
}

/**
 * Base card component.
 * No drop shadows — uses border contrast instead.
 * If interactive, border shifts from bg-border to text-muted on hover.
 */
export function Card({ children, className = '', interactive = false }: CardProps) {
  return (
    <div
      className={`rounded-card p-6 border transition-colors ${
        interactive ? 'hover:border-text-muted' : ''
      } ${className}`}
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderColor: 'var(--bg-border)',
      }}
    >
      {children}
    </div>
  )
}
