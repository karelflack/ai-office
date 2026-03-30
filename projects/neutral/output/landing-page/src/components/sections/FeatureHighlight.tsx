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
  // If true, image is on the left and copy on the right
  imageSide: 'left' | 'right'
}

// Deep feature highlights — copy verbatim from Jorunn's brand-copy.md
const HIGHLIGHTS: HighlightBlock[] = [
  {
    eyebrow: 'Your thinking, connected',
    headline: 'Notes that find each other.',
    body: 'Most note-taking tools leave organization to you. Neutral surfaces connections you didn\'t notice: the project you scoped last month, the research you saved last week, the idea you had at 11pm. Your thoughts become a knowledge base without the overhead of maintaining one.',
    bullets: [
      'Automatic backlinks between related notes',
      'AI-powered topic clustering across your history',
      'Full-text search that understands context, not just keywords',
    ],
    imageAlt: 'Connected notes interface showing automatic backlinks',
    imageSide: 'left',
  },
  {
    eyebrow: 'Privacy-first, from the ground up',
    headline: 'Your data is yours.\nFull stop.',
    body: 'We built Neutral with a simple rule: we shouldn\'t see what you\'re working on. That\'s not a legal disclaimer — it\'s an architectural decision. End-to-end encryption means your notes are unreadable to us. No exceptions, no training on your data, no "we may use your content to improve our services."',
    bullets: [
      'End-to-end encryption on all notes and transcripts',
      'Zero-knowledge architecture — Neutral cannot read your content',
      'Your notes never train our AI models',
    ],
    imageAlt: 'Privacy architecture diagram showing encryption',
    imageSide: 'right',
  },
  {
    eyebrow: 'Meeting-ready, always',
    headline: 'Notes done before the\nmeeting ends.',
    body: 'Neutral works in the background while you stay present. No meeting bot joins your call — transcription runs locally. By the time you close the meeting window, your raw notes have been organized, the action items extracted, and the summary is ready to share.',
    bullets: [
      'Local transcription — no bot, no intrusion, no "Otter is recording this call"',
      'Draft a follow-up email directly from your meeting notes',
      'Auto-extracts decisions and action items with one click',
    ],
    imageAlt: 'Meeting notes interface showing auto-organized summary',
    imageSide: 'left',
  },
]

function ScreenshotPlaceholder({ alt }: { alt: string }) {
  return (
    /*
      Placeholder for product screenshot.
      Replace with <Image src="..." alt={alt} width={600} height={400} /> when assets are ready.
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
                  {/* Preserve intentional line breaks from copy spec */}
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
