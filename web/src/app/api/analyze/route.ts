import { NextResponse } from "next/server";
import { buildReport } from "@/lib/analyze";
import { getSupabaseAdmin, getSupabaseConfigError, getSupabaseEnvStatus, rowToPlayResult } from "@/lib/supabase";
import type { PlayResult } from "@/types/game";
import fs from "fs";
import path from "path";

function checkAdmin(request: Request): boolean {
  const secret = process.env.ADMIN_SECRET;
  if (!secret) return process.env.NODE_ENV === "development";
  const header = request.headers.get("x-admin-secret");
  const url = new URL(request.url);
  const query = url.searchParams.get("secret");
  return header === secret || query === secret;
}

/** 로컬 개발: pygame results.csv 폴백 */
function loadLocalCsv(): PlayResult[] {
  const csvPath = path.join(
    process.cwd(),
    "..",
    "붉은무공훈장",
    "results.csv",
  );
  if (!fs.existsSync(csvPath)) return [];
  const text = fs.readFileSync(csvPath, "utf-8");
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const vals = line.split(",");
    const row: Record<string, string> = {};
    headers.forEach((h, i) => {
      row[h.trim()] = vals[i]?.trim() ?? "";
    });
    return rowToPlayResult({
      ...row,
      human: Number(row.human),
      soldier: Number(row.soldier),
      trust: Number(row.trust),
      empathy: Number(row.empathy),
      instinct: Number(row.instinct),
      duty: Number(row.duty),
      guilt: Number(row.guilt),
      courage: Number(row.courage),
      fragments: Number(row.fragments),
      matches: Number(row.matches),
    });
  });
}

export async function GET(request: Request) {
  try {
    if (!checkAdmin(request)) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    let rows: PlayResult[] = [];
    let source = "Supabase play_results";

    // 데이터 소스 오류(테이블 부재·키 오류 등)로 로그인을 막지 않는다.
    // 오류가 나도 관리자는 (빈) 대시보드에 진입하고, 원인은 source에 표시된다.
    try {
      const admin = getSupabaseAdmin();
      const cfgErr = getSupabaseConfigError();
      if (admin) {
        const { data, error } = await admin
          .from("play_results")
          .select("*")
          .order("created_at", { ascending: false });
        if (error) {
          source = `Supabase 오류: ${error.message} (schema.sql로 play_results 테이블을 생성했는지 확인하세요)`;
        } else {
          rows = (data ?? []).map((r) => rowToPlayResult(r));
        }
      } else if (cfgErr) {
        rows = loadLocalCsv();
        source = rows.length
          ? `local results.csv · (경고) ${cfgErr}`
          : cfgErr;
      } else {
        rows = loadLocalCsv();
        source = rows.length
          ? "local results.csv (dev fallback)"
          : "데이터 없음 · Supabase 미설정(환경변수 NEXT_PUBLIC_SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY)";
      }
    } catch (srcErr) {
      source = `데이터 소스 연결 오류: ${
        srcErr instanceof Error ? srcErr.message : String(srcErr)
      }`;
    }

    const report = buildReport(rows, source);
    const envStatus = getSupabaseEnvStatus();
    return NextResponse.json({
      ...report,
      envStatus,
      // 전체 원자료 — 클라이언트에서 학년/성별/전공/MBTI 교차분석 및 내보내기에 사용
      rows,
      recentPlays: rows.slice(0, 100).map((r) => ({
        name: r.name,
        gender: r.gender,
        grade: r.grade,
        mbti: r.mbti,
        ending: r.ending,
        human: r.human,
        soldier: r.soldier,
        courage: r.courage,
        empathy: r.empathy,
        fragments: r.fragments,
        matches: r.matches,
        created_at: r.created_at,
      })),
    });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "서버 오류" },
      { status: 500 },
    );
  }
}
