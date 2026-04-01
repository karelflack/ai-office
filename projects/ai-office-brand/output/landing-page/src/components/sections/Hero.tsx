'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { fadeInUp, floatingImage, staggerContainer } from '@/lib/motion'

// Placeholder company names for the logo strip — replace with real logos before launch
const LOGO_PLACEHOLDERS = ['Meridian', 'Fieldstone', 'Patchwork', 'Loom Labs', 'Castlemark']

export function Hero() {
  return (
    <section className="relative pt-32 pb-24 px-6 overflow-hidden">
      {/* Subtle radial gradient behind hero — blue glow in background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(37, 99, 235, 0.12) 0%, transparent 70%)',
        }}
      />

      <div className="max-w-4xl mx-auto text-center relative">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center gap-6"
        >
          {/* Eyebrow badge */}
          <motion.div variants={fadeInUp}>
            <Badge>Now Available</Badge>
          </motion.div>

          {/* Hero headline — line breaks are intentional */}
          <motion.h1
            variants={fadeInUp}
            className="font-bold leading-[1.1] tracking-tight"
            style={{
              color: 'var(--text-primary)',
              fontSize: 'clamp(42px, 6vw, 72px)',
              letterSpacing: '-0.02em',
            }}
          >
            Delegate everything.
            <br />
            Ship faster.
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={fadeInUp}
            className="text-lg leading-relaxed max-w-xl"
            style={{ color: 'var(--text-secondary)' }}
          >
            AI Office gives every professional a team of specialized AI assistants.
            Research, drafting, scheduling, analysis — done in minutes, not hours.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto"
          >
            <Button href="#" variant="primary">
              Start for Free
            </Button>
            <Button href="#features" variant="secondary">
              See it in action →
            </Button>
          </motion.div>

          {/* Social proof line */}
          <motion.p
            variants={fadeInUp}
            className="text-sm"
            style={{ color: 'var(--text-muted)' }}
          >
            Used by 6,000+ consultants, operators, and founders who ship without growing headcount.
          </motion.p>

          {/* Logo strip — muted, low-contrast */}
          <motion.div
            variants={fadeInUp}
            className="flex items-center gap-8 flex-wrap justify-center"
          >
            {LOGO_PLACEHOLDERS.map((name) => (
              <span
                key={name}
                className="text-xs font-medium tracking-wide uppercase"
                style={{ color: 'var(--text-muted)' }}
              >
                {name}
              </span>
            ))}
          </motion.div>
        </motion.div>

        {/* Product screenshot placeholder — floating animation */}
        <motion.div
          className="mt-16 mx-auto max-w-3xl"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4, ease: 'easeOut' }}
        >
          <motion.div
            animate={floatingImage.animate}
            transition={floatingImage.transition}
            className="rounded-card border overflow-hidden"
            style={{
              borderColor: 'var(--bg-border)',
              backgroundColor: 'var(--bg-surface)',
            }}
          >
            {/*
              Placeholder for product screenshot.
              Replace with <Image> using .webp source once product screenshots are available.
              Dimensions: 16:10 aspect ratio, 1200×750px recommended.
            */}
            <div
              className="w-full aspect-video flex flex-col"
              style={{ backgroundColor: 'var(--bg-surface)' }}
            >
              {/* Browser chrome */}
              <div
                className="flex items-center gap-2 px-4 py-3 border-b"
                style={{ borderColor: 'var(--bg-border)' }}
              >
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--bg-border)' }} />
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--bg-border)' }} />
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--bg-border)' }} />
                <div
                  className="ml-4 flex-1 h-5 rounded max-w-xs"
                  style={{ backgroundColor: 'var(--bg-border)' }}
                />
              </div>
              {/* Mock agent panel */}
              <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <div
                  className="w-48 border-r p-4 flex flex-col gap-3 hidden sm:flex"
                  style={{ borderColor: 'var(--bg-border)' }}
                >
                  {['Research Agent', 'Writer Agent', 'Scheduler', 'Analyst'].map((agent, i) => (
                    <div
                      key={agent}
                      className="flex items-center gap-2"
                    >
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: i === 0 ? 'var(--accent)' : 'var(--text-muted)' }}
                      />
                      <span
                        className="text-xs"
                        style={{ color: i === 0 ? 'var(--text-primary)' : 'var(--text-muted)' }}
                      >
                        {agent}
                      </span>
                    </div>
                  ))}
                </div>
                {/* Main area */}
                <div className="flex-1 flex items-center justify-center p-4">
                  <p
                    className="text-sm font-medium font-mono"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    [ Product screenshot — replace before launch ]
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  )
}
