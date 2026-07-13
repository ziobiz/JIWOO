import { REFERENCE } from "./references";
import type { AnalysisReport, PlayResult } from "@/types/game";

const ENDING_ORDER = ["TRUE", "GOOD", "NORMAL", "BAD", "HIDDEN"] as const;
const GOOD_ENDINGS = new Set(["TRUE", "GOOD", "HIDDEN"]);

function pct(n: number, d: number): number {
  return d ? Math.round((100 * n) / d * 10) / 10 : 0;
}

function isThinking(mbti: string): boolean {
  return mbti.length >= 3 && mbti[2].toUpperCase() === "T";
}

function isFeeling(mbti: string): boolean {
  return mbti.length >= 3 && mbti[2].toUpperCase() === "F";
}

export function analyzeResults(rows: PlayResult[]): AnalysisReport["data"] {
  const n = rows.length;

  const q1 = rows.filter((r) => r.q1 === "A" || r.q1 === "B");
  const q1a = q1.filter((r) => r.q1 === "A").length;
  const male = q1.filter((r) => r.gender === "g_m");
  const female = q1.filter((r) => r.gender === "g_f");

  const model1 = {
    n: q1.length,
    principlePct: pct(q1a, q1.length),
    empathyPct: pct(q1.length - q1a, q1.length),
    malePrinciplePct: pct(
      male.filter((r) => r.q1 === "A").length,
      male.length,
    ),
    femalePrinciplePct: pct(
      female.filter((r) => r.q1 === "A").length,
      female.length,
    ),
    maleN: male.length,
    femaleN: female.length,
    avgHuman: n
      ? Math.round((rows.reduce((s, r) => s + r.human, 0) / n) * 10) / 10
      : 0,
    avgSoldier: n
      ? Math.round((rows.reduce((s, r) => s + r.soldier, 0) / n) * 10) / 10
      : 0,
  };

  const tRows = rows.filter((r) => isThinking(r.mbti));
  const fRows = rows.filter((r) => isFeeling(r.mbti));
  const model2 = {
    tN: tRows.length,
    fN: fRows.length,
    tGoodEndingPct: pct(
      tRows.filter((r) => GOOD_ENDINGS.has(r.ending)).length,
      tRows.length,
    ),
    fGoodEndingPct: pct(
      fRows.filter((r) => GOOD_ENDINGS.has(r.ending)).length,
      fRows.length,
    ),
    tAvgCourage: tRows.length
      ? Math.round(
          (tRows.reduce((s, r) => s + r.courage, 0) / tRows.length) * 10,
        ) / 10
      : 0,
    fAvgCourage: fRows.length
      ? Math.round(
          (fRows.reduce((s, r) => s + r.courage, 0) / fRows.length) * 10,
        ) / 10
      : 0,
  };

  const q3 = rows.filter((r) => r.q3 === "A" || r.q3 === "B");
  const q3a = q3.filter((r) => r.q3 === "A").length;
  const model3 = {
    n: q3.length,
    selfPct: pct(q3a, q3.length),
    altruismPct: pct(q3.length - q3a, q3.length),
    avgInstinct: n
      ? Math.round((rows.reduce((s, r) => s + r.instinct, 0) / n) * 10) / 10
      : 0,
    avgEmpathy: n
      ? Math.round((rows.reduce((s, r) => s + r.empathy, 0) / n) * 10) / 10
      : 0,
    avgFragments: n
      ? Math.round((rows.reduce((s, r) => s + r.fragments, 0) / n) * 10) / 10
      : 0,
  };

  const counts = new Map<string, number>();
  for (const r of rows) counts.set(r.ending, (counts.get(r.ending) ?? 0) + 1);

  const endingDistribution: { code: string; count: number; pct: number }[] =
    ENDING_ORDER.filter((c) => counts.has(c)).map((code) => ({
      code,
      count: counts.get(code) ?? 0,
      pct: pct(counts.get(code) ?? 0, n),
    }));
  for (const [code, count] of counts) {
    if (!ENDING_ORDER.includes(code as (typeof ENDING_ORDER)[number])) {
      endingDistribution.push({ code, count, pct: pct(count, n) });
    }
  }

  const goodEndingPct = pct(
    rows.filter((r) => GOOD_ENDINGS.has(r.ending)).length,
    n,
  );

  return { endingDistribution, goodEndingPct, model1, model2, model3 };
}

export function buildReport(
  rows: PlayResult[],
  source = "Supabase play_results",
): AnalysisReport {
  return {
    generatedAt: new Date().toISOString(),
    source,
    sampleSize: rows.length,
    reference: REFERENCE,
    data: analyzeResults(rows),
  };
}
