# DAFU Website

Minimal, centered Next.js site for DAFU – Enterprise Fraud Detection Platform.

## 🎨 Design

- **Text-first, centered** layout (single column, max 720px)
- **Typography**: Fira Code across the site
- **Colors**: Pure white background, navy emphasis (`#1e40af`)
- **No shadows / outlines**: flat, lightweight UI
- **Global footer** (every page): Source, Contact, Last updated

## 🧭 Pages

- `/` Home: Focus Sectors, Key Metrics, Core Capabilities, Upcoming Features, Quick Start, Project Authors
- `/features` Features (centered text-only)
- `/documentation` Links to repo docs (CLI, Guides, Docker)

## 🔍 Links (Docs in repo)

- Docs root: `https://github.com/masterfabric/dafu/tree/dev/docs`
- CLI: `https://github.com/masterfabric/dafu/tree/dev/docs/cli`
- Guides: `https://github.com/masterfabric/dafu/tree/dev/docs/guides`
- Docker: `https://github.com/masterfabric/dafu/tree/dev/docs/docker`

## 👥 Project Authors

- Data is read from `app/data.json` and rendered on the home page.
- Schema:

```json
{
  "authors": [
    {
      "full_name": "Full Name",
      "github": "https://github.com/username",
      "linkedin": "https://www.linkedin.com/in/username/",
      "bio": "Optional short bio"
    }
  ]
}
```

Add new authors by appending to the array. Link labels render in lowercase (github · linkedin).

## 🚀 Quick Start

```bash
# Install deps
npm install

# Dev
npm run dev

# Build (production)
npm run build

# Start (production)
npm run start
```

Open `http://localhost:3000`.

## 🧱 Tech

- Next.js 15 (App Router)
- TypeScript, Tailwind (utility layers only), PostCSS
- SEO: metadata, sitemap, robots.txt, JSON‑LD

## 🧹 Conventions

- Single-column, centered content via `.centered-page`
- Reusable typographic helpers: `.h1`, `.h2`, `.h3`, `.lead`, `.muted`, `.hr`, `.center-list`
- No component library; pure text links and lists

## 📦 Structure

```
web/
├── app/
│   ├── layout.tsx            # Global SEO + footer
│   ├── page.tsx              # Home (centered)
│   ├── features/page.tsx     # Features (centered)
│   ├── documentation/page.tsx# Docs links
│   ├── data.json             # Authors data
│   ├── globals.css           # Design tokens & utilities
│   ├── sitemap.ts            # Sitemap
│   └── manifest.ts           # PWA manifest
└── public/                   # Static assets (robots.txt, icons)
```

## 🔗 Footer

- Source: `https://github.com/masterfabric/dafu/`
- Contact: `dafu@masterfabric.co`
- Last updated: rendered per-request

## 📝 License

AGPL-3.0 – see [LICENSE](../../LICENSE).

— Built with ❤️ by MasterFabric
