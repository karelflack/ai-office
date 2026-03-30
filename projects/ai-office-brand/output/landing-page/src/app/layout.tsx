import type { Metadata } from 'next'
import { ThemeProvider } from 'next-themes'
// Self-hosted fonts via fontsource — no Google Fonts CDN (privacy + performance)
import '@fontsource-variable/inter'
import '@fontsource/jetbrains-mono/400.css'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Office — Delegate everything. Ship faster.',
  description:
    'AI Office gives every professional a team of specialized AI assistants. Research, drafting, scheduling, analysis — done in minutes, not hours.',
  openGraph: {
    title: 'AI Office — Delegate everything. Ship faster.',
    description:
      'The AI-powered team for every professional. Multiple specialized agents working in parallel so you can focus on the work only you can do.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    /*
      suppressHydrationWarning is required to prevent React hydration mismatch
      when next-themes sets data-theme before the React tree hydrates.
    */
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="data-theme"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
