import Link from "next/link";
import authorsData from "./data.json";

type Author = {
  full_name: string;
  github: string;
  linkedin: string;
  bio?: string;
};

type DataFile = {
  authors: Author[];
};

export default function Home() {
  const today = new Date().toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  const authors = (authorsData as DataFile).authors;

  return (
    <main className="centered-page">
      <header>
        <h1 className="h1">DAFU</h1>
        <p className="muted">Data Analytics Functional Utilities</p>
      </header>

      <div className="hr" />

      <section>
        <h2 className="h2">Enterprise Fraud Detection</h2>
        <p className="lead">Advanced ML-based fraud detection with sub-50ms latency, 99.9% uptime, and 10K+ TPS.</p>
      </section>

      <div className="hr" />

      {/* Focus Sectors */}
      <section>
        <h3 className="h3">Focus Sectors</h3>
        <ul className="center-list">
          <li><strong>Financial Services</strong> — banks, issuers, acquirers</li>
          <li><strong>E‑commerce</strong> — marketplaces, retail, subscription</li>
          <li><strong>Payments</strong> — card-not-present, wallets, PSPs</li>
          <li><strong>Fintech</strong> — neobanks, lending, crypto on/off-ramps</li>
          <li><strong>Travel & Ticketing</strong> — OTA, airlines, events</li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h3 className="h3">Key Metrics</h3>
        <ul className="center-list">
          <li>{"<50ms"} API latency</li>
          <li>99.9% uptime</li>
          <li>10K+ TPS throughput</li>
          <li>95%+ detection accuracy</li>
        </ul>
        <p className="muted" style={{ marginTop: "0.75rem" }}>Last updated: {today}</p>
      </section>

      <div className="hr" />

      <section>
        <h3 className="h3">Core Capabilities</h3>
        <ul className="center-list">
          <li>Isolation Forest, LSTM & GRU models</li>
          <li>Real-time stream and batch processing</li>
          <li>Model persistence & comparison</li>
          <li>Kubernetes-ready infrastructure</li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h3 className="h3">Upcoming Features</h3>
        <ul className="center-list">
          <li>Real-time API — Sub-50ms fraud scoring</li>
          <li>Enterprise Security — OAuth2, JWT, RBAC</li>
          <li>Scalable Architecture — Kubernetes auto-scaling</li>
          <li>Advanced Monitoring — Prometheus, Grafana, Jaeger</li>
          <li>High-throughput Processing — 10,000+ TPS optimization</li>
        </ul>
      </section>

      <div className="hr" />

      <section>
        <h3 className="h3">Quick Start</h3>
        <pre style={{ textAlign: 'left', margin: '0 auto', maxWidth: 640 }}>
{`git clone https://github.com/MasterFabric/dafu.git
cd dafu
chmod +x dafu
./dafu
# dafu> fraud-detection`}
        </pre>
      </section>

      <div className="hr" />

      <section>
        <h3 className="h3">Project Authors</h3>
        <ul className="center-list">
          {authors.map((a, i) => (
            <li key={i}>
              <div><strong>{a.full_name}</strong></div>
              {a.bio && <div className="muted" style={{ marginTop: '0.25rem' }}>{a.bio}</div>}
              <div style={{ marginTop: '0.25rem' }}>
                <a href={a.github} target="_blank" rel="noopener noreferrer">github</a>
                <span className="muted"> · </span>
                <a href={a.linkedin} target="_blank" rel="noopener noreferrer">linkedin</a>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <div className="hr" />

      <nav style={{ display: 'grid', gap: '0.75rem' }}>
        <Link href="/features">Features</Link>
        <Link href="/documentation">Documentation</Link>
      </nav>
    </main>
  );
}
