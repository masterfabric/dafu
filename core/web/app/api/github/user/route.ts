import { NextRequest, NextResponse } from 'next/server';

const GITHUB_API_BASE = 'https://api.github.com';

async function fetchGitHubAPI(endpoint: string) {
  const headers: HeadersInit = {
    'Accept': 'application/vnd.github.v3+json',
  };

  const response = await fetch(`${GITHUB_API_BASE}${endpoint}`, {
    headers,
    next: { revalidate: 3600 }, // Cache for 1 hour
  });

  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.statusText}`);
  }

  return response.json();
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const username = searchParams.get('username');

  if (!username) {
    return NextResponse.json(
      { error: 'Username parameter is required' },
      { status: 400 }
    );
  }

  try {
    const user = await fetchGitHubAPI(`/users/${username}`);

    return NextResponse.json({
      login: user.login,
      name: user.name || user.login,
      avatar_url: user.avatar_url,
      bio: user.bio || '',
      company: user.company || '',
      location: user.location || '',
      blog: user.blog || '',
      public_repos: user.public_repos || 0,
      followers: user.followers || 0,
      following: user.following || 0,
      html_url: user.html_url,
      created_at: user.created_at,
    });
  } catch (error) {
    console.error('Error fetching GitHub user data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch GitHub user data' },
      { status: 500 }
    );
  }
}

