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

export const NAME_MAX: Record<Lang, number> = { KR: 10, JP: 10, CH: 10, EN: 10 };
export const LANG_FLAG: Record<Lang, string> = {
  KR: "🇰🇷",
  EN: "🇺🇸",
  CH: "🇨🇳",
  JP: "🇯🇵",
};
// 국기 이모지가 지원되지 않는 환경(Windows 등) 대비 짧은 코드
export const LANG_CODE: Record<Lang, string> = {
  KR: "한",
  EN: "EN",
  CH: "中",
  JP: "日",
};
