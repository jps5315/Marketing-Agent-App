/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  experimental: {
    suppressHydrationWarning: true
  },
  transpilePackages: ['lucide-react'],
}

module.exports = nextConfig
