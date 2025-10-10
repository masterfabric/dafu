# DAFU Website Deployment Guide

This guide covers deploying the DAFU website to various platforms.

## 🚀 Quick Deploy

### Vercel (Recommended)

The easiest way to deploy your Next.js app is to use [Vercel](https://vercel.com):

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   cd web
   vercel
   ```

3. **Production Deploy**
   ```bash
   vercel --prod
   ```

**Configuration:**
- Framework Preset: Next.js
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`

### Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build the project**
   ```bash
   npm run build
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod
   ```

**netlify.toml configuration:**
```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

### Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM node:18-alpine AS base

   # Install dependencies only when needed
   FROM base AS deps
   RUN apk add --no-cache libc6-compat
   WORKDIR /app

   COPY package.json package-lock.json ./
   RUN npm ci

   # Rebuild the source code only when needed
   FROM base AS builder
   WORKDIR /app
   COPY --from=deps /app/node_modules ./node_modules
   COPY . .

   RUN npm run build

   # Production image
   FROM base AS runner
   WORKDIR /app

   ENV NODE_ENV production

   RUN addgroup --system --gid 1001 nodejs
   RUN adduser --system --uid 1001 nextjs

   COPY --from=builder /app/public ./public
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

   USER nextjs

   EXPOSE 3000

   ENV PORT 3000

   CMD ["node", "server.js"]
   ```

2. **Update next.config.ts**
   ```typescript
   const nextConfig: NextConfig = {
     output: 'standalone',
     // ... other config
   };
   ```

3. **Build and Run**
   ```bash
   docker build -t dafu-web .
   docker run -p 3000:3000 dafu-web
   ```

### AWS Amplify

1. **Connect your repository** to AWS Amplify
2. **Configure build settings:**
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

## 🌐 Custom Domain Setup

### Vercel
1. Go to your project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### DNS Configuration
```
Type: CNAME
Name: www
Value: <your-deployment-url>

Type: A
Name: @
Value: <platform-ip-address>
```

## 🔒 Environment Variables

Set these environment variables in your deployment platform:

```bash
# Production URL
NEXT_PUBLIC_SITE_URL=https://dafu.masterfabric.co

# API URL (when API is ready)
NEXT_PUBLIC_API_URL=https://api.masterfabric.co

# Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

## 📊 Performance Optimization

### Build Optimization
```bash
# Analyze bundle size
npm run build -- --profile

# Check for optimization opportunities
npx next-bundle-analyzer
```

### CDN Configuration
- Enable compression (Gzip/Brotli)
- Configure cache headers
- Use image optimization services
- Enable HTTP/2

### Recommended Headers
```
Cache-Control: public, max-age=31536000, immutable (for static assets)
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

## 🔍 SEO Checklist

Before deploying, ensure:

- [ ] All meta tags are configured
- [ ] Sitemap.xml is generated
- [ ] Robots.txt is present
- [ ] Open Graph images are created
- [ ] Canonical URLs are set
- [ ] Structured data (JSON-LD) is included
- [ ] Page load time < 3 seconds
- [ ] Mobile-friendly design
- [ ] HTTPS enabled

## 🧪 Pre-deployment Testing

1. **Build Test**
   ```bash
   npm run build
   npm start
   ```

2. **Lighthouse Audit**
   - Performance: 90+
   - Accessibility: 90+
   - Best Practices: 90+
   - SEO: 90+

3. **Cross-browser Testing**
   - Chrome
   - Firefox
   - Safari
   - Edge

4. **Mobile Testing**
   - iOS Safari
   - Chrome Mobile
   - Samsung Internet

## 📈 Monitoring

### Vercel Analytics
Add Vercel Analytics to track:
- Page views
- Performance metrics
- User engagement

```typescript
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
```

### Google Analytics
```typescript
// app/layout.tsx
<script
  async
  src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
/>
<script
  dangerouslySetInnerHTML={{
    __html: `
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
    `,
  }}
/>
```

## 🚨 Troubleshooting

### Build Failures
- Clear `.next` directory
- Delete `node_modules` and reinstall
- Check Node.js version (18+)

### Performance Issues
- Enable static generation where possible
- Optimize images with next/image
- Implement code splitting
- Use dynamic imports for heavy components

### SEO Issues
- Verify robots.txt is accessible
- Check sitemap.xml generation
- Ensure meta tags are rendered server-side
- Test with Google Search Console

## 📝 Deployment Checklist

- [ ] Build succeeds locally
- [ ] All environment variables set
- [ ] Custom domain configured
- [ ] SSL/HTTPS enabled
- [ ] Analytics integrated
- [ ] Error tracking setup
- [ ] Performance monitoring active
- [ ] Backup strategy in place
- [ ] CI/CD pipeline configured
- [ ] Documentation updated

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18
      - name: Install dependencies
        run: npm ci
      - name: Build
        run: npm run build
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

**For more information, visit:**
- [Next.js Deployment Docs](https://nextjs.org/docs/deployment)
- [Vercel Documentation](https://vercel.com/docs)
- [DAFU Main Repository](https://github.com/MasterFabric/dafu)

