-- TeleMCQ initial schema
-- Run in Supabase SQL editor (or via `supabase db push`)

create extension if not exists "pgcrypto";

-- Telegram account per user (1:1)
create table if not exists public.telegram_accounts (
  user_id uuid primary key references auth.users(id) on delete cascade,
  phone text not null,
  session_encrypted text not null,
  connected_at timestamptz not null default now()
);

-- Selected channel per user (1:1 in v1)
create table if not exists public.channels (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  tg_channel_id bigint not null,
  tg_access_hash bigint,
  title text not null,
  last_scraped_msg_id bigint not null default 0,
  last_synced_at timestamptz,
  created_at timestamptz not null default now()
);

-- MCQs scraped from a channel
create table if not exists public.mcqs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  channel_id uuid not null references public.channels(id) on delete cascade,
  tg_msg_id bigint not null,
  category text,
  question text not null,
  options jsonb not null,
  correct_answer text,
  source_date timestamptz not null,
  created_at timestamptz not null default now(),
  search_tsv tsvector generated always as (
    to_tsvector('english', coalesce(category,'') || ' ' || question || ' ' || coalesce(options::text,''))
  ) stored,
  unique (channel_id, tg_msg_id)
);

create index if not exists idx_mcqs_user on public.mcqs (user_id, source_date desc);
create index if not exists idx_mcqs_search on public.mcqs using gin (search_tsv);

-- Answers persisted per user
create table if not exists public.user_answers (
  user_id uuid not null references auth.users(id) on delete cascade,
  mcq_id uuid not null references public.mcqs(id) on delete cascade,
  selected_answer text not null,
  answered_at timestamptz not null default now(),
  primary key (user_id, mcq_id)
);
