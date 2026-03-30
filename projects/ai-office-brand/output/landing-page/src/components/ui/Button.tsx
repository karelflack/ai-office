import React from 'react'
import { motion } from 'framer-motion'

interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary'
  href?: string
  onClick?: () => void
  className?: string
  fullWidth?: boolean
}

/**
 * Primary: accent background, white text — main CTA.
 * Secondary (ghost): transparent bg, border, muted text — supporting action.
 * No pill rounding — professional tool, not a consumer app.
 */
export function Button({
  children,
  variant = 'primary',
  href,
  onClick,
  className = '',
  fullWidth = false,
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center text-sm font-medium rounded-button px-6 py-3 transition-colors cursor-pointer select-none'
  const widthClass = fullWidth ? 'w-full' : ''

  const styles =
    variant === 'primary'
      ? 'text-white'
      : 'bg-transparent border'

  const inlineStyle =
    variant === 'primary'
      ? { backgroundColor: 'var(--accent)' }
      : {
          borderColor: 'var(--bg-border)',
          color: 'var(--text-secondary)',
        }

  const content = (
    <motion.span
      className={`${base} ${styles} ${widthClass} ${className}`}
      style={inlineStyle}
      whileHover={
        variant === 'primary'
          ? { scale: 1.01, backgroundColor: 'var(--accent-hover)' }
          : { borderColor: 'var(--text-muted)', color: 'var(--text-primary)' }
      }
      transition={{ duration: 0.15 }}
      onClick={onClick}
    >
      {children}
    </motion.span>
  )

  if (href) {
    return (
      <a href={href} className={fullWidth ? 'w-full block' : ''}>
        {content}
      </a>
    )
  }

  return content
}
