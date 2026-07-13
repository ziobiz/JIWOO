import { NextResponse } from "next/server";
import { getSupabasePublic } from "@/lib/supabase";
import type { PlayResult } from "@/types/game";

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

    const supabase = getSupabasePublic();
    if (!supabase) {
      return NextResponse.json(
        {
          error: "Supabase not configured",
          hint: "Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in .env.local",
        },
        { status: 503 },
      );
    }

    const { data, error } = await supabase
      .from("play_results")
      .insert(row)
      .select("id")
      .single();

    if (error) {
      console.error("[results POST]", error);
      return NextResponse.json({ error: error.message }, { status: 500 });
    }

    return NextResponse.json({ ok: true, id: data?.id });
  } catch (e) {
    console.error(e);
    return NextResponse.json({ error: "Invalid request" }, { status: 400 });
  }
}
