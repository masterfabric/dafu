import { NextResponse } from 'next/server';

const GITHUB_OWNER = 'masterfabric';
const GITHUB_REPO = 'dafu';
const GITHUB_API_BASE = 'https://api.github.com';

interface GitHubCommit {
  sha: string;
  commit: {
    message: string;
    author: {
      name: string;
      date: string;
    };
  };
  author: {
    login: string;
    avatar_url: string;
  } | null;
  html_url: string;
}

interface GitHubPR {
  number: number;
  title: string;
  body: string | null;
  state: string;
  created_at: string;
  updated_at: string;
  user: {
    login: string;
    avatar_url: string;
  };
  html_url: string;
  merged_at: string | null;
  additions?: number;
  deletions?: number;
  changed_files?: number;
}

async function fetchGitHubAPI(endpoint: string) {
  const headers: HeadersInit = {
    'Accept': 'application/vnd.github.v3+json',
  };

  const response = await fetch(`${GITHUB_API_BASE}${endpoint}`, {
    headers,
    next: { revalidate: 300 }, // Cache for 5 minutes
  });

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.statusText}`);
  }

  return response.json();
}

export async function GET() {
  try {
    // Fetch recent commits (last 10)
    const commits: GitHubCommit[] = await fetchGitHubAPI(
      `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/commits?per_page=10&sha=dev`
    );

    // Fetch open PRs with stats
    const openPRs: GitHubPR[] = await fetchGitHubAPI(
      `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/pulls?state=open&per_page=10&sort=updated`
    );

    // Fetch PR details with stats for open PRs
    const openPRsWithDetails = await Promise.all(
      openPRs.map(async (pr) => {
        const details = await fetchGitHubAPI(
          `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/pulls/${pr.number}`
        );
        return { ...pr, ...details };
      })
    );

    // Fetch recently merged PRs (last 5)
    const allClosedPRs: GitHubPR[] = await fetchGitHubAPI(
      `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/pulls?state=closed&per_page=5&sort=updated`
    );
    
    // Fetch PR details with stats for merged PRs
    const mergedPRsWithDetails = await Promise.all(
      allClosedPRs
        .filter(pr => pr.merged_at !== null)
        .slice(0, 5)
        .map(async (pr) => {
          const details = await fetchGitHubAPI(
            `/repos/${GITHUB_OWNER}/${GITHUB_REPO}/pulls/${pr.number}`
          );
          return { ...pr, ...details };
        })
    );

    return NextResponse.json({
      commits: commits.map(commit => ({
        sha: commit.sha.substring(0, 7),
        fullSha: commit.sha,
        message: commit.commit.message.split('\n')[0], // First line only
        fullMessage: commit.commit.message, // Full message for hover
        author: commit.author?.login || commit.commit.author.name,
        avatar: commit.author?.avatar_url,
        date: commit.commit.author.date,
        url: commit.html_url,
      })),
      openPRs: openPRsWithDetails.map(pr => ({
        number: pr.number,
        title: pr.title,
        body: pr.body || '',
        author: pr.user.login,
        avatar: pr.user.avatar_url,
        createdAt: pr.created_at,
        updatedAt: pr.updated_at,
        additions: pr.additions || 0,
        deletions: pr.deletions || 0,
        changedFiles: pr.changed_files || 0,
        url: pr.html_url,
      })),
      mergedPRs: mergedPRsWithDetails.map(pr => ({
        number: pr.number,
        title: pr.title,
        body: pr.body || '',
        author: pr.user.login,
        avatar: pr.user.avatar_url,
        mergedAt: pr.merged_at,
        additions: pr.additions || 0,
        deletions: pr.deletions || 0,
        changedFiles: pr.changed_files || 0,
        url: pr.html_url,
      })),
    });
  } catch (error) {
    console.error('Error fetching GitHub data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch GitHub data' },
      { status: 500 }
    );
  }
}

