'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { fadeInUp, staggerContainer } from '@/lib/motion'

type BillingCycle = 'annual' | 'monthly'

interface PlanData {
  name: string
  tagline: string
  priceAnnual: string
  priceMonthly: string
  priceNote: string
  features: string[]
  cta: string
  // CTA labels are intentional: "Get Started", "Start Free Trial", "Talk to Us"
  // Do not normalize them to one label — per Jorunn's copy notes
  popular?: boolean
}

const PLANS: PlanData[] = [
  {
    name: 'Free',
    tagline: 'Start thinking.',
    priceAnnual: '$0',
    priceMonthly: '$0',
    priceNote: 'per month',
    features: [
      'Up to 500 notes',
      'Basic AI suggestions',
      '5 meeting transcripts / month',
      'Local-only sync',
    ],
    cta: 'Get Started',
  },
  {
    name: 'Pro',
    tagline: 'For professionals who depend on it.',
    priceAnnual: '$12',
    priceMonthly: '$16',
    priceNote: 'per month',
    features: [
      'Everything in Free',
      'Unlimited notes',
      'Unlimited meeting transcripts',
      'Full AI — summarize, connect, draft',
      'End-to-end encryption',
      'Priority support',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Team',
    tagline: 'For the teams that think together.',
    priceAnnual: '$29',
    priceMonthly: '$29',
    priceNote: 'per seat / month',
    features: [
      'Everything in Pro',
      'Shared workspaces and note libraries',
      'Admin controls and audit logs',
      'SSO / SAML',
      'Dedicated onboarding',
    ],
    cta: 'Talk to Us',
  },
]

export function Pricing() {
  const [billing, setBilling] = useState<BillingCycle>('annual')

  return (
    <section id="pricing" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <motion.div variants={fadeInUp} className="mb-4">
            <Badge>Simple pricing</Badge>
          </motion.div>
          <motion.h2
            variants={fadeInUp}
            className="text-4xl font-bold mb-4 tracking-tight"
            style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
          >
            Transparent pricing.
            <br />
            No surprises.
          </motion.h2>
          <motion.p
            variants={fadeInUp}
            className="text-base mb-8"
            style={{ color: 'var(--text-secondary)' }}
          >
            One product. Three tiers. No credits, no usage caps on core features.
          </motion.p>

          {/* Billing toggle */}
          <motion.div variants={fadeInUp} className="inline-flex items-center rounded-button p-1 border" style={{ borderColor: 'var(--bg-border)', backgroundColor: 'var(--bg-surface)' }}>
            <button
              onClick={() => setBilling('annual')}
              className="px-4 py-1.5 text-sm font-medium rounded-button transition-all"
              style={{
                backgroundColor: billing === 'annual' ? 'var(--accent)' : 'transparent',
                color: billing === 'annual' ? '#fff' : 'var(--text-secondary)',
              }}
            >
              Annual
              <span
                className="ml-1.5 text-xs"
                style={{ color: billing === 'annual' ? 'rgba(255,255,255,0.75)' : 'var(--text-muted)' }}
              >
                Save 25%
              </span>
            </button>
            <button
              onClick={() => setBilling('monthly')}
              className="px-4 py-1.5 text-sm font-medium rounded-button transition-all"
              style={{
                backgroundColor: billing === 'monthly' ? 'var(--accent)' : 'transparent',
                color: billing === 'monthly' ? '#fff' : 'var(--text-secondary)',
              }}
            >
              Monthly
            </button>
          </motion.div>
        </motion.div>

        {/* Pricing cards */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {PLANS.map((plan) => (
            <motion.div key={plan.name} variants={fadeInUp}>
              <div
                className="relative h-full flex flex-col rounded-card p-6 border transition-colors"
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  // Highlighted border for the popular plan
                  borderColor: plan.popular ? 'var(--accent)' : 'var(--bg-border)',
                }}
              >
                {/* Most popular badge */}
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge>Most popular</Badge>
                  </div>
                )}

                <div className="mb-6">
                  <h3
                    className="text-lg font-semibold mb-1"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {plan.name}
                  </h3>
                  <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
                    {plan.tagline}
                  </p>
                  <div className="flex items-end gap-1">
                    <span
                      className="text-4xl font-bold"
                      style={{ color: 'var(--text-primary)', letterSpacing: '-0.02em' }}
                    >
                      {billing === 'annual' ? plan.priceAnnual : plan.priceMonthly}
                    </span>
                    <span className="text-sm pb-1" style={{ color: 'var(--text-muted)' }}>
                      / {plan.priceNote}
                    </span>
                  </div>
                  {/* Annual billing note for paid plans */}
                  {plan.name !== 'Free' && (
                    <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>
                      {billing === 'annual' ? 'billed annually' : 'billed monthly'}
                    </p>
                  )}
                </div>

                <ul className="flex flex-col gap-3 mb-8 flex-1">
                  {plan.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-start gap-2.5 text-sm"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      <Check size={14} className="mt-0.5 shrink-0" style={{ color: 'var(--accent)' }} />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Button
                  href="#"
                  variant={plan.popular ? 'primary' : 'secondary'}
                  fullWidth
                >
                  {plan.cta}
                </Button>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
