import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { PlayResult } from "@/types/game";

let _admin: SupabaseClient | null = null;
let _public: SupabaseClient | null = null;

/** 서버 전용 — service role (관리자 API) */
export function getSupabaseAdmin(): SupabaseClient | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return null;
  if (!_admin) _admin = createClient(url, key);
  return _admin;
}

/** 클라이언트/서버 공용 — anon key (결과 제출) */
export function getSupabasePublic(): SupabaseClient | null {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  if (!_public) _public = createClient(url, key);
  return _public;
}

export function isSupabaseConfigured(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL &&
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  );
}

/** DB row → PlayResult */
export function rowToPlayResult(row: Record<string, unknown>): PlayResult {
  return {
    id: String(row.id ?? ""),
    created_at: String(row.created_at ?? ""),
    name: String(row.name ?? ""),
    gender: row.gender as PlayResult["gender"],
    grade: row.grade as PlayResult["grade"],
    major: row.major as PlayResult["major"],
    mbti: String(row.mbti ?? ""),
    q1: (row.q1 as PlayResult["q1"]) ?? "",
    q2: (row.q2 as PlayResult["q2"]) ?? "",
    q3: (row.q3 as PlayResult["q3"]) ?? "",
    ending: row.ending as PlayResult["ending"],
    human: Number(row.human ?? 0),
    soldier: Number(row.soldier ?? 0),
    trust: Number(row.trust ?? 0),
    empathy: Number(row.empathy ?? 0),
    instinct: Number(row.instinct ?? 0),
    duty: Number(row.duty ?? 0),
    guilt: Number(row.guilt ?? 0),
    courage: Number(row.courage ?? 0),
    fragments: Number(row.fragments ?? 0),
    matches: Number(row.matches ?? 0),
  };
}
