import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { PlayResult } from "@/types/game";

let _admin: SupabaseClient | null = null;
let _public: SupabaseClient | null = null;
let _configError: string | null = null;

/** 설정된 Supabase URL/키 문제 메시지 (관리자 화면에 표시용) */
export function getSupabaseConfigError(): string | null {
  return _configError;
}

/**
 * NEXT_PUBLIC_SUPABASE_URL 정규화
 * - 공백/따옴표 제거
 * - https:// 누락 시 자동 보정
 * - http(s) URL 이 아니면 null
 */
export function normalizeSupabaseUrl(raw: string | undefined | null): string | null {
  if (raw == null) return null;
  let u = String(raw).trim();
  if (!u) return null;
  // .env 에 따옴표가 포함된 경우
  if (
    (u.startsWith('"') && u.endsWith('"')) ||
    (u.startsWith("'") && u.endsWith("'"))
  ) {
    u = u.slice(1, -1).trim();
  }
  if (!u) return null;
  // https 누락 (예: xxxx.supabase.co)
  if (!/^https?:\/\//i.test(u)) {
    u = `https://${u}`;
  }
  try {
    const parsed = new URL(u);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") return null;
    if (!parsed.hostname) return null;
    return parsed.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
}

function readUrlAndKey(
  keyEnv: "SUPABASE_SERVICE_ROLE_KEY" | "NEXT_PUBLIC_SUPABASE_ANON_KEY",
): { url: string; key: string } | null {
  const rawUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const rawKey = process.env[keyEnv];
  const url = normalizeSupabaseUrl(rawUrl);
  const key = (rawKey ?? "").trim().replace(/^["']|["']$/g, "");

  if (!rawUrl?.trim() && !rawKey?.trim()) {
    _configError = null; // 완전 미설정 — 일반 폴백
    return null;
  }
  if (!url) {
    _configError =
      "NEXT_PUBLIC_SUPABASE_URL 이 비어 있거나 올바른 http(s) 주소가 아닙니다. Vercel → Settings → Environment Variables 에서 https://xxxx.supabase.co 형식으로 다시 저장하세요.";
    return null;
  }
  if (!key) {
    _configError = `${keyEnv} 값이 비어 있습니다. Vercel 환경변수에 키를 다시 입력하세요.`;
    return null;
  }
  _configError = null;
  return { url, key };
}

/** 서버 전용 — service role (관리자 API) */
export function getSupabaseAdmin(): SupabaseClient | null {
  try {
    const cfg = readUrlAndKey("SUPABASE_SERVICE_ROLE_KEY");
    if (!cfg) return null;
    if (!_admin) _admin = createClient(cfg.url, cfg.key);
    return _admin;
  } catch (e) {
    _configError = `Supabase Admin 초기화 실패: ${
      e instanceof Error ? e.message : String(e)
    }`;
    _admin = null;
    return null;
  }
}

/** 클라이언트/서버 공용 — anon key (결과 제출) */
export function getSupabasePublic(): SupabaseClient | null {
  try {
    const cfg = readUrlAndKey("NEXT_PUBLIC_SUPABASE_ANON_KEY");
    if (!cfg) return null;
    if (!_public) _public = createClient(cfg.url, cfg.key);
    return _public;
  } catch (e) {
    _configError = `Supabase Public 초기화 실패: ${
      e instanceof Error ? e.message : String(e)
    }`;
    _public = null;
    return null;
  }
}

export function isSupabaseConfigured(): boolean {
  return Boolean(
    normalizeSupabaseUrl(process.env.NEXT_PUBLIC_SUPABASE_URL) &&
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.trim(),
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
