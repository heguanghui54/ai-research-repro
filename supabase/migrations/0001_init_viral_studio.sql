create extension if not exists pgcrypto;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table if not exists public.app_users (
  id text primary key default gen_random_uuid()::text,
  email text not null unique,
  password_hash text not null,
  display_name text not null default '',
  avatar_url text not null default '',
  role text not null default 'member',
  status text not null default 'active',
  plan text not null default 'starter',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.projects (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null references public.app_users(id) on delete cascade,
  name text not null,
  description text not null default '',
  reference_url text not null default '',
  niche text not null default '',
  status text not null default 'active',
  target_platforms jsonb not null default '[]'::jsonb,
  default_avatar_mode text not null default 'cosyvoice',
  default_voice_provider text not null default 'deepseek',
  settings jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.reference_videos (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null references public.app_users(id) on delete cascade,
  project_id text not null references public.projects(id) on delete cascade,
  reference_url text not null,
  source_title text not null default '',
  source_platform text not null default '',
  duration_sec integer not null default 0,
  transcript_text text not null default '',
  transcript_json jsonb not null default '[]'::jsonb,
  hook_summary text not null default '',
  style_notes text not null default '',
  analysis_payload jsonb not null default '{}'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.video_jobs (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null references public.app_users(id) on delete cascade,
  project_id text not null references public.projects(id) on delete cascade,
  reference_id text references public.reference_videos(id) on delete set null,
  status text not null default 'queued',
  topic text not null default '',
  title text not null default '',
  script_text text not null default '',
  script_json jsonb not null default '{}'::jsonb,
  avatar_mode text not null default 'cosyvoice',
  voice_provider text not null default 'deepseek',
  render_ratio text not null default '9:16',
  output_path text not null default '',
  output_url text not null default '',
  thumbnail_url text not null default '',
  error text not null default '',
  progress integer not null default 0,
  pipeline_state jsonb not null default '{}'::jsonb,
  publish_bundle jsonb not null default '{}'::jsonb,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.job_steps (
  id text primary key default gen_random_uuid()::text,
  job_id text not null references public.video_jobs(id) on delete cascade,
  step_key text not null,
  status text not null default 'queued',
  detail jsonb not null default '{}'::jsonb,
  error text not null default '',
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.integrations (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null references public.app_users(id) on delete cascade,
  provider text not null,
  api_key_enc text not null default '',
  base_url text not null default '',
  model text not null default '',
  settings jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.publish_targets (
  id text primary key default gen_random_uuid()::text,
  owner_id text not null references public.app_users(id) on delete cascade,
  project_id text references public.projects(id) on delete cascade,
  platform text not null,
  handle text not null default '',
  publish_mode text not null default 'manual',
  settings jsonb not null default '{}'::jsonb,
  auth_payload jsonb not null default '{}'::jsonb,
  is_enabled boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.publish_jobs (
  id text primary key default gen_random_uuid()::text,
  job_id text not null references public.video_jobs(id) on delete cascade,
  target_id text not null references public.publish_targets(id) on delete cascade,
  status text not null default 'queued',
  remote_id text not null default '',
  remote_url text not null default '',
  error text not null default '',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists set_updated_at_app_users on public.app_users;
create trigger set_updated_at_app_users before update on public.app_users
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_projects on public.projects;
create trigger set_updated_at_projects before update on public.projects
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_reference_videos on public.reference_videos;
create trigger set_updated_at_reference_videos before update on public.reference_videos
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_video_jobs on public.video_jobs;
create trigger set_updated_at_video_jobs before update on public.video_jobs
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_job_steps on public.job_steps;
create trigger set_updated_at_job_steps before update on public.job_steps
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_integrations on public.integrations;
create trigger set_updated_at_integrations before update on public.integrations
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_publish_targets on public.publish_targets;
create trigger set_updated_at_publish_targets before update on public.publish_targets
for each row execute function public.set_updated_at();

drop trigger if exists set_updated_at_publish_jobs on public.publish_jobs;
create trigger set_updated_at_publish_jobs before update on public.publish_jobs
for each row execute function public.set_updated_at();

create index if not exists idx_projects_owner_id on public.projects(owner_id);
create index if not exists idx_reference_videos_owner_id on public.reference_videos(owner_id);
create index if not exists idx_reference_videos_project_id on public.reference_videos(project_id);
create index if not exists idx_video_jobs_owner_id on public.video_jobs(owner_id);
create index if not exists idx_video_jobs_project_id on public.video_jobs(project_id);
create index if not exists idx_job_steps_job_id on public.job_steps(job_id);
create index if not exists idx_integrations_owner_id on public.integrations(owner_id);
create index if not exists idx_publish_targets_owner_id on public.publish_targets(owner_id);
create index if not exists idx_publish_jobs_job_id on public.publish_jobs(job_id);
