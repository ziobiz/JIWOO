"use client";

import { GAME, type Lang } from "./gameData";
import { LANG_CODE } from "./useLang";

export function LangSelector({
  lang,
  setLang,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
}) {
  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-stone-700 bg-stone-900/80 p-1">
      {GAME.meta.langs.map((l) => {
        const active = l === lang;
        return (
          <button
            key={l}
            type="button"
            onClick={() => setLang(l)}
            title={GAME.meta.langNative[l]}
            aria-pressed={active}
            className={`inline-flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold leading-none transition-colors ${
              active
                ? "bg-amber-600 text-stone-950"
                : "text-stone-400 hover:text-stone-100 hover:bg-stone-800"
            }`}
          >
            {LANG_CODE[l]}
          </button>
        );
      })}
    </div>
  );
}
