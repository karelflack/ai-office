'use client'

import { motion } from 'framer-motion'
import { Button } from '@/components/ui/Button'
import { fadeInUp, staggerContainer } from '@/lib/motion'

export function CTA() {
  return (
    <section className="py-24 px-6">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="max-w-2xl mx-auto text-center"
      >
        <motion.h2
          variants={fadeInUp}
          className="text-4xl font-bold mb-4 tracking-tight"
          style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
        >
          Start thinking more clearly.
          <br />
          Today.
        </motion.h2>

        <motion.p
          variants={fadeInUp}
          className="text-base leading-relaxed mb-8"
          style={{ color: 'var(--text-secondary)' }}
        >
          No credit card. No setup. No tutorial to watch.
          <br />
          Just open Neutral and start.
        </motion.p>

        <motion.div variants={fadeInUp} className="flex flex-col items-center gap-4">
          <Button href="#" variant="primary">
            Get Started — It&apos;s Free
          </Button>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
            Free plan available. No credit card required. Upgrade or cancel anytime.
          </p>
        </motion.div>
      </motion.div>
    </section>
  )
}
