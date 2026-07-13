"use client";

import { GAME, type Lang } from "./gameData";
import { LANG_FLAG } from "./useLang";

export function LangSelector({
  lang,
  setLang,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
}) {
  return (
    <div className="flex gap-1.5 rounded-full border border-stone-700 bg-stone-900/80 px-2 py-1.5">
      {GAME.meta.langs.map((l) => (
        <button
          key={l}
          type="button"
          onClick={() => setLang(l)}
          title={GAME.meta.langNative[l]}
          className={`h-7 w-7 rounded-full text-base leading-none transition-all ${
            l === lang
              ? "bg-amber-700/40 ring-1 ring-amber-500 scale-110"
              : "opacity-60 hover:opacity-100"
          }`}
        >
          {LANG_FLAG[l]}
        </button>
      ))}
    </div>
  );
}
