-- Row Level Security policies
-- Every row is scoped to auth.uid()

alter table public.telegram_accounts enable row level security;
alter table public.channels          enable row level security;
alter table public.mcqs              enable row level security;
alter table public.user_answers      enable row level security;

-- telegram_accounts
create policy "tg_select_own" on public.telegram_accounts
  for select using (auth.uid() = user_id);
create policy "tg_modify_own" on public.telegram_accounts
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- channels
create policy "ch_select_own" on public.channels
  for select using (auth.uid() = user_id);
create policy "ch_modify_own" on public.channels
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- mcqs
create policy "mcq_select_own" on public.mcqs
  for select using (auth.uid() = user_id);
create policy "mcq_modify_own" on public.mcqs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- user_answers
create policy "ans_select_own" on public.user_answers
  for select using (auth.uid() = user_id);
create policy "ans_modify_own" on public.user_answers
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
