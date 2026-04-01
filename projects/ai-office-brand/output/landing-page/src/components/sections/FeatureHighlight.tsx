'use client'

import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { fadeInUp, staggerContainer } from '@/lib/motion'

interface HighlightBlock {
  eyebrow: string
  headline: string
  body: string
  bullets: string[]
  imageAlt: string
  imageSide: 'left' | 'right'
}

// Deep feature highlights — three key differentiators for AI Office
const HIGHLIGHTS: HighlightBlock[] = [
  {
    eyebrow: 'Your work, delegated',
    headline: 'Describe the task.\nGet the result.',
    body: 'Stop prompting. Start delegating. Tell AI Office what you need in plain English — a competitive analysis, a project proposal, a vendor comparison — and it figures out the rest. The right agents are assigned automatically, work in parallel, and deliver a complete output you can use.',
    bullets: [
      'Multi-step tasks broken down and distributed automatically',
      'Agents hand off to each other — no manual chaining required',
      'Structured, reviewable output — not a wall of AI text',
    ],
    imageAlt: 'Task delegation interface showing agents working in parallel',
    imageSide: 'left',
  },
  {
    eyebrow: 'Built for real work, not demos',
    headline: 'Outputs you can send.\nNot prompts to refine.',
    body: 'Most AI tools make you do the work twice: once prompting, once fixing. AI Office is designed around outputs, not inputs. Every agent knows its job. Every deliverable is structured, formatted, and ready to review. The quality is high enough to use, not just to show.',
    bullets: [
      'Documents in your voice — not generic AI boilerplate',
      'Structured outputs: briefs, reports, drafts, not chat history',
      'One-click refinement when something needs adjustment',
    ],
    imageAlt: 'Document output showing structured briefing with formatting',
    imageSide: 'right',
  },
  {
    eyebrow: 'Works where you already work',
    headline: 'Your tools.\nYour context.',
    body: 'AI Office connects to your calendar, email, and documents. It reads what you already have so you never have to paste the same context twice. When it writes, it writes back to where the output needs to go — your inbox, your doc, your task list.',
    bullets: [
      'Connect Gmail, Google Calendar, Notion, and Slack',
      'AI Office reads your existing context — no re-onboarding per task',
      'Outputs delivered directly to the tools you already use',
    ],
    imageAlt: 'Integrations panel showing connected tools',
    imageSide: 'left',
  },
]

function ScreenshotPlaceholder({ alt }: { alt: string }) {
  return (
    /*
      Placeholder for product screenshot.
      Replace with <Image src="..." alt={alt} width={600} height={400} /> when assets are ready.
      Recommended: 4:3 aspect ratio, .webp format, 1200×900px source.
    */
    <div
      className="w-full aspect-[4/3] rounded-card border flex items-center justify-center"
      style={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--bg-border)' }}
    >
      <p
        className="text-xs font-mono text-center px-4"
        style={{ color: 'var(--text-muted)' }}
      >
        [ Screenshot: {alt} ]
      </p>
    </div>
  )
}

export function FeatureHighlight() {
  return (
    <section className="py-24 px-6">
      <div className="max-w-6xl mx-auto flex flex-col gap-32">
        {HIGHLIGHTS.map((block) => {
          const isImageLeft = block.imageSide === 'left'

          return (
            <motion.div
              key={block.eyebrow}
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className={`flex flex-col ${isImageLeft ? 'lg:flex-row' : 'lg:flex-row-reverse'} items-center gap-12 lg:gap-16`}
            >
              {/* Screenshot side */}
              <motion.div variants={fadeInUp} className="w-full lg:w-1/2">
                <ScreenshotPlaceholder alt={block.imageAlt} />
              </motion.div>

              {/* Copy side */}
              <motion.div
                variants={staggerContainer}
                className="w-full lg:w-1/2 flex flex-col gap-4"
              >
                <motion.div variants={fadeInUp}>
                  <Badge>{block.eyebrow}</Badge>
                </motion.div>

                <motion.h2
                  variants={fadeInUp}
                  className="text-3xl font-bold leading-tight"
                  style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
                >
                  {/* Preserve intentional line breaks */}
                  {block.headline.split('\n').map((line, i) => (
                    <span key={i}>
                      {line}
                      {i < block.headline.split('\n').length - 1 && <br />}
                    </span>
                  ))}
                </motion.h2>

                <motion.p
                  variants={fadeInUp}
                  className="text-base leading-relaxed"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  {block.body}
                </motion.p>

                <motion.ul variants={staggerContainer} className="flex flex-col gap-2">
                  {block.bullets.map((bullet) => (
                    <motion.li
                      key={bullet}
                      variants={fadeInUp}
                      className="flex items-start gap-3 text-sm"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      <Check
                        size={16}
                        className="mt-0.5 shrink-0"
                        style={{ color: 'var(--accent)' }}
                      />
                      {bullet}
                    </motion.li>
                  ))}
                </motion.ul>
              </motion.div>
            </motion.div>
          )
        })}
      </div>
    </section>
  )
}
