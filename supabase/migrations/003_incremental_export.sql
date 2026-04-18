-- Track the last time each user's channel was exported to DOCX,
-- so subsequent exports only include MCQs scraped after that point.

alter table public.channels
  add column if not exists last_exported_at timestamptz;
