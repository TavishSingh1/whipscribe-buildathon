create table users (
  id uuid primary key,
  email text not null unique,
  password_hash text not null,
  is_demo boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table creator_profiles (
  id uuid primary key,
  user_id uuid not null unique references users(id) on delete cascade,
  podcast_name text not null,
  description text not null default '',
  niche text not null default '',
  target_audience text not null default '',
  audience_level text not null default '',
  brand_voice text not null default '',
  tone text not null default '',
  communication_style text not null default '',
  content_goals text not null default '',
  preferred_platforms jsonb not null default '[]',
  clip_style text not null default '',
  preferred_topics jsonb not null default '[]',
  excluded_topics jsonb not null default '[]',
  cta_style text not null default '',
  language text not null default 'English',
  website text,
  social_handles jsonb not null default '{}',
  brand_guidelines text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table content_examples (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  platform text not null,
  title text not null,
  content text not null,
  source text not null default 'manual',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table connected_accounts (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  provider text not null,
  account_name text not null,
  access_token_encrypted text,
  refresh_token_encrypted text,
  metadata_json jsonb not null default '{}',
  scopes jsonb not null default '[]',
  status text not null default 'connected',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table episodes (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  file_name text not null,
  file_type text not null,
  duration double precision,
  storage_url text not null,
  status text not null default 'uploaded',
  transcript jsonb,
  title text,
  description text,
  guest text,
  topic text,
  additional_instructions text,
  clip_goal text not null default 'Balanced',
  social_goal text not null default 'Engagement',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table processing_jobs (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  episode_id uuid not null references episodes(id) on delete cascade,
  current_step text not null default 'queued',
  progress integer not null default 0,
  error_message text,
  started_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table clips (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  episode_id uuid not null references episodes(id) on delete cascade,
  title text not null,
  start_time double precision not null,
  end_time double precision not null,
  video_url text,
  score_reason text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table show_notes (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  episode_id uuid not null references episodes(id) on delete cascade,
  summary text not null,
  chapters jsonb not null default '[]',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table social_posts (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  episode_id uuid not null references episodes(id) on delete cascade,
  platform text not null,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table usage_records (
  id uuid primary key,
  user_id uuid not null references users(id) on delete cascade,
  episode_id uuid references episodes(id) on delete set null,
  processing_minutes double precision not null default 0,
  llm_tokens_estimated integer not null default 0,
  clips_generated integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
