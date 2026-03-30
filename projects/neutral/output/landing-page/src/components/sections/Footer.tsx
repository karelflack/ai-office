import { Twitter, Linkedin, Github } from 'lucide-react'

const FOOTER_LINKS = {
  Product: ['Features', 'Pricing', 'Changelog', 'Roadmap'],
  Company: ['About', 'Blog', 'Careers', 'Contact'],
  Legal: ['Privacy Policy', 'Terms of Service', 'Security', 'Cookie Policy'],
}

export function Footer() {
  return (
    <footer
      className="border-t px-6 pt-16 pb-10"
      style={{ borderColor: 'var(--bg-border)' }}
    >
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-10 mb-16">
          {/* Brand column */}
          <div className="col-span-2">
            {/* Wordmark — Inter 600, -0.03em tracking */}
            <span
              className="text-lg font-semibold block mb-3"
              style={{ color: 'var(--text-primary)', letterSpacing: '-0.03em' }}
            >
              Neutral
            </span>
            <p className="text-sm leading-relaxed max-w-xs" style={{ color: 'var(--text-secondary)' }}>
              Think clearly. Work calmly.
            </p>

            {/* Social icons */}
            <div className="flex items-center gap-4 mt-6">
              <a
                href="#"
                aria-label="X (Twitter)"
                className="transition-colors"
                style={{ color: 'var(--text-muted)' }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-primary)')
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-muted)')
                }
              >
                <Twitter size={16} />
              </a>
              <a
                href="#"
                aria-label="LinkedIn"
                className="transition-colors"
                style={{ color: 'var(--text-muted)' }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-primary)')
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-muted)')
                }
              >
                <Linkedin size={16} />
              </a>
              <a
                href="#"
                aria-label="GitHub"
                className="transition-colors"
                style={{ color: 'var(--text-muted)' }}
                onMouseEnter={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-primary)')
                }
                onMouseLeave={(e) =>
                  ((e.currentTarget as HTMLElement).style.color = 'var(--text-muted)')
                }
              >
                <Github size={16} />
              </a>
            </div>
          </div>

          {/* Navigation columns */}
          {Object.entries(FOOTER_LINKS).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--text-muted)' }}>
                {category}
              </h4>
              <ul className="flex flex-col gap-2.5">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm transition-colors"
                      style={{ color: 'var(--text-secondary)' }}
                      onMouseEnter={(e) =>
                        ((e.currentTarget as HTMLElement).style.color = 'var(--text-primary)')
                      }
                      onMouseLeave={(e) =>
                        ((e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)')
                      }
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Legal line */}
        <div
          className="pt-8 border-t flex flex-col sm:flex-row items-center justify-between gap-4"
          style={{ borderColor: 'var(--bg-border)' }}
        >
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            © 2026 Neutral. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}
