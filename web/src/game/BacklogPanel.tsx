"use client";

import { useEffect, useRef } from "react";
import { t, nm, ui, type Lang } from "./gameData";
import type { BacklogEntry } from "./engine";

export function BacklogPanel({
  lang,
  entries,
  playerName,
  onClose,
}: {
  lang: Lang;
  entries: BacklogEntry[];
  playerName: string;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [entries]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/85"
      onClick={onClose}
    >
      <div
        className="w-full max-w-2xl max-h-[75vh] mx-4 rounded-xl border border-stone-700 bg-stone-900 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-5 py-3 border-b border-stone-800">
          <h2 className="font-serif text-amber-100">{ui("backlog_title", lang)}</h2>
        </div>
        <div ref={ref} className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {entries.length === 0 ? (
            <p className="text-sm text-stone-500 text-center py-8">
              {ui("backlog_empty", lang)}
            </p>
          ) : (
            entries.map((e, i) => (
              <div key={i} className="text-sm">
                {e.speaker && (
                  <span className="text-amber-400 font-medium mr-2">
                    {nm(e.speaker, lang, playerName)}
                  </span>
                )}
                <span
                  className={
                    e.mode === "mono"
                      ? "italic text-stone-400"
                      : e.mode === "act"
                        ? "text-stone-500"
                        : "text-stone-200"
                  }
                >
                  {t(e.text, lang)}
                </span>
              </div>
            ))
          )}
        </div>
        <p className="text-xs text-stone-600 text-center py-2 border-t border-stone-800">
          {ui("backlog_hint", lang)}
        </p>
      </div>
    </div>
  );
}
