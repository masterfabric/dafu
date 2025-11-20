'use client';

import Link from "next/link";
import { useEffect, useState } from "react";
import ticketsData from "../tickets.json";
import { GitHubHoverCard } from "../components/GitHubHoverCard";

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

interface GitHubUser {
  login: string;
  name: string;
  avatar_url: string;
  bio: string;
  company: string;
  location: string;
  blog: string;
  public_repos: number;
  followers: number;
  following: number;
  html_url: string;
  created_at: string;
}

function extractUsername(githubUrl: string): string {
  const match = githubUrl.match(/github\.com\/([^\/]+)/);
  return match ? match[1] : '';
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
  });
}

export default function TicketsPage() {
  const { tickets } = ticketsData as TicketsFile;
  const [userData, setUserData] = useState<Record<string, GitHubUser>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    const fetchUserData = async () => {
      const usernames = tickets.map(t => extractUsername(t.github));
      const uniqueUsernames = [...new Set(usernames)];

      const data: Record<string, GitHubUser> = {};
      const loadingState: Record<string, boolean> = {};

      for (const username of uniqueUsernames) {
        if (!username) continue;
        loadingState[username] = true;
        try {
          const response = await fetch(`/api/github/user?username=${username}`);
          if (response.ok) {
            const user = await response.json();
            data[username] = user;
          }
        } catch (error) {
          console.error(`Failed to fetch user data for ${username}:`, error);
        } finally {
          loadingState[username] = false;
        }
      }

      setUserData(data);
      setLoading(loadingState);
    };

    fetchUserData();
  }, []);

  return (
    <main className="centered-page">
      <header>
        <h1 className="h1">Authors Tickets</h1>
        <p className="lead">Open tickets and letters from project authors</p>
      </header>

      <div className="hr" />

      <section>
        <ul className="center-list">
          {tickets.map((t) => {
            const username = extractUsername(t.github);
            const user = userData[username];
            const isLoading = loading[username];

            return (
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

                  {/* Signature line with avatar */}
                  <div style={{ marginTop: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span className="muted">—</span>
                    <GitHubHoverCard
                      content={
                        user ? (
                          <div className="github-card-content">
                            <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                <img
                                  src={user.avatar_url}
                                  alt={user.name}
                                  style={{
                                    width: '48px',
                                    height: '48px',
                                    borderRadius: '50%',
                                  }}
                                />
                                <div>
                                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{user.name}</div>
                                  <div className="muted" style={{ fontSize: '0.75rem' }}>@{user.login}</div>
                                </div>
                              </div>
                              {user.bio && (
                                <div style={{ fontSize: '0.875rem', color: '#4b5563', marginTop: '8px' }}>
                                  {user.bio}
                                </div>
                              )}
                            </div>
                            <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                              <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                                {user.location && (
                                  <span className="muted">{user.location}</span>
                                )}
                                {user.company && (
                                  <span className="muted">{user.company}</span>
                                )}
                              </div>
                            </div>
                            <div style={{ padding: '12px', display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                              <span className="muted">
                                <strong style={{ color: '#111827' }}>{user.public_repos}</strong> repositories
                              </span>
                              <span className="muted">
                                <strong style={{ color: '#111827' }}>{user.followers}</strong> followers
                              </span>
                              <span className="muted">
                                <strong style={{ color: '#111827' }}>{user.following}</strong> following
                              </span>
                            </div>
                            <div style={{ padding: '12px' }}>
                              <a
                                href={user.html_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                  fontSize: '0.75rem',
                                  color: '#3b82f6',
                                  textDecoration: 'none',
                                }}
                              >
                                View on GitHub →
                              </a>
                            </div>
                          </div>
                        ) : (
                          <div className="github-card-content" style={{ padding: '12px' }}>
                            <div className="muted" style={{ fontSize: '0.875rem' }}>
                              Loading user info...
                            </div>
                          </div>
                        )
                      }
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {user?.avatar_url && (
                          <img
                            src={user.avatar_url}
                            alt={user.name}
                            style={{
                              width: '20px',
                              height: '20px',
                              borderRadius: '50%',
                              flexShrink: 0,
                            }}
                          />
                        )}
                        {isLoading && !user && (
                          <div
                            style={{
                              width: '20px',
                              height: '20px',
                              borderRadius: '50%',
                              backgroundColor: '#e5e7eb',
                              flexShrink: 0,
                            }}
                          />
                        )}
                        <a
                          href={t.github}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="muted"
                        >
                          {t.author}
                        </a>
                      </div>
                    </GitHubHoverCard>
                  </div>
                </div>
              </li>
            );
          })}
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
