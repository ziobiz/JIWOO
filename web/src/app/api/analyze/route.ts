import { NextResponse } from "next/server";
import { buildReport } from "@/lib/analyze";
import { getSupabaseAdmin, rowToPlayResult } from "@/lib/supabase";
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
  if (!checkAdmin(request)) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  let rows: PlayResult[] = [];
  let source = "Supabase play_results";

  const admin = getSupabaseAdmin();
  if (admin) {
    const { data, error } = await admin
      .from("play_results")
      .select("*")
      .order("created_at", { ascending: false });
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    rows = (data ?? []).map((r) => rowToPlayResult(r));
  } else {
    rows = loadLocalCsv();
    source = "local results.csv (dev fallback)";
  }

  const report = buildReport(rows, source);
  return NextResponse.json({
    ...report,
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
}
