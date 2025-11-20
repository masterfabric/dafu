'use client';

import { useEffect, useState } from 'react';
import { GitHubHoverCard } from './GitHubHoverCard';

interface Commit {
  sha: string;
  fullSha?: string;
  message: string;
  fullMessage?: string;
  author: string;
  avatar?: string;
  date: string;
  url: string;
}

interface PR {
  number: number;
  title: string;
  body?: string;
  author: string;
  avatar?: string;
  createdAt?: string;
  updatedAt?: string;
  mergedAt?: string | null;
  additions?: number;
  deletions?: number;
  changedFiles?: number;
  url: string;
}

interface GitHubData {
  commits: Commit[];
  openPRs: PR[];
  mergedPRs: PR[];
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
}

function formatFullDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function truncateText(text: string, maxLength: number): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export default function GitHubActivity() {
  const [data, setData] = useState<GitHubData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch('/api/github');
        if (!response.ok) {
          throw new Error('Failed to fetch GitHub data');
        }
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 300000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <section>
        <h3 className="h3">Recent Activity</h3>
        <p className="muted">Loading...</p>
      </section>
    );
  }

  if (error || !data) {
    return (
      <section>
        <h3 className="h3">Recent Activity</h3>
        <p className="muted">Unable to load activity data.</p>
      </section>
    );
  }

  return (
    <>
      {/* Recent Commits */}
      <section>
        <h3 className="h3">Recent Commits</h3>
        <ul className="center-list" style={{ textAlign: 'left', maxWidth: '800px', margin: '0 auto' }}>
          {data.commits.slice(0, 5).map((commit) => (
            <li key={commit.sha} style={{ marginBottom: '0.75rem' }}>
              <GitHubHoverCard
                content={
                  <div className="github-card-content">
                    <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        {commit.avatar && (
                          <img
                            src={commit.avatar}
                            alt={commit.author}
                            style={{
                              width: '20px',
                              height: '20px',
                              borderRadius: '50%',
                            }}
                          />
                        )}
                        <strong style={{ fontSize: '0.875rem' }}>{commit.author}</strong>
                        <span className="muted" style={{ fontSize: '0.75rem' }}>
                          {formatFullDate(commit.date)}
                        </span>
                      </div>
                      <code style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                        {commit.fullSha || commit.sha}
                      </code>
                    </div>
                    <div style={{ padding: '12px' }}>
                      <div style={{ fontSize: '0.875rem', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                        {commit.fullMessage || commit.message}
                      </div>
                      <a
                        href={commit.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-block',
                          marginTop: '8px',
                          fontSize: '0.75rem',
                          color: '#3b82f6',
                          textDecoration: 'none',
                        }}
                      >
                        View on GitHub →
                      </a>
                    </div>
                  </div>
                }
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                  {commit.avatar && (
                    <img
                      src={commit.avatar}
                      alt={commit.author}
                      style={{
                        width: '20px',
                        height: '20px',
                        borderRadius: '50%',
                        flexShrink: 0,
                      }}
                    />
                  )}
                  <div style={{ flex: 1 }}>
                    <a
                      href={commit.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ textDecoration: 'none' }}
                    >
                      <code style={{ fontSize: '0.875rem', color: '#3b82f6' }}>
                        {commit.sha}
                      </code>
                      {' '}
                      <span>{commit.message}</span>
                    </a>
                    <div className="muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                      by {commit.author} · {formatDate(commit.date)}
                    </div>
                  </div>
                </div>
              </GitHubHoverCard>
            </li>
          ))}
        </ul>
        <p style={{ marginTop: '1rem' }}>
          <a
            href={`https://github.com/masterfabric/dafu/commits/dev`}
            target="_blank"
            rel="noopener noreferrer"
          >
            View all commits →
          </a>
        </p>
      </section>

      <div className="hr" />

      {/* Open Pull Requests */}
      {data.openPRs.length > 0 && (
        <>
          <section>
            <h3 className="h3">Open Pull Requests</h3>
            <ul className="center-list" style={{ textAlign: 'left', maxWidth: '800px', margin: '0 auto' }}>
              {data.openPRs.map((pr) => (
                <li key={pr.number} style={{ marginBottom: '0.75rem' }}>
                  <GitHubHoverCard
                    content={
                      <div className="github-card-content">
                        <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            {pr.avatar && (
                              <img
                                src={pr.avatar}
                                alt={pr.author}
                                style={{
                                  width: '20px',
                                  height: '20px',
                                  borderRadius: '50%',
                                }}
                              />
                            )}
                            <strong style={{ fontSize: '0.875rem' }}>{pr.author}</strong>
                            <span className="muted" style={{ fontSize: '0.75rem' }}>
                              {formatFullDate(pr.updatedAt || pr.createdAt || '')}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                            #{pr.number}: {pr.title}
                          </div>
                        </div>
                        {pr.body && (
                          <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                            <div style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#4b5563' }}>
                              {truncateText(pr.body.replace(/[#*`]/g, ''), 200)}
                            </div>
                          </div>
                        )}
                        {(pr.additions !== undefined || pr.deletions !== undefined || pr.changedFiles !== undefined) && (
                          <div style={{ padding: '12px', display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                            {pr.changedFiles !== undefined && (
                              <span className="muted">
                                {pr.changedFiles} {pr.changedFiles === 1 ? 'file' : 'files'} changed
                              </span>
                            )}
                            {pr.additions !== undefined && pr.additions > 0 && (
                              <span style={{ color: '#16a34a' }}>+{pr.additions}</span>
                            )}
                            {pr.deletions !== undefined && pr.deletions > 0 && (
                              <span style={{ color: '#dc2626' }}>-{pr.deletions}</span>
                            )}
                          </div>
                        )}
                        <div style={{ padding: '12px' }}>
                          <a
                            href={pr.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              fontSize: '0.75rem',
                              color: '#3b82f6',
                              textDecoration: 'none',
                            }}
                          >
                            View pull request →
                          </a>
                        </div>
                      </div>
                    }
                  >
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                      {pr.avatar && (
                        <img
                          src={pr.avatar}
                          alt={pr.author}
                          style={{
                            width: '20px',
                            height: '20px',
                            borderRadius: '50%',
                            flexShrink: 0,
                          }}
                        />
                      )}
                      <div style={{ flex: 1 }}>
                        <a
                          href={pr.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ textDecoration: 'none' }}
                        >
                          <strong>#{pr.number}</strong> {pr.title}
                        </a>
                        <div className="muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                          by {pr.author} · updated {formatDate(pr.updatedAt || pr.createdAt || '')}
                        </div>
                      </div>
                    </div>
                  </GitHubHoverCard>
                </li>
              ))}
            </ul>
          </section>
          <div className="hr" />
        </>
      )}

      {/* Recently Merged PRs */}
      {data.mergedPRs.length > 0 && (
        <section>
          <h3 className="h3">Recently Merged</h3>
          <ul className="center-list" style={{ textAlign: 'left', maxWidth: '800px', margin: '0 auto' }}>
            {data.mergedPRs.map((pr) => (
              <li key={pr.number} style={{ marginBottom: '0.75rem' }}>
                <GitHubHoverCard
                  content={
                    <div className="github-card-content">
                      <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                          {pr.avatar && (
                            <img
                              src={pr.avatar}
                              alt={pr.author}
                              style={{
                                width: '20px',
                                height: '20px',
                                borderRadius: '50%',
                              }}
                            />
                          )}
                          <strong style={{ fontSize: '0.875rem' }}>{pr.author}</strong>
                          <span className="muted" style={{ fontSize: '0.75rem' }}>
                            merged {pr.mergedAt ? formatFullDate(pr.mergedAt) : 'recently'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>
                          #{pr.number}: {pr.title}
                        </div>
                      </div>
                      {pr.body && (
                        <div style={{ padding: '12px', borderBottom: '1px solid #e5e7eb' }}>
                          <div style={{ fontSize: '0.875rem', lineHeight: '1.5', color: '#4b5563' }}>
                            {truncateText(pr.body.replace(/[#*`]/g, ''), 200)}
                          </div>
                        </div>
                      )}
                      {(pr.additions !== undefined || pr.deletions !== undefined || pr.changedFiles !== undefined) && (
                        <div style={{ padding: '12px', display: 'flex', gap: '16px', fontSize: '0.75rem' }}>
                          {pr.changedFiles !== undefined && (
                            <span className="muted">
                              {pr.changedFiles} {pr.changedFiles === 1 ? 'file' : 'files'} changed
                            </span>
                          )}
                          {pr.additions !== undefined && pr.additions > 0 && (
                            <span style={{ color: '#16a34a' }}>+{pr.additions}</span>
                          )}
                          {pr.deletions !== undefined && pr.deletions > 0 && (
                            <span style={{ color: '#dc2626' }}>-{pr.deletions}</span>
                          )}
                        </div>
                      )}
                      <div style={{ padding: '12px' }}>
                        <a
                          href={pr.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: '0.75rem',
                            color: '#3b82f6',
                            textDecoration: 'none',
                          }}
                        >
                          View pull request →
                        </a>
                      </div>
                    </div>
                  }
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                    {pr.avatar && (
                      <img
                        src={pr.avatar}
                        alt={pr.author}
                        style={{
                          width: '20px',
                          height: '20px',
                          borderRadius: '50%',
                          flexShrink: 0,
                        }}
                      />
                    )}
                    <div style={{ flex: 1 }}>
                      <a
                        href={pr.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ textDecoration: 'none' }}
                      >
                        <strong>#{pr.number}</strong> {pr.title}
                      </a>
                      <div className="muted" style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>
                        by {pr.author} · merged {pr.mergedAt ? formatDate(pr.mergedAt) : 'recently'}
                      </div>
                    </div>
                  </div>
                </GitHubHoverCard>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}

