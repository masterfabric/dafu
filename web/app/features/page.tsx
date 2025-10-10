import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Features - DAFU Platform",
  description: "Explore DAFU's ML-based fraud detection capabilities.",
};

export default function FeaturesPage() {
  return (
    <main className="centered-page">
      <header>
        <h1 className="h1">Features</h1>
        <p className="muted">Production-ready capabilities</p>
      </header>

      <div className="hr" />

      <section>
        <h2 className="h2">Implemented</h2>
        <ul className="center-list">
          <li>Interactive CLI with persistent sessions</li>
          <li>Unified model interface and comparison</li>
          <li>Isolation Forest, LSTM & GRU models</li>
          <li>Stream and batch prediction modes</li>
          <li>Model persistence (save / load)</li>
          <li>Data preprocessing and analysis</li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h2 className="h2">Planned</h2>
        <ul className="center-list">
          <li>Sub-50ms real-time API</li>
          <li>OAuth2 / JWT / RBAC</li>
          <li>Kubernetes auto-scaling</li>
          <li>Prometheus / Grafana / Jaeger</li>
        </ul>
      </section>

      <div className="hr" />

      <nav style={{ display: 'grid', gap: '0.75rem' }}>
        <Link href="/">Home</Link>
        <Link href="/documentation">Documentation</Link>
      </nav>
    </main>
  );
}
