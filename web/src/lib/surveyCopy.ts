import { GAME, type Lang } from "@/game/gameData";
import {
  SURVEY_DIMS,
  SURVEY_VARIANT_COUNT,
  surveyUiKey,
  type SurveyDim,
} from "@/game/surveyVariants";
import { getSupabaseAdmin, getSupabasePublic } from "./supabase";

export type LangMap = Record<Lang, string>;

export interface SurveyVariant {
  t: LangMap;
  a: LangMap;
  b: LangMap;
}

/** q1/q2/q3 각각 변종 5개 */
export type SurveyCopy = Record<SurveyDim, SurveyVariant[]>;

const LANGS: Lang[] = ["KR", "EN", "CH", "JP"];

function emptyLang(): LangMap {
  return { KR: "", EN: "", CH: "", JP: "" };
}

function fromUiKey(key: string): LangMap {
  const d = GAME.i18n.UI[key] ?? {};
  return {
    KR: d.KR ?? "",
    EN: d.EN ?? d.KR ?? "",
    CH: d.CH ?? d.KR ?? "",
    JP: d.JP ?? d.KR ?? "",
  };
}

/** game-data.json 기본 문항 (빌드 시점 고정) */
export function buildDefaultSurveyCopy(): SurveyCopy {
  const out = {} as SurveyCopy;
  for (const dim of SURVEY_DIMS) {
    out[dim] = [];
    for (let v = 1; v <= SURVEY_VARIANT_COUNT; v++) {
      out[dim].push({
        t: fromUiKey(surveyUiKey(dim, v, "t")),
        a: fromUiKey(surveyUiKey(dim, v, "a")),
        b: fromUiKey(surveyUiKey(dim, v, "b")),
      });
    }
  }
  return out;
}

export const DEFAULT_SURVEY_COPY: SurveyCopy = buildDefaultSurveyCopy();

export const SURVEY_DIM_LABEL: Record<SurveyDim, string> = {
  q1: "유형 1 · 원칙 vs 공감",
  q2: "유형 2 · 진실·용기 vs 명예",
  q3: "유형 3 · 개인 안위 vs 이타심",
};

function normalizeVariant(raw: unknown, fallback: SurveyVariant): SurveyVariant {
  const r = (raw ?? {}) as Partial<SurveyVariant>;
  const pick = (part: "t" | "a" | "b"): LangMap => {
    const src = (r[part] ?? {}) as Partial<LangMap>;
    const fb = fallback[part];
    const out = emptyLang();
    for (const lang of LANGS) {
      const v = typeof src[lang] === "string" ? src[lang]!.trim() : "";
      out[lang] = v || fb[lang] || "";
    }
    return out;
  };
  return { t: pick("t"), a: pick("a"), b: pick("b") };
}

/** DB payload 와 기본값을 병합 (항상 3×5 구조 보장) */
export function mergeSurveyCopy(raw: unknown): SurveyCopy {
  const base = buildDefaultSurveyCopy();
  if (!raw || typeof raw !== "object") return base;
  const src = raw as Partial<Record<SurveyDim, unknown>>;
  const out = {} as SurveyCopy;
  for (const dim of SURVEY_DIMS) {
    const arr = Array.isArray(src[dim]) ? (src[dim] as unknown[]) : [];
    out[dim] = base[dim].map((fb, i) => normalizeVariant(arr[i], fb));
  }
  return out;
}

export async function resolveSurveyCopy(): Promise<SurveyCopy> {
  try {
    const sb = getSupabaseAdmin() ?? getSupabasePublic();
    if (!sb) return buildDefaultSurveyCopy();
    const { data, error } = await sb
      .from("survey_copy")
      .select("payload")
      .eq("id", 1)
      .maybeSingle();
    if (error || !data) return buildDefaultSurveyCopy();
    return mergeSurveyCopy(data.payload);
  } catch {
    return buildDefaultSurveyCopy();
  }
}

/** 저장용 — 과한 길이 자르기 */
export function sanitizeSurveyCopy(input: SurveyCopy): SurveyCopy {
  const clip = (s: string, n: number) => s.slice(0, n);
  const out = {} as SurveyCopy;
  for (const dim of SURVEY_DIMS) {
    const list = Array.isArray(input[dim]) ? input[dim] : [];
    out[dim] = [];
    for (let i = 0; i < SURVEY_VARIANT_COUNT; i++) {
      const v = normalizeVariant(list[i], DEFAULT_SURVEY_COPY[dim][i]);
      out[dim].push({
        t: {
          KR: clip(v.t.KR, 600),
          EN: clip(v.t.EN, 600),
          CH: clip(v.t.CH, 600),
          JP: clip(v.t.JP, 600),
        },
        a: {
          KR: clip(v.a.KR, 300),
          EN: clip(v.a.EN, 300),
          CH: clip(v.a.CH, 300),
          JP: clip(v.a.JP, 300),
        },
        b: {
          KR: clip(v.b.KR, 300),
          EN: clip(v.b.EN, 300),
          CH: clip(v.b.CH, 300),
          JP: clip(v.b.JP, 300),
        },
      });
    }
  }
  return out;
}

export function surveyText(
  copy: SurveyCopy,
  dim: SurveyDim,
  variant: number,
  part: "t" | "a" | "b",
  lang: Lang,
): string {
  const v = Math.max(1, Math.min(SURVEY_VARIANT_COUNT, variant));
  const entry = copy[dim][v - 1];
  return entry[part][lang] || entry[part].KR || "";
}
