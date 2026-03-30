import type { Metadata } from 'next'
import { ThemeProvider } from 'next-themes'
// Self-hosted fonts via fontsource — no Google Fonts CDN (privacy + performance)
import '@fontsource-variable/inter'
import '@fontsource/jetbrains-mono/400.css'
import './globals.css'

export const metadata: Metadata = {
  title: 'Neutral — Think clearly. Work calmly.',
  description:
    'Neutral is the AI workspace for professionals who think for a living. Capture ideas, connect them, and ship work — without the noise.',
  openGraph: {
    title: 'Neutral — Think clearly. Work calmly.',
    description:
      'The AI workspace that gets out of your way. Notes, meetings, and thinking — in one calm interface.',
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
