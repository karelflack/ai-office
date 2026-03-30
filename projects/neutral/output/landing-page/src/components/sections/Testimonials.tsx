'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { fadeInUp, staggerContainer } from '@/lib/motion'

// PLACEHOLDER testimonials — replace with real quotes before launch.
// Written in the right voice and length — do not stretch or make them more effusive.
const TESTIMONIALS = [
  {
    quote:
      "I've tried everything. Notion, Obsidian, Roam, Logseq. Neutral is the first one that actually gets out of the way.",
    name: 'Alex M.',
    title: 'Product Manager',
    company: 'Acme Corp', // placeholder
  },
  {
    quote:
      "The local transcription alone is worth it. Nobody knows Neutral is running, and my notes are better than anything I've written manually.",
    name: 'Sarah K.',
    title: 'Independent Researcher',
    company: 'Meridian', // placeholder
  },
  {
    quote: "I've stopped worrying about where to put things. Neutral just... finds them when I need them.",
    name: 'Daniel T.',
    title: 'Founder',
    company: 'Loom Labs', // placeholder
  },
]

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 px-6">
      <div
        className="max-w-6xl mx-auto rounded-card p-16 border"
        style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--bg-border)' }}
      >
        {/* Section header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <motion.div variants={fadeInUp} className="mb-4">
            <Badge>What people are saying</Badge>
          </motion.div>
          <motion.h2
            variants={fadeInUp}
            className="text-4xl font-bold tracking-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Used by people who take
            <br />
            their work seriously.
          </motion.h2>
        </motion.div>

        {/* Testimonial cards */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {TESTIMONIALS.map((t) => (
            <motion.div key={t.name} variants={fadeInUp}>
              <Card className="h-full flex flex-col gap-4">
                <blockquote
                  className="text-sm leading-relaxed flex-1"
                  style={{ color: 'var(--text-primary)' }}
                >
                  &ldquo;{t.quote}&rdquo;
                </blockquote>
                <div className="flex items-center gap-3 pt-2 border-t" style={{ borderColor: 'var(--bg-border)' }}>
                  {/* Avatar placeholder — initials in a circle */}
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0"
                    style={{ backgroundColor: 'var(--accent-subtle)', color: 'var(--accent)' }}
                  >
                    {t.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
                      {t.name}
                    </p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      {t.title} · {t.company}
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
