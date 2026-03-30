'use client'

import { motion } from 'framer-motion'
import { BrainCircuit, Link2, Mic, Lock, Zap, Layers } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { fadeInUp, staggerContainer } from '@/lib/motion'
import type { LucideIcon } from 'lucide-react'

interface FeatureCardData {
  icon: LucideIcon
  title: string
  body: string
}

// Feature grid data — copy verbatim from Jorunn's brand-copy.md
const FEATURES: FeatureCardData[] = [
  {
    icon: BrainCircuit,
    title: 'Smart Capture',
    body: 'Type a thought, paste a link, or speak it aloud. Neutral captures everything and finds the connection later — so you don\'t have to.',
  },
  {
    icon: Link2,
    title: 'Connected Notes',
    body: 'Every note you write is linked to the ones that came before it. No folders, no tags, no manual organization. Structure emerges on its own.',
  },
  {
    icon: Mic,
    title: 'Meeting Notes Without a Bot',
    body: 'Neutral transcribes locally — no robot joins your call. Your raw jottings become clean, searchable notes before you\'re back at your desk.',
  },
  {
    icon: Lock,
    title: 'Private by Design',
    body: 'Your notes never train our models. End-to-end encryption by default. We do not see your data, and we do not want to.',
  },
  {
    icon: Zap,
    title: 'AI That Thinks Alongside You',
    body: 'Ask Neutral to summarize, draft, or find a connection in your notes. It suggests — you decide. You stay in control.',
  },
  {
    icon: Layers,
    title: 'One Place, Not Ten Tabs',
    body: 'Notes, tasks, and meeting context in a single interface. Switch less. Think more. Close a browser tab you\'ve had open for a month.',
  },
]

export function Features() {
  return (
    <section id="features" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <motion.div variants={fadeInUp} className="mb-4">
            <Badge>What Neutral does</Badge>
          </motion.div>
          <motion.h2
            variants={fadeInUp}
            className="text-4xl font-bold mb-4 tracking-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Everything you need.
            <br />
            Nothing you don&apos;t.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="text-base max-w-md mx-auto"
            style={{ color: 'var(--text-secondary)' }}
          >
            Six features. Carefully chosen. None of them trying to replace your judgment.
          </motion.p>
        </motion.div>

        {/* Feature grid — 3 columns on desktop, 2 on tablet, 1 on mobile */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {FEATURES.map((feature) => (
            <motion.div key={feature.title} variants={fadeInUp}>
              <Card interactive className="h-full">
                {/* Icon — 24px, accent color per Ingrid's spec */}
                <feature.icon
                  size={24}
                  className="mb-4"
                  style={{ color: 'var(--accent)' }}
                />
                <h3
                  className="text-lg font-semibold mb-2"
                  style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
                >
                  {feature.title}
                </h3>
                <p
                  className="text-sm leading-relaxed"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {feature.body}
                </p>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
