import { NextResponse } from "next/server";
import { getSupabaseAdmin } from "@/lib/supabase";
import { DEFAULT_BRANDING, resolveBranding, siteUrl } from "@/lib/branding";

export const dynamic = "force-dynamic";

function checkAdmin(request: Request): boolean {
  const secret = process.env.ADMIN_SECRET;
  if (!secret) return process.env.NODE_ENV === "development";
  const header = request.headers.get("x-admin-secret");
  const query = new URL(request.url).searchParams.get("secret");
  return header === secret || query === secret;
}

/** 공개 — 현재 브랜딩 + 사이트 주소 + 기본값 */
export async function GET() {
  const b = await resolveBranding();
  return NextResponse.json({ ...b, siteUrl: siteUrl(), defaults: DEFAULT_BRANDING });
}

/** 관리자 — 브랜딩 저장 (단일 행 id=1 upsert) */
export async function PUT(request: Request) {
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
    const body = (await request.json().catch(() => ({}))) as Partial<{
      title: string;
      description: string;
      imageUrl: string;
      credit: string;
      copyright: string;
      notice: string;
      tagline: string;
    }>;

    const row = {
      id: 1,
      title: (body.title ?? "").slice(0, 120),
      description: (body.description ?? "").slice(0, 400),
      image_url: (body.imageUrl ?? "").slice(0, 500),
      credit: (body.credit ?? "").slice(0, 500),
      copyright: (body.copyright ?? "").slice(0, 300),
      notice: (body.notice ?? "").slice(0, 600),
      tagline: (body.tagline ?? "").slice(0, 300),
      updated_at: new Date().toISOString(),
    };

    const { error } = await admin.from("site_branding").upsert(row, { onConflict: "id" });
    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
    return NextResponse.json({ ok: true, branding: await resolveBranding() });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "저장 실패" },
      { status: 500 },
    );
  }
}
