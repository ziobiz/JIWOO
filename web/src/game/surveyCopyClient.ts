/**
 * 클라이언트 — 사전 설문 문항 오버라이드 (관리자 저장분)
 */
import type { Lang } from "./gameData";
import { ui } from "./gameData";
import {
  surveyUiKey,
  type SurveyDim,
} from "./surveyVariants";
import type { SurveyCopy } from "@/lib/surveyCopy";

let cached: SurveyCopy | null = null;
let loading: Promise<SurveyCopy | null> | null = null;

export async function loadSurveyCopyClient(): Promise<SurveyCopy | null> {
  if (cached) return cached;
  if (loading) return loading;
  loading = (async () => {
    try {
      const res = await fetch("/api/survey", { cache: "no-store" });
      if (!res.ok) return null;
      const j = (await res.json()) as { survey?: SurveyCopy };
      cached = j.survey ?? null;
      return cached;
    } catch {
      return null;
    } finally {
      loading = null;
    }
  })();
  return loading;
}

export function invalidateSurveyCopyCache() {
  cached = null;
}

/** 설문 표시용 — 오버라이드 있으면 우선, 없으면 i18n */
export function surveyDisplay(
  copy: SurveyCopy | null,
  dim: SurveyDim,
  variant: number,
  part: "t" | "a" | "b",
  lang: Lang,
): string {
  if (copy) {
    const v = Math.max(1, Math.min(5, variant));
    const entry = copy[dim]?.[v - 1];
    const s = entry?.[part]?.[lang] || entry?.[part]?.KR;
    if (s?.trim()) return s;
  }
  return ui(surveyUiKey(dim, variant, part), lang);
}
