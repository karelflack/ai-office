'use client'

import { motion } from 'framer-motion'
import { ArrowRight, FileText, Calendar, BarChart2, Mail, Search, Layers } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card } from '@/components/ui/Card'
import { fadeInUp, staggerContainer } from '@/lib/motion'
import type { LucideIcon } from 'lucide-react'

interface FeatureCardData {
  icon: LucideIcon
  title: string
  body: string
}

// Feature grid — six agents that make up the AI Office team
const FEATURES: FeatureCardData[] = [
  {
    icon: Search,
    title: 'Research on Demand',
    body: 'Describe what you need to know. The Research Agent finds, structures, and summarizes — returning a briefing you can act on, not a list of links to read.',
  },
  {
    icon: FileText,
    title: 'Documents That Write Themselves',
    body: 'From proposals to reports to memos — describe the output, attach your context, and receive a draft in your voice. Review and send.',
  },
  {
    icon: Mail,
    title: 'Email Without the Back-and-Forth',
    body: 'AI Office drafts your replies, follow-ups, and cold outreach. It reads the thread, matches your tone, and gets it right the first time.',
  },
  {
    icon: Calendar,
    title: 'Scheduling That Actually Works',
    body: 'Book meetings, block focus time, and resolve conflicts without touching your calendar. The Scheduler Agent manages the overhead you resent.',
  },
  {
    icon: BarChart2,
    title: 'Analysis Without the Spreadsheet',
    body: 'Drop in your data and describe the question. The Analyst Agent surfaces the answer — not the pivot table you have to interpret yourself.',
  },
  {
    icon: Layers,
    title: 'Parallel, Not Sequential',
    body: 'Multiple agents work at the same time. While one researches, another drafts, another schedules. Complex tasks finish in minutes, not hours.',
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
            <Badge>What AI Office does</Badge>
          </motion.div>
          <motion.h2
            variants={fadeInUp}
            className="text-4xl font-bold mb-4 tracking-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Your team.
            <br />
            Available immediately.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="text-base max-w-md mx-auto"
            style={{ color: 'var(--text-secondary)' }}
          >
            Six specialized agents. Each one expert at a different kind of work. All of them reporting to you.
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
              <Card interactive className="h-full group">
                {/* Icon — 24px, accent color */}
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
