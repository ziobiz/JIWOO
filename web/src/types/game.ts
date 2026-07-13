/** 플레이 결과 — results.csv / Supabase play_results 와 동일 스키마 */

export type Gender = "g_m" | "g_f" | "g_x";
export type Grade = "grade_1" | "grade_2" | "grade_3";
export type Major = "maj_ec" | "maj_ej" | "maj_ch" | "maj_jp";
export type SurveyAnswer = "A" | "B";
export type EndingCode = "TRUE" | "GOOD" | "NORMAL" | "BAD" | "HIDDEN";

export interface PlayerProfile {
  name: string;
  gender: Gender;
  grade: Grade;
  major: Major;
  mbti: string;
  portrait: number;
  survey: { q1?: SurveyAnswer; q2?: SurveyAnswer; q3?: SurveyAnswer };
}

export interface PlayResult {
  id?: string;
  created_at?: string;
  name: string;
  gender: Gender;
  grade: Grade;
  major: Major;
  mbti: string;
  q1: SurveyAnswer | "";
  q2: SurveyAnswer | "";
  q3: SurveyAnswer | "";
  ending: EndingCode;
  human: number;
  soldier: number;
  trust: number;
  empathy: number;
  instinct: number;
  duty: number;
  guilt: number;
  courage: number;
  fragments: number;
  matches: number;
}

export interface AnalysisReport {
  generatedAt: string;
  source: string;
  sampleSize: number;
  reference: typeof import("@/lib/references").REFERENCE;
  data: {
    endingDistribution: { code: string; count: number; pct: number }[];
    goodEndingPct: number;
    model1: {
      n: number;
      principlePct: number;
      empathyPct: number;
      malePrinciplePct: number;
      femalePrinciplePct: number;
      maleN: number;
      femaleN: number;
      avgHuman: number;
      avgSoldier: number;
    };
    model2: {
      tN: number;
      fN: number;
      tGoodEndingPct: number;
      fGoodEndingPct: number;
      tAvgCourage: number;
      fAvgCourage: number;
    };
    model3: {
      n: number;
      selfPct: number;
      altruismPct: number;
      avgInstinct: number;
      avgEmpathy: number;
      avgFragments: number;
    };
  };
}
