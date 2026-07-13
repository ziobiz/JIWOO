"use client";

import { GAME, ui, statLabel, type Lang } from "./gameData";
import type { GameState } from "./engine";

/** 데스크톱판과 동일한 3개 그룹 구성 */
const GROUPS: { titleKey: string; keys: string[] }[] = [
  { titleKey: "grp_relation", keys: ["신뢰", "공감"] },
  { titleKey: "grp_player", keys: ["인간본능", "사회적역할"] },
  { titleKey: "grp_henry", keys: ["죄책감", "용기"] },
];

// 스탯별 게이지 색 (관계=호박, 능력치=청록, 상태=자주)
const STAT_COLOR: Record<string, string> = {
  신뢰: "from-amber-700 to-amber-400",
  공감: "from-amber-700 to-amber-400",
  인간본능: "from-teal-800 to-emerald-400",
  사회적역할: "from-sky-800 to-sky-400",
  죄책감: "from-rose-900 to-rose-500",
  용기: "from-orange-800 to-amber-400",
};

function StatRow({
  k,
  lang,
  value,
}: {
  k: string;
  lang: Lang;
  value: number;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[11px] text-stone-300 w-16 shrink-0">
        {statLabel(k, lang)}
      </span>
      <div className="flex-1 h-1.5 rounded-full bg-stone-800 overflow-hidden">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${STAT_COLOR[k] ?? "from-amber-700 to-amber-400"} transition-all duration-300`}
          style={{ width: `${Math.min(100, value)}%` }}
        />
      </div>
      <span className="text-[11px] tabular-nums text-amber-200/90 w-6 text-right">
        {value}
      </span>
    </div>
  );
}

export function HudPanel({ lang, state }: { lang: Lang; state: GameState }) {
  const human = state.conflict["인간"] ?? 0;
  const soldier = state.conflict["군인"] ?? 0;
  const total = human + soldier || 1;
  const humanPct = (human / total) * 100;

  return (
    <div className="absolute top-20 right-4 z-10 w-56 rounded-xl border border-amber-900/40 bg-gradient-to-b from-black/70 to-stone-950/80 backdrop-blur-sm p-3.5 shadow-xl">
      {/* 갈등의 저울 */}
      <div className="mb-3">
        <p className="text-[9px] tracking-[0.25em] text-amber-600/80 mb-1.5 uppercase">
          {ui("an_scale", lang)}
        </p>
        <div className="relative h-3 rounded-full bg-stone-800 overflow-hidden ring-1 ring-stone-700/60">
          <div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-sky-800 to-sky-600 transition-all duration-500"
            style={{ width: `${humanPct}%` }}
          />
          <div
            className="absolute inset-y-0 right-0 bg-gradient-to-l from-orange-900 to-orange-700 transition-all duration-500"
            style={{ width: `${100 - humanPct}%` }}
          />
          <div className="absolute inset-y-0 left-1/2 w-px bg-amber-300/70 -translate-x-1/2" />
        </div>
        <div className="flex justify-between text-[9px] text-stone-400 mt-1">
          <span>{ui("conflict_human", lang)} {human}</span>
          <span>{soldier} {ui("conflict_soldier", lang)}</span>
        </div>
      </div>

      {/* 3개 그룹 */}
      {GROUPS.map((g) => (
        <div key={g.titleKey} className="mt-3">
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="h-3 w-0.5 rounded bg-amber-500" />
            <p className="text-[10px] font-medium text-amber-200/90 tracking-wide">
              {ui(g.titleKey, lang)}
            </p>
          </div>
          <div className="space-y-1.5 pl-2">
            {g.keys.map((k) => (
              <StatRow key={k} k={k} lang={lang} value={state.stats[k] ?? 0} />
            ))}
          </div>
        </div>
      ))}

      {/* 기억 조각 */}
      <div className="mt-3 pt-2.5 border-t border-amber-900/30">
        <div className="flex items-center justify-between">
          <p className="text-[10px] text-stone-400">
            {ui("frag_hud", lang, {
              n: state.items.length,
              t: GAME.constants.allFragments.length,
            })}
          </p>
          <div className="flex gap-1">
            {GAME.constants.allFragments.map((f) => {
              const owned = state.items.includes(f);
              return (
                <span
                  key={f}
                  title={f}
                  className={`h-2.5 w-2.5 rotate-45 border transition-all ${
                    owned
                      ? "bg-amber-400 border-amber-300 shadow-[0_0_6px_rgba(251,191,36,0.6)]"
                      : "bg-stone-800/60 border-stone-600"
                  }`}
                />
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
