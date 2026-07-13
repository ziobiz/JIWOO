"use client";

import { useCallback, useEffect, useState } from "react";
import type { Lang } from "./gameData";

const KEY = "twc.lang";

export function useLang(): [Lang, (l: Lang) => void] {
  const [lang, setLangState] = useState<Lang>("KR");

  useEffect(() => {
    const saved = (typeof window !== "undefined" &&
      window.localStorage.getItem(KEY)) as Lang | null;
    if (saved) setLangState(saved);
  }, []);

  const setLang = useCallback((l: Lang) => {
    setLangState(l);
    if (typeof window !== "undefined") window.localStorage.setItem(KEY, l);
  }, []);

  return [lang, setLang];
}

export const NAME_MAX: Record<Lang, number> = { KR: 5, JP: 5, CH: 5, EN: 10 };
export const LANG_FLAG: Record<Lang, string> = {
  KR: "🇰🇷",
  EN: "🇺🇸",
  CH: "🇨🇳",
  JP: "🇯🇵",
};
