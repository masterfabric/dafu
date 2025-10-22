import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Documentation - DAFU Platform",
  description: "Guides and API references for DAFU.",
};

const GH_BASE = "https://github.com/masterfabric/dafu/tree/dev/docs";

export default function DocumentationPage() {
  return (
    <main className="centered-page">
      <header>
        <h1 className="h1">Documentation</h1>
        <p className="muted">Everything you need to use DAFU</p>
      </header>

      <div className="hr" />

      <section>
        <h2 className="h2">Overview</h2>
        <ul className="center-list">
          <li>
            <a href={`${GH_BASE}`} target="_blank" rel="noopener noreferrer">Docs (tree/dev/docs)</a>
          </li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h2 className="h2">CLI</h2>
        <ul className="center-list">
          <li>
            <a href={`${GH_BASE}/cli`} target="_blank" rel="noopener noreferrer">CLI (docs/cli)</a>
          </li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h2 className="h2">Guides</h2>
        <ul className="center-list">
          <li>
            <a href={`${GH_BASE}/guides`} target="_blank" rel="noopener noreferrer">Guides (docs/guides)</a>
          </li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h2 className="h2">Docker</h2>
        <ul className="center-list">
          <li>
            <a href={`${GH_BASE}/docker`} target="_blank" rel="noopener noreferrer">Docker (docs/docker)</a>
          </li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h2 className="h2">Assets</h2>
        <ul className="center-list">
          <li>
            <a href={`${GH_BASE}/assets`} target="_blank" rel="noopener noreferrer">Assets (docs/assets)</a>
          </li>
        </ul>
      </section>

      <div className="hr" />

      <nav style={{ display: 'grid', gap: '0.75rem' }}>
        <Link href="/">Home</Link>
        <Link href="/features">Features</Link>
      </nav>
    </main>
  );
}
