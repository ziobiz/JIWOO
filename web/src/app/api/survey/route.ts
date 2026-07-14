import { NextResponse } from "next/server";
import { getSupabaseAdmin } from "@/lib/supabase";
import {
  DEFAULT_SURVEY_COPY,
  mergeSurveyCopy,
  resolveSurveyCopy,
  sanitizeSurveyCopy,
  type SurveyCopy,
} from "@/lib/surveyCopy";

export const dynamic = "force-dynamic";

function checkAdmin(request: Request): boolean {
  const secret = process.env.ADMIN_SECRET;
  if (!secret) return process.env.NODE_ENV === "development";
  const header = request.headers.get("x-admin-secret");
  const query = new URL(request.url).searchParams.get("secret");
  return header === secret || query === secret;
}

/** 공개 — 현재 사전 설문 문항 + 기본값 */
export async function GET() {
  const survey = await resolveSurveyCopy();
  return NextResponse.json({
    survey,
    defaults: DEFAULT_SURVEY_COPY,
  });
}

/** 관리자 — 사전 설문 문항 저장 */
export async function PUT(request: Request) {
  try {
    if (!checkAdmin(request)) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    const admin = getSupabaseAdmin();
    if (!admin) {
      return NextResponse.json(
        {
          error: "Supabase 관리자 설정이 필요합니다 (SUPABASE_SERVICE_ROLE_KEY).",
        },
        { status: 503 },
      );
    }

    const body = (await request.json().catch(() => ({}))) as {
      survey?: SurveyCopy;
    };
    const survey = sanitizeSurveyCopy(mergeSurveyCopy(body.survey));

    const { error } = await admin.from("survey_copy").upsert(
      {
        id: 1,
        payload: survey,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "id" },
    );
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json({ ok: true, survey: await resolveSurveyCopy() });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "저장 실패" },
      { status: 500 },
    );
  }
}
