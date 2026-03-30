import { Navbar } from '@/components/nav/Navbar'
import { Hero } from '@/components/sections/Hero'
import { Features } from '@/components/sections/Features'
import { FeatureHighlight } from '@/components/sections/FeatureHighlight'
import { Testimonials } from '@/components/sections/Testimonials'
import { Pricing } from '@/components/sections/Pricing'
import { CTA } from '@/components/sections/CTA'
import { Footer } from '@/components/sections/Footer'

/**
 * Homepage — assembles all sections in wireframe order:
 * Nav → Hero → Features → Deep Feature Highlights → Testimonials → Pricing → CTA → Footer
 */
export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <FeatureHighlight />
        <Testimonials />
        <Pricing />
        <CTA />
      </main>
      <Footer />
    </>
  )
}
