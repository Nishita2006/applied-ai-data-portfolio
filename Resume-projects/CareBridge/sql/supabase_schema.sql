-- Run this file once in the Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  first_name text,
  active_visit_id uuid,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.visits (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  appointment_date date not null, appointment_time time not null, provider text not null, specialty text not null,
  reason text not null, location text, notes text, brief_confirmed boolean not null default false,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
alter table public.profiles drop constraint if exists profiles_active_visit_id_fkey;
alter table public.profiles add constraint profiles_active_visit_id_fkey foreign key(active_visit_id) references public.visits(id) on delete set null;
create table if not exists public.readiness_tasks (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, title text not null, completed boolean not null default false,
  notes text not null default '', position integer not null, unique(visit_id,title)
);
create table if not exists public.symptoms (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, name text not null, onset text, severity integer,
  frequency text, pattern text, triggers text, relief text, description text, created_at timestamptz not null default now(),
  constraint symptom_severity check(severity is null or severity between 0 and 10)
);
create table if not exists public.medications (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, name text not null, dose text, frequency text, notes text,
  created_at timestamptz not null default now()
);
create table if not exists public.allergies (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, allergy text not null, reaction text, notes text,
  created_at timestamptz not null default now()
);
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, title text not null, filename text, mime_type text,
  storage_path text, suggested_category text, confidence double precision, category text,
  category_confirmed boolean not null default false, extraction_status text not null default 'ready', created_at timestamptz not null default now()
);
create table if not exists public.document_text (
  document_id uuid primary key references public.documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade, visit_id uuid not null references public.visits(id) on delete cascade,
  extracted_text text not null, created_at timestamptz not null default now()
);
create table if not exists public.provider_questions (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null references public.visits(id) on delete cascade, question text not null,
  priority boolean not null default false, position integer not null default 0, created_at timestamptz not null default now()
);
create table if not exists public.visit_briefs (
  id uuid primary key default gen_random_uuid(), user_id uuid not null references auth.users(id) on delete cascade,
  visit_id uuid not null unique references public.visits(id) on delete cascade, confirmed boolean not null default false,
  confirmed_at timestamptz, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);

create or replace function public.handle_new_user() returns trigger language plpgsql security definer set search_path='' as $$
begin
  insert into public.profiles(user_id,first_name) values(new.id,new.raw_user_meta_data->>'first_name') on conflict(user_id) do nothing;
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users for each row execute procedure public.handle_new_user();

create index if not exists visits_user_id_idx on public.visits(user_id);
create index if not exists readiness_owner_idx on public.readiness_tasks(user_id,visit_id);
create index if not exists symptoms_owner_idx on public.symptoms(user_id,visit_id);
create index if not exists medications_owner_idx on public.medications(user_id,visit_id);
create index if not exists allergies_owner_idx on public.allergies(user_id,visit_id);
create index if not exists documents_owner_idx on public.documents(user_id,visit_id);
create index if not exists document_text_owner_idx on public.document_text(user_id,visit_id);
create index if not exists questions_owner_idx on public.provider_questions(user_id,visit_id);
create index if not exists briefs_owner_idx on public.visit_briefs(user_id,visit_id);

alter table public.profiles enable row level security;
alter table public.visits enable row level security;
alter table public.readiness_tasks enable row level security;
alter table public.symptoms enable row level security;
alter table public.medications enable row level security;
alter table public.allergies enable row level security;
alter table public.documents enable row level security;
alter table public.document_text enable row level security;
alter table public.provider_questions enable row level security;
alter table public.visit_briefs enable row level security;

revoke all on table public.profiles,public.visits,public.readiness_tasks,public.symptoms,public.medications,public.allergies,public.documents,public.document_text,public.provider_questions,public.visit_briefs from anon;
grant select,insert,update,delete on table public.profiles,public.visits,public.readiness_tasks,public.symptoms,public.medications,public.allergies,public.documents,public.document_text,public.provider_questions,public.visit_briefs to authenticated;

create or replace function public.owns_visit(target_visit uuid) returns boolean language sql stable security definer set search_path='' as $$
  select exists(select 1 from public.visits where id=target_visit and user_id=(select auth.uid()));
$$;

drop policy if exists "profiles_select_own" on public.profiles;
drop policy if exists "profiles_insert_own" on public.profiles;
drop policy if exists "profiles_update_own" on public.profiles;
drop policy if exists "profiles_delete_own" on public.profiles;
create policy "profiles_select_own" on public.profiles for select to authenticated using ((select auth.uid())=user_id);
create policy "profiles_insert_own" on public.profiles for insert to authenticated with check ((select auth.uid())=user_id and (active_visit_id is null or public.owns_visit(active_visit_id)));
create policy "profiles_update_own" on public.profiles for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id and (active_visit_id is null or public.owns_visit(active_visit_id)));
create policy "profiles_delete_own" on public.profiles for delete to authenticated using ((select auth.uid())=user_id);

drop policy if exists "visits_select_own" on public.visits;
drop policy if exists "visits_insert_own" on public.visits;
drop policy if exists "visits_update_own" on public.visits;
drop policy if exists "visits_delete_own" on public.visits;
create policy "visits_select_own" on public.visits for select to authenticated using ((select auth.uid())=user_id);
create policy "visits_insert_own" on public.visits for insert to authenticated with check ((select auth.uid())=user_id);
create policy "visits_update_own" on public.visits for update to authenticated using ((select auth.uid())=user_id) with check ((select auth.uid())=user_id);
create policy "visits_delete_own" on public.visits for delete to authenticated using ((select auth.uid())=user_id);

-- Child policies require both the direct owner and an owned parent visit.
do $$ declare t text; begin
  foreach t in array array['readiness_tasks','symptoms','medications','allergies','documents','document_text','provider_questions','visit_briefs'] loop
    execute format('drop policy if exists %I on public.%I',t||'_select_own',t);
    execute format('drop policy if exists %I on public.%I',t||'_insert_own',t);
    execute format('drop policy if exists %I on public.%I',t||'_update_own',t);
    execute format('drop policy if exists %I on public.%I',t||'_delete_own',t);
    execute format('create policy %I on public.%I for select to authenticated using ((select auth.uid())=user_id and public.owns_visit(visit_id))',t||'_select_own',t);
    execute format('create policy %I on public.%I for insert to authenticated with check ((select auth.uid())=user_id and public.owns_visit(visit_id))',t||'_insert_own',t);
    execute format('create policy %I on public.%I for update to authenticated using ((select auth.uid())=user_id and public.owns_visit(visit_id)) with check ((select auth.uid())=user_id and public.owns_visit(visit_id))',t||'_update_own',t);
    execute format('create policy %I on public.%I for delete to authenticated using ((select auth.uid())=user_id and public.owns_visit(visit_id))',t||'_delete_own',t);
  end loop;
end $$;

insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types)
values('carebridge-records','carebridge-records',false,10485760,array['application/pdf','text/plain'])
on conflict(id) do update set public=false,file_size_limit=10485760,allowed_mime_types=array['application/pdf','text/plain'];
drop policy if exists "records_storage_select_own" on storage.objects;
drop policy if exists "records_storage_insert_own" on storage.objects;
drop policy if exists "records_storage_delete_own" on storage.objects;
create policy "records_storage_select_own" on storage.objects for select to authenticated using(bucket_id='carebridge-records' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy "records_storage_insert_own" on storage.objects for insert to authenticated with check(bucket_id='carebridge-records' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy "records_storage_delete_own" on storage.objects for delete to authenticated using(bucket_id='carebridge-records' and (storage.foldername(name))[1]=(select auth.uid())::text);
