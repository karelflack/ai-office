'use client'

import { useState, useEffect } from 'react'
import { Menu, X } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

const NAV_LINKS = [
  { label: 'Features', href: '#features' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'Blog', href: '#' },
]

/**
 * Sticky navbar — transparent at top, gains a surface background on scroll.
 * Collapses to hamburger on mobile.
 * Wordmark is Inter 600, tight tracking.
 */
export function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 16)
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
        scrolled ? 'border-b' : ''
      }`}
      style={{
        backgroundColor: scrolled ? 'var(--bg-base)' : 'transparent',
        borderColor: 'var(--bg-border)',
      }}
    >
      <nav className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Wordmark — Inter 600, -0.03em tracking */}
        <a
          href="/"
          className="text-lg font-semibold flex items-center gap-2"
          style={{ color: 'var(--text-primary)', letterSpacing: '-0.03em' }}
        >
          {/* Accent square mark — geometric, simple */}
          <span
            className="w-5 h-5 rounded-[4px] flex-shrink-0"
            style={{ backgroundColor: 'var(--accent)' }}
          />
          AI Office
        </a>

        {/* Desktop nav links */}
        <ul className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <li key={link.label}>
              <a
                href={link.href}
                className="text-sm transition-colors"
                style={{ color: 'var(--text-secondary)' }}
                onMouseEnter={(e) =>
                  ((e.target as HTMLElement).style.color = 'var(--text-primary)')
                }
                onMouseLeave={(e) =>
                  ((e.target as HTMLElement).style.color = 'var(--text-secondary)')
                }
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Desktop CTAs */}
        <div className="hidden md:flex items-center gap-3">
          <ThemeToggle />
          <Button href="#" variant="primary">
            Get Started →
          </Button>
        </div>

        {/* Mobile: theme toggle + hamburger */}
        <div className="flex md:hidden items-center gap-2">
          <ThemeToggle />
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Toggle menu"
            className="w-8 h-8 flex items-center justify-center"
            style={{ color: 'var(--text-secondary)' }}
          >
            {menuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </nav>

      {/* Mobile menu drawer */}
      {menuOpen && (
        <div
          className="md:hidden border-t px-6 py-4 flex flex-col gap-4"
          style={{ backgroundColor: 'var(--bg-base)', borderColor: 'var(--bg-border)' }}
        >
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-sm py-2"
              style={{ color: 'var(--text-secondary)' }}
              onClick={() => setMenuOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <Button href="#" variant="primary" fullWidth>
            Get Started →
          </Button>
        </div>
      )}
    </header>
  )
}
