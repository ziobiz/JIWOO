import raw from "@/data/game-data.json";

export type Lang = "KR" | "EN" | "CH" | "JP";

/** JSON 노드는 [kind, ...args] 배열. 느슨하게 다룬다. */
export type Node = unknown[];

export interface ChoiceOption {
  label: string;
  effects: Record<string, number>;
  nodes: Node[];
}
export interface ExplorePlace {
  name: string;
  nodes: Node[];
}

interface Dict {
  [k: string]: Partial<Record<Lang, string>>;
}

interface GameData {
  meta: {
    title: string;
    subtitle: string;
    langs: Lang[];
    langNative: Record<Lang, string>;
  };
  constants: {
    initialStats: Record<string, number>;
    allFragments: string[];
    fragmentIcon: Record<string, string>;
    mbtiTypes: string[];
    genderKeys: string[];
    gradeKeys: string[];
    majorKeys: string[];
    portraitCount: number;
    surveyDims?: string[];
    surveyVariantCount?: number;
  };
  story: Node[];
  endings: Record<string, Node[]>;
  i18n: { UI: Dict; TR: Dict; NAMES: Dict; STAT: Dict };
}

export const GAME = raw as unknown as GameData;

// ── i18n 헬퍼 (Python i18n.py 이식) ──────────────────
export function t(text: string | null, lang: Lang): string | null {
  if (text === null || lang === "KR") return text;
  const e = GAME.i18n.TR[text];
  return e?.[lang] ?? text;
}

export function nm(
  name: string | null,
  lang: Lang,
  playerName?: string,
): string | null {
  if (name === "나" && playerName) return playerName;
  if (name === null || lang === "KR") return name;
  const e = GAME.i18n.NAMES[name];
  return e?.[lang] ?? name;
}

export function statLabel(key: string, lang: Lang): string {
  const d = GAME.i18n.STAT[key];
  if (!d) return key;
  return d[lang] ?? d.KR ?? key;
}

export function ui(
  key: string,
  lang: Lang,
  params?: Record<string, string | number>,
): string {
  const d = GAME.i18n.UI[key] ?? {};
  let s = d[lang] || d.KR || key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      s = s.replaceAll(`{${k}}`, String(v));
    }
  }
  return s;
}

// ── 에셋 경로 해석 (game.py IMG_BASE 이식) ────────────
/** 누끼(투명 PNG) 갱신 시 브라우저 캐시 무효화 */
const ASSET_VER = "nukki2";

const CHAR_BASES = new Set([
  "player1",
  "player2",
  "henry",
  "wilson",
  "jim",
  "commander",
  "soldier",
  "daniel",
  "mark",
  "veteran",
  "wounded",
  "medic",
]);

function withVer(path: string, bust: boolean): string {
  return bust ? `${path}?v=${ASSET_VER}` : path;
}

export function imgSrc(key: string | null): string | null {
  if (!key) return null;
  let base = key;
  const bg = key.match(/^bg(\d+)$/);
  if (bg) base = `bg(${bg[1]})`;
  else if (key === "player1") base = "player(1)";
  else if (key === "player2") base = "player(2)";
  const isChar =
    CHAR_BASES.has(key) ||
    key.startsWith("henry") ||
    key.startsWith("portrait") ||
    key.startsWith("player");
  return withVer(`/assets/${base}.png`, isChar);
}

export function portraitSrc(index: number): string {
  return withVer(`/assets/portrait${index}.png`, true);
}

// ── 화자 → 좌측 초상 (game.py resolve_speaker_portrait 이식) ──
const SPEAKER_PORTRAIT: Record<string, string> = {
  헨리: "henry",
  윌슨: "wilson",
  짐: "jim",
  지휘관: "commander",
  병사: "soldier",
  병사A: "soldier",
  병사B: "soldier",
  대니얼: "daniel",
  마크: "mark",
  노병: "veteran",
  부상병: "wounded",
  의무병: "medic",
};

const HENRY_EMOTION: [string, string[]][] = [
  ["henry_hurt", ["겁쟁이로만", "다른 사람들처럼", "날 겁쟁이로"]],
  ["henry_warm", ["미워하지 않아", "용서", "들려주고 싶", "듣고 싶었", "고마워", "네가 있어서", "이제 나는"]],
  ["henry_grief", ["짐이", "돌아오지 못한", "죽었잖아", "끝까지 싸우다", "먼저 떠올"]],
  ["henry_guilt", ["겁쟁이", "비겁", "죄인", "도망쳤", "비웃", "도망친"]],
  ["henry_brave", ["버텨", "앞으로", "이번엔", "이번에", "내가 가", "구하자", "같이 들자", "지킬", "해낼", "가자", "알겠어"]],
  ["henry_afraid", ["무섭", "무서", "두려", "겁나", "도망가고 싶", "도망칠까", "떨려"]],
  ["henry_hope", ["믿어 볼게", "버틸 수 있", "그러길 바라", "다행", "정말?", "바랄게"]],
];

export function resolveSpeakerPortrait(
  speaker: string | null,
  text: string,
): string | null {
  if (!speaker || speaker === "나") return null;
  const base = SPEAKER_PORTRAIT[speaker];
  if (!base) return null;
  if (base === "henry") {
    const tt = text || "";
    for (const [key, kws] of HENRY_EMOTION) {
      if (kws.some((k) => tt.includes(k))) return key;
    }
    return "henry";
  }
  return base;
}

// ── 엔딩 판정 (game.py determine_ending 이식) ─────────
export function determineEnding(
  stats: Record<string, number>,
  itemCount: number,
): string {
  const E = stats["공감"] ?? 0;
  const T = stats["신뢰"] ?? 0;
  const G = stats["죄책감"] ?? 0;
  const C = stats["용기"] ?? 0;
  if (itemCount >= GAME.constants.allFragments.length && E >= 90) return "HIDDEN";
  if (E >= 80 && T >= 80 && G <= 40 && C >= 80) return "TRUE";
  if (T <= 30 || G >= 80) return "BAD";
  if (E >= 60 && C >= 60) return "GOOD";
  return "NORMAL";
}

export function evalCond(
  cond: [string, string, number],
  stats: Record<string, number>,
  conflict: Record<string, number>,
  itemCount: number,
): boolean {
  const [key, op, val] = cond;
  let left: number;
  if (key === "조각수") left = itemCount;
  else if (key === "인간" || key === "군인") left = conflict[key] ?? 0;
  else left = stats[key] ?? 0;
  switch (op) {
    case ">=":
      return left >= val;
    case "<=":
      return left <= val;
    case ">":
      return left > val;
    case "<":
      return left < val;
    case "==":
      return left === val;
    default:
      return false;
  }
}
