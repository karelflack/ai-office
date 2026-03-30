// Shared Framer Motion animation variants — minimal and consistent.
// Scroll animations use whileInView with once: true so they only trigger on first reveal.

import type { Variants } from 'framer-motion'

/** Fade in while sliding up slightly — used for section content on scroll */
export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 12,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
}

/** Stagger container — wraps children that should animate in sequence */
export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
}

/** Floating animation for hero product screenshot */
export const floatingImage = {
  animate: {
    y: [0, -6, 0],
  },
  transition: {
    repeat: Infinity,
    duration: 4,
    ease: 'easeInOut',
  },
}
