import type { Profile } from "./profile";
import type { EngineSnapshot } from "./engine";
import type { Lang } from "./gameData";

const SAVE_KEY = "twc.save";
const SETTINGS_KEY = "twc.settings";

export interface GameSettings {
  bgm: number;
  sfx: number;
  lang: Lang;
}

export function loadSettings(): GameSettings {
  if (typeof window === "undefined")
    return { bgm: 0.8, sfx: 0.8, lang: "KR" };
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return { bgm: 0.8, sfx: 0.8, lang: "KR" };
    const d = JSON.parse(raw);
    return {
      bgm: typeof d.bgm === "number" ? d.bgm : 0.8,
      sfx: typeof d.sfx === "number" ? d.sfx : 0.8,
      lang: d.lang ?? "KR",
    };
  } catch {
    return { bgm: 0.8, sfx: 0.8, lang: "KR" };
  }
}

export function saveSettings(s: GameSettings) {
  if (typeof window !== "undefined")
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
}

export interface SaveMeta {
  label: string;
  savedAt: number;
  name: string;
}

export function readSaveMeta(): SaveMeta | null {
  const snap = loadSnapshot();
  if (!snap) return null;
  return {
    label: snap.label,
    savedAt: snap.savedAt,
    name: snap.profile.name,
  };
}

export function loadSnapshot(): EngineSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as EngineSnapshot;
  } catch {
    return null;
  }
}

export function saveSnapshot(snap: EngineSnapshot) {
  if (typeof window !== "undefined")
    localStorage.setItem(SAVE_KEY, JSON.stringify(snap));
}

export function deleteSave() {
  if (typeof window !== "undefined") localStorage.removeItem(SAVE_KEY);
}

export function hasSave(): boolean {
  return loadSnapshot() !== null;
}
