import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  interactive?: boolean
}

/**
 * Base card component.
 * No drop shadows — uses border contrast instead (keeps visual language clean).
 * If interactive, border shifts on hover.
 */
export function Card({ children, className = '', interactive = false }: CardProps) {
  return (
    <div
      className={`rounded-card p-6 border transition-colors ${
        interactive ? 'cursor-default' : ''
      } ${className}`}
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderColor: 'var(--bg-border)',
      }}
      onMouseEnter={
        interactive
          ? (e) => ((e.currentTarget as HTMLElement).style.borderColor = 'var(--text-muted)')
          : undefined
      }
      onMouseLeave={
        interactive
          ? (e) => ((e.currentTarget as HTMLElement).style.borderColor = 'var(--bg-border)')
          : undefined
      }
    >
      {children}
    </div>
  )
}
