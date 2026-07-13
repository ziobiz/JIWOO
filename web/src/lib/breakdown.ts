/** 학년·성별·전공·MBTI 그룹별 교차분석 */
import type { PlayResult } from "@/types/game";

const GOOD_ENDINGS = new Set(["TRUE", "GOOD", "HIDDEN"]);

export const LABEL: Record<string, string> = {
  // 성별
  g_m: "남",
  g_f: "여",
  g_x: "선택 안 함",
  // 학년
  grade_1: "1학년",
  grade_2: "2학년",
  grade_3: "3학년",
  // 전공
  maj_ec: "영중",
  maj_ej: "영일",
  maj_ch: "중국어",
  maj_jp: "일본어",
};

export function label(key: string): string {
  return LABEL[key] ?? key;
}

export interface GroupStat {
  key: string;
  label: string;
  n: number;
  goodEndingPct: number; // 진엔딩(TRUE/GOOD/HIDDEN) 비율
  principlePct: number; // Q1=A(원칙) 비율
  altruismPct: number; // Q3=B(이타심) 비율
  avgCourage: number;
  avgEmpathy: number;
  avgGuilt: number;
  avgHuman: number;
  avgSoldier: number;
  avgFragments: number;
  avgMatches: number;
}

function round1(n: number): number {
  return Math.round(n * 10) / 10;
}

function avg(rows: PlayResult[], pick: (r: PlayResult) => number): number {
  if (!rows.length) return 0;
  return round1(rows.reduce((s, r) => s + pick(r), 0) / rows.length);
}

function pct(n: number, d: number): number {
  return d ? round1((100 * n) / d) : 0;
}

export function statOf(key: string, lbl: string, rows: PlayResult[]): GroupStat {
  const n = rows.length;
  const q1 = rows.filter((r) => r.q1 === "A" || r.q1 === "B");
  const q3 = rows.filter((r) => r.q3 === "A" || r.q3 === "B");
  return {
    key,
    label: lbl,
    n,
    goodEndingPct: pct(rows.filter((r) => GOOD_ENDINGS.has(r.ending)).length, n),
    principlePct: pct(q1.filter((r) => r.q1 === "A").length, q1.length),
    altruismPct: pct(q3.filter((r) => r.q3 === "B").length, q3.length),
    avgCourage: avg(rows, (r) => r.courage),
    avgEmpathy: avg(rows, (r) => r.empathy),
    avgGuilt: avg(rows, (r) => r.guilt),
    avgHuman: avg(rows, (r) => r.human),
    avgSoldier: avg(rows, (r) => r.soldier),
    avgFragments: avg(rows, (r) => r.fragments),
    avgMatches: avg(rows, (r) => r.matches),
  };
}

/** 주어진 키 순서대로 그룹 통계를 만든다(데이터 없는 그룹도 0으로 표시). */
function breakdown(
  rows: PlayResult[],
  keys: string[],
  keyFn: (r: PlayResult) => string,
): GroupStat[] {
  return keys.map((k) => statOf(k, label(k), rows.filter((r) => keyFn(r) === k)));
}

const GENDER_KEYS = ["g_m", "g_f", "g_x"];
const GRADE_KEYS = ["grade_1", "grade_2", "grade_3"];
const MAJOR_KEYS = ["maj_ec", "maj_ej", "maj_ch", "maj_jp"];

export function byGender(rows: PlayResult[]): GroupStat[] {
  return breakdown(rows, GENDER_KEYS, (r) => r.gender);
}
export function byGrade(rows: PlayResult[]): GroupStat[] {
  return breakdown(rows, GRADE_KEYS, (r) => r.grade);
}
export function byMajor(rows: PlayResult[]): GroupStat[] {
  return breakdown(rows, MAJOR_KEYS, (r) => r.major);
}

/** MBTI 사고형(T) vs 감정형(F) */
export function byMbtiTF(rows: PlayResult[]): GroupStat[] {
  const isT = (r: PlayResult) => r.mbti.length >= 3 && r.mbti[2].toUpperCase() === "T";
  const isF = (r: PlayResult) => r.mbti.length >= 3 && r.mbti[2].toUpperCase() === "F";
  return [
    statOf("T", "사고형 T", rows.filter(isT)),
    statOf("F", "감정형 F", rows.filter(isF)),
  ];
}

/** MBTI 16유형 — 데이터가 있는 유형만(표본순 정렬) */
export function byMbtiType(rows: PlayResult[]): GroupStat[] {
  const map = new Map<string, PlayResult[]>();
  for (const r of rows) {
    const t = (r.mbti || "").toUpperCase().slice(0, 4);
    if (t.length !== 4) continue;
    (map.get(t) ?? map.set(t, []).get(t)!).push(r);
  }
  return [...map.entries()]
    .map(([k, rs]) => statOf(k, k, rs))
    .sort((a, b) => b.n - a.n);
}
