-- 붉은 무공훈장 웹 — Supabase 스키마
-- Supabase 대시보드 → SQL Editor 에 붙여넣고 실행하세요.

create table if not exists public.play_results (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null default '',
  gender text not null default 'g_x',
  grade text not null default 'grade_1',
  major text not null default 'maj_ec',
  mbti text not null default '',
  q1 text check (q1 in ('A', 'B', '')),
  q2 text check (q2 in ('A', 'B', '')),
  q3 text check (q3 in ('A', 'B', '')),
  ending text not null,
  human int not null default 0,
  soldier int not null default 0,
  trust int not null default 0,
  empathy int not null default 0,
  instinct int not null default 0,
  duty int not null default 0,
  guilt int not null default 0,
  courage int not null default 0,
  fragments int not null default 0,
  matches int not null default 0
);

create index if not exists play_results_created_at_idx on public.play_results (created_at desc);
create index if not exists play_results_ending_idx on public.play_results (ending);

alter table public.play_results enable row level security;

-- 누구나 결과 제출 가능 (학생 플레이)
create policy "Anyone can insert play results"
  on public.play_results for insert
  to anon, authenticated
  with check (true);

-- 읽기는 service role(API 서버)만 — anon 직접 조회 차단
-- (관리자 페이지는 /api/analyze 경유)

comment on table public.play_results is '붉은 무공훈장 플레이 결과 — 학술 분석용';

-- 링크 미리보기(오픈그래프) 브랜딩 — 단일 행(id=1)
create table if not exists public.site_branding (
  id int primary key default 1,
  title text,
  description text,
  image_url text,
  updated_at timestamptz not null default now()
);

insert into public.site_branding (id) values (1)
  on conflict (id) do nothing;

alter table public.site_branding enable row level security;

-- 누구나 읽기 가능 (링크 미리보기 메타데이터 생성용)
create policy "Anyone can read branding"
  on public.site_branding for select
  to anon, authenticated
  using (true);

comment on table public.site_branding is '사이트 링크 미리보기(OG) 브랜딩 설정';
