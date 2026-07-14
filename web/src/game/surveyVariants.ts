/**
 * 성향 설문 변종 선택
 * ─────────────────
 * 유형 3종(q1·q2·q3) × 변종 5개. 결과는 항상 A/B로만 저장(분석 호환).
 * 본 문항 추적은 브라우저 localStorage (기기별). IP/MAC 미사용
 * → 같은 Wi‑Fi의 다른 사람도 각자 다른 문항을 받는다.
 */

export const SURVEY_DIMS = ["q1", "q2", "q3"] as const;
export type SurveyDim = (typeof SURVEY_DIMS)[number];
export const SURVEY_VARIANT_COUNT = 5;

export type SurveyVariantPick = Record<SurveyDim, number>;

const SEEN_KEY = "twc.surveySeen";

type SeenMap = Partial<Record<SurveyDim, number[]>>;

function readSeen(): SeenMap {
  if (typeof window === "undefined") return {};
  try {
    const raw = localStorage.getItem(SEEN_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw) as SeenMap;
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function writeSeen(seen: SeenMap) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(SEEN_KEY, JSON.stringify(seen));
  } catch {
    /* quota / private mode */
  }
}

function pickOne(dim: SurveyDim, seen: SeenMap, avoid?: number): number {
  const used = new Set((seen[dim] ?? []).filter((n) => n >= 1 && n <= SURVEY_VARIANT_COUNT));
  let pool = Array.from({ length: SURVEY_VARIANT_COUNT }, (_, i) => i + 1).filter(
    (n) => !used.has(n),
  );
  if (pool.length === 0) {
    // 5개 모두 봤으면 초기화. 직전에 본 문항은 가능하면 제외.
    seen[dim] = [];
    pool = Array.from({ length: SURVEY_VARIANT_COUNT }, (_, i) => i + 1);
    if (avoid && pool.length > 1) pool = pool.filter((n) => n !== avoid);
  }
  return pool[Math.floor(Math.random() * pool.length)];
}

/** 설문 진입 시 유형별 미사용 변종 1개씩 고르고 seen에 기록. */
export function pickAndMarkSurveyVariants(): SurveyVariantPick {
  const seen = readSeen();
  const picks = {} as SurveyVariantPick;
  for (const dim of SURVEY_DIMS) {
    const last = (seen[dim] ?? []).at(-1);
    const v = pickOne(dim, seen, last);
    picks[dim] = v;
    const list = seen[dim] ?? [];
    if (!list.includes(v)) list.push(v);
    seen[dim] = list;
  }
  writeSeen(seen);
  return picks;
}

export function surveyUiKey(dim: SurveyDim, variant: number, part: "t" | "a" | "b"): string {
  const v = Math.max(1, Math.min(SURVEY_VARIANT_COUNT, variant | 0));
  return `${dim}v${v}_${part}`;
}
