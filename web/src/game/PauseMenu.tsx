"use client";

import { ui, type Lang } from "./gameData";

export function PauseMenu({
  lang,
  bgmVol,
  sfxVol,
  onBgmVol,
  onSfxVol,
  onResume,
  onSave,
  onLoad,
  onTitle,
  message,
}: {
  lang: Lang;
  bgmVol: number;
  sfxVol: number;
  onBgmVol: (v: number) => void;
  onSfxVol: (v: number) => void;
  onResume: () => void;
  onSave: () => void;
  onLoad: () => void;
  onTitle: () => void;
  message: string;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="w-full max-w-md rounded-xl border border-amber-800/50 bg-stone-900 p-6 space-y-3">
        <h2 className="text-center font-serif text-xl text-amber-100 mb-4">
          {ui("pause_title", lang)}
        </h2>

        <MenuBtn onClick={onResume} primary>
          {ui("resume", lang)}
        </MenuBtn>
        <MenuBtn onClick={onSave}>{ui("save", lang)}</MenuBtn>
        <MenuBtn onClick={onLoad}>{ui("load", lang)}</MenuBtn>

        <VolRow
          label={ui("bgm_vol", lang)}
          value={bgmVol}
          onChange={onBgmVol}
        />
        <VolRow
          label={ui("sfx_vol", lang)}
          value={sfxVol}
          onChange={onSfxVol}
        />

        <MenuBtn onClick={onTitle}>{ui("to_title", lang)}</MenuBtn>

        {message && (
          <p className="text-center text-sm text-emerald-400 pt-1">{message}</p>
        )}
        <p className="text-center text-xs text-stone-600 pt-2">
          {ui("pause_hint", lang)}
        </p>
      </div>
    </div>
  );
}

function MenuBtn({
  children,
  onClick,
  primary,
}: {
  children: React.ReactNode;
  onClick: () => void;
  primary?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg border px-4 py-2.5 text-sm transition-colors ${
        primary
          ? "border-amber-600 bg-amber-700/40 text-amber-50 hover:bg-amber-700/60"
          : "border-stone-700 bg-stone-950 text-stone-200 hover:border-amber-800"
      }`}
    >
      {children}
    </button>
  );
}

function VolRow({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center gap-3 px-1">
      <span className="text-sm text-stone-300 w-20 shrink-0">{label}</span>
      <input
        type="range"
        min={0}
        max={100}
        value={Math.round(value * 100)}
        onChange={(e) => onChange(Number(e.target.value) / 100)}
        className="flex-1 accent-amber-600"
      />
      <span className="text-xs text-stone-500 w-8 text-right">
        {Math.round(value * 100)}
      </span>
    </div>
  );
}
