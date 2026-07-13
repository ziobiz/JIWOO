"use client";

import { GAME, ui, statLabel, type Lang } from "./gameData";
import type { GameState } from "./engine";

const STAT_KEYS = ["신뢰", "공감", "인간본능", "사회적역할", "죄책감", "용기"];

export function HudPanel({ lang, state }: { lang: Lang; state: GameState }) {
  const human = state.conflict["인간"] ?? 0;
  const soldier = state.conflict["군인"] ?? 0;
  const total = human + soldier || 1;
  const humanPct = (human / total) * 100;

  return (
    <div className="absolute top-20 right-4 z-10 w-48 rounded-xl border border-stone-700/60 bg-black/55 backdrop-blur-sm p-3 shadow-lg">
      {/* 갈등의 저울 — 중심에서 벌어지는 게이지 */}
      <div className="mb-3">
        <p className="text-[9px] tracking-widest text-amber-600/80 mb-1.5 uppercase">
          Conflict
        </p>
        <div className="relative h-3 rounded-full bg-stone-800 overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 bg-sky-700/80 rounded-l-full transition-all duration-500"
            style={{ width: `${humanPct}%` }}
          />
          <div
            className="absolute inset-y-0 right-0 bg-orange-800/80 rounded-r-full transition-all duration-500"
            style={{ width: `${100 - humanPct}%` }}
          />
          <div className="absolute inset-y-0 left-1/2 w-0.5 bg-amber-400/60 -translate-x-1/2" />
        </div>
        <div className="flex justify-between text-[9px] text-stone-400 mt-1">
          <span>{ui("conflict_human", lang)} {human}</span>
          <span>{soldier} {ui("conflict_soldier", lang)}</span>
        </div>
      </div>

      <div className="h-px bg-stone-700/80 mb-2" />

      {/* 스탯 */}
      <div className="space-y-1.5">
        {STAT_KEYS.map((k) => {
          const v = state.stats[k] ?? 0;
          return (
            <div key={k}>
              <div className="flex justify-between text-[10px]">
                <span className="text-stone-300">{statLabel(k, lang)}</span>
                <span className="text-amber-200/90 font-medium tabular-nums">
                  {v}
                </span>
              </div>
              <div className="h-1 rounded-full bg-stone-800 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-amber-800 to-amber-500 transition-all duration-300"
                  style={{ width: `${Math.min(100, v)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div className="h-px bg-stone-700/80 my-2" />

      {/* 기억 조각 */}
      <div>
        <p className="text-[9px] text-stone-500 mb-1.5">
          {ui("frag_hud", lang, { n: state.items.length, t: GAME.constants.allFragments.length })}
        </p>
        <div className="flex gap-1.5 justify-center">
          {GAME.constants.allFragments.map((f) => {
            const owned = state.items.includes(f);
            return (
              <span
                key={f}
                title={f}
                className={`h-3 w-3 rotate-45 border transition-all ${
                  owned
                    ? "bg-amber-400 border-amber-300 shadow-[0_0_6px_rgba(251,191,36,0.5)]"
                    : "bg-stone-800 border-stone-600"
                }`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
