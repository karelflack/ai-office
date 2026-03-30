'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { fadeInUp, floatingImage, staggerContainer } from '@/lib/motion'

// Placeholder company names for the logo strip
const LOGO_PLACEHOLDERS = ['Acme Corp', 'Meridian', 'Loom Labs', 'Patchwork', 'Fieldstone']

export function Hero() {
  return (
    <section className="relative pt-32 pb-24 px-6 overflow-hidden">
      <div className="max-w-4xl mx-auto text-center">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="flex flex-col items-center gap-6"
        >
          {/* Eyebrow badge */}
          <motion.div variants={fadeInUp}>
            <Badge>Now in Beta</Badge>
          </motion.div>

          {/* Hero headline — line breaks are intentional per Jorunn's copy */}
          <motion.h1
            variants={fadeInUp}
            className="font-bold leading-[1.1] tracking-tight"
            style={{
              color: 'var(--text-primary)',
              fontSize: 'clamp(42px, 6vw, 72px)',
              letterSpacing: '-0.02em',
            }}
          >
            Think clearly.
            <br />
            Work calmly.
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={fadeInUp}
            className="text-lg leading-relaxed max-w-xl"
            style={{ color: 'var(--text-secondary)' }}
          >
            Neutral is the AI workspace for professionals who think for a living.
            Capture ideas, connect them, and ship work — without the noise.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            variants={fadeInUp}
            className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto"
          >
            <Button href="#" variant="primary">
              Get Started — It&apos;s Free
            </Button>
            <Button href="#features" variant="secondary">
              See how it works →
            </Button>
          </motion.div>

          {/* Social proof line */}
          <motion.p
            variants={fadeInUp}
            className="text-sm"
            style={{ color: 'var(--text-muted)' }}
          >
            Used by 4,000+ researchers, writers, and operators who can&apos;t afford distraction.
          </motion.p>

          {/* Logo strip — muted, low-contrast per Jorunn's note */}
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

        {/* Product screenshot placeholder — floating animation per Ingrid's spec */}
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
              className="w-full aspect-video flex items-center justify-center"
              style={{ backgroundColor: 'var(--bg-surface)' }}
            >
              {/* Browser chrome */}
              <div className="w-full h-full flex flex-col">
                <div
                  className="flex items-center gap-2 px-4 py-3 border-b"
                  style={{ borderColor: 'var(--bg-border)' }}
                >
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: 'var(--bg-border)' }}
                  />
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: 'var(--bg-border)' }}
                  />
                  <span
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: 'var(--bg-border)' }}
                  />
                  <div
                    className="ml-4 flex-1 h-5 rounded max-w-xs"
                    style={{ backgroundColor: 'var(--bg-border)' }}
                  />
                </div>
                <div className="flex-1 flex items-center justify-center">
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
