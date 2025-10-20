import Link from "next/link";
import ticketsData from "../tickets.json";

type Ticket = {
  number: number;
  title: string;
  author: string;
  github: string;
  created_at: string;
  tags: string[];
  body: string[];
};

type TicketsFile = { tickets: Ticket[] };

export default function TicketsPage() {
  const { tickets } = ticketsData as TicketsFile;

  return (
    <main className="centered-page">
      <header>
        <h1 className="h1">Authors Tickets</h1>
        <p className="lead">Open tickets and letters from project authors</p>
      </header>

      <div className="hr" />

      <section>
        <ul className="center-list">
          {tickets.map((t) => (
            <li key={t.number} style={{ marginTop: '1.25rem' }}>
              {/* Prominent number + big title */}
              <div className="muted">Ticket <strong>#{t.number}</strong> · {t.created_at}</div>
              <h2 className="h2" style={{ marginTop: '0.25rem' }}>{t.title}</h2>

              {/* Left-aligned body */}
              <div style={{ textAlign: 'left', margin: '0.75rem auto 0', maxWidth: 680 }}>
                {t.body.map((p, i) => (
                  <p key={i} style={{ marginTop: i === 0 ? 0 : '0.75rem' }}>{p}</p>
                ))}

                {/* Tags under body */}
                <div style={{ marginTop: '0.75rem' }}>
                  {t.tags.map((tag, i) => (
                    <span key={i} style={{ marginRight: '0.5rem' }}>#{tag}</span>
                  ))}
                </div>

                {/* Signature line */}
                <div className="muted" style={{ marginTop: '0.75rem' }}>
                  — <a href={t.github} target="_blank" rel="noopener noreferrer">{t.author}</a>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <div className="hr" />

      <nav style={{ display: 'grid', gap: '0.75rem' }}>
        <Link href="/">Home</Link>
        <Link href="/features">Features</Link>
        <Link href="/documentation">Documentation</Link>
      </nav>
    </main>
  );
}
