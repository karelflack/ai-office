import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    // Required for static export — images should be pre-optimised as .webp at source
    unoptimized: true,
  },
}

export default nextConfig
