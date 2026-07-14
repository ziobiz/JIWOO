import { NextResponse } from "next/server";
import { getSupabasePublic, getSupabaseAdmin } from "@/lib/supabase";
import type { PlayResult } from "@/types/game";

function checkAdmin(request: Request): boolean {
  const secret = process.env.ADMIN_SECRET;
  if (!secret) return process.env.NODE_ENV === "development";
  const header = request.headers.get("x-admin-secret");
  const url = new URL(request.url);
  const query = url.searchParams.get("secret");
  return header === secret || query === secret;
}

export async function POST(request: Request) {
  try {
    const body = (await request.json()) as Partial<PlayResult>;
    if (!body.ending || !body.name) {
      return NextResponse.json(
        { error: "ending and name are required" },
        { status: 400 },
      );
    }

    const row = {
      name: body.name.slice(0, 20),
      gender: body.gender ?? "g_x",
      grade: body.grade ?? "grade_1",
      major: body.major ?? "maj_ec",
      mbti: (body.mbti ?? "").slice(0, 4),
      q1: body.q1 ?? "",
      q2: body.q2 ?? "",
      q3: body.q3 ?? "",
      ending: body.ending,
      human: body.human ?? 0,
      soldier: body.soldier ?? 0,
      trust: body.trust ?? 0,
      empathy: body.empathy ?? 0,
      instinct: body.instinct ?? 0,
      duty: body.duty ?? 0,
      guilt: body.guilt ?? 0,
      courage: body.courage ?? 0,
      fragments: body.fragments ?? 0,
      matches: body.matches ?? 0,
    };

    // 서버 API — service role 로 저장 (anon 은 INSERT 후 SELECT RLS 에 막힘)
    const supabase = getSupabaseAdmin() ?? getSupabasePublic();
    if (!supabase) {
      return NextResponse.json(
        {
          error: "Supabase not configured",
          hint: "Set NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY in Vercel env",
        },
        { status: 503 },
      );
    }

    const { data, error } = await supabase
      .from("play_results")
      .insert(row)
      .select("id")
      .maybeSingle();

    if (error) {
      console.error("[results POST]", error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ ok: true, id: data?.id ?? null });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}

/** 관리자 전용 — 수집 데이터 삭제 (테스트 데이터 정리용)
 *  body: { all: true }  또는  { ids: string[] } */
export async function DELETE(request: Request) {
  try {
    if (!checkAdmin(request)) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    const admin = getSupabaseAdmin();
    if (!admin) {
      return NextResponse.json(
        { error: "Supabase 관리자 설정이 필요합니다 (SUPABASE_SERVICE_ROLE_KEY)." },
        { status: 503 },
      );
    }

    const body = (await request.json().catch(() => ({}))) as {
      all?: boolean;
      ids?: string[];
    };

    if (body.all) {
      // 전체 삭제 — 항상 참인 조건으로 모든 행 제거
      const { error, count } = await admin
        .from("play_results")
        .delete({ count: "exact" })
        .not("id", "is", null);
      if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
      }
      return NextResponse.json({ ok: true, deleted: count ?? 0 });
    }

    if (Array.isArray(body.ids) && body.ids.length > 0) {
      const { error, count } = await admin
        .from("play_results")
        .delete({ count: "exact" })
        .in("id", body.ids);
      if (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
      }
      return NextResponse.json({ ok: true, deleted: count ?? 0 });
    }

    return NextResponse.json(
      { error: "삭제할 대상이 없습니다 (all 또는 ids 필요)." },
      { status: 400 },
    );
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "삭제 실패" },
      { status: 500 },
    );
  }
}
