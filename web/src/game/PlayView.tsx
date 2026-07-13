"use client";

import { useEffect, useMemo, useReducer, useRef } from "react";
import Image from "next/image";
import { Engine, type GameState } from "./engine";
import {
  GAME,
  t,
  nm,
  ui,
  statLabel,
  imgSrc,
  portraitSrc,
  type Lang,
} from "./gameData";
import type { Profile } from "./profile";
import { LangSelector } from "./LangSelector";

const STAT_KEYS = ["신뢰", "공감", "인간본능", "사회적역할", "죄책감", "용기"];

export function PlayView({
  lang,
  setLang,
  profile,
  onEnd,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  profile: Profile;
  onEnd: (code: string, state: GameState) => void;
}) {
  const engineRef = useRef<Engine | null>(null);
  if (engineRef.current === null) engineRef.current = new Engine();
  const engine = engineRef.current;
  const [, force] = useReducer((x) => x + 1, 0);
  const endedRef = useRef(false);

  const tick = () => {
    if (engine.done && !endedRef.current) {
      endedRef.current = true;
      onEnd(engine.endingCode ?? "NORMAL", engine.state);
      return;
    }
    force();
  };

  const advance = () => {
    engine.advance();
    tick();
  };
  const choose = (i: number) => {
    engine.choose(i);
    tick();
  };
  const explore = (i: number) => {
    engine.selectExplore(i);
    tick();
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        if (engine.frame && ["text", "title", "card", "result", "item"].includes(engine.frame.type))
          advance();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const frame = engine.frame;
  const state = engine.state;

  const bgSrc = imgSrc(state.bg);
  // 좌측 인물: 대사 화자 우선(플레이어 or NPC 초상), 없으면 중앙 스프라이트
  const leftPortrait = useMemo(() => {
    if (frame?.type === "text") {
      if (frame.speaker === "나") return portraitSrc(profile.portrait);
      if (frame.portrait) return imgSrc(frame.portrait);
    }
    return null;
  }, [frame, profile.portrait]);
  const centerChar = !leftPortrait ? imgSrc(state.charKey) : null;

  const clickToAdvance =
    frame && ["text", "title", "card", "result", "item"].includes(frame.type);

  return (
    <div className="fixed inset-0 select-none overflow-hidden bg-black text-stone-100">
      {/* 배경 */}
      {bgSrc && (
        <Image src={bgSrc} alt="bg" fill priority sizes="100vw" className="object-cover" />
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-black/40" />

      {/* 중앙 스프라이트 */}
      {centerChar && (
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[78%] w-[40%]">
          <Image src={centerChar} alt="char" fill sizes="40vw" className="object-contain object-bottom" />
        </div>
      )}
      {/* 좌측 인물 */}
      {leftPortrait && (
        <div className="absolute bottom-0 left-4 h-[72%] w-[30%] max-w-[380px]">
          <Image src={leftPortrait} alt="speaker" fill sizes="30vw" className="object-contain object-bottom" />
        </div>
      )}

      {/* 상단 바 : 언어 + 플레이어 이름 */}
      <div className="absolute top-0 inset-x-0 flex items-start justify-between p-4 z-20">
        <LangSelector lang={lang} setLang={setLang} />
        <div className="rounded-lg bg-black/50 px-3 py-1.5 text-right">
          <p className="text-sm text-amber-100">{profile.name || nm("나", lang)}</p>
          <p className="text-[10px] text-stone-400">
            {ui(profile.grade, lang)} · {ui(profile.major, lang)} · {profile.mbti}
          </p>
        </div>
      </div>

      {/* HUD : 스탯 */}
      <div className="absolute top-20 right-4 z-10 w-44 space-y-1.5 rounded-lg bg-black/45 p-3">
        {STAT_KEYS.map((k) => (
          <div key={k}>
            <div className="flex justify-between text-[10px] text-stone-300">
              <span>{statLabel(k, lang)}</span>
              <span>{state.stats[k] ?? 0}</span>
            </div>
            <div className="h-1 rounded bg-stone-800">
              <div
                className="h-1 rounded bg-amber-600"
                style={{ width: `${Math.min(100, state.stats[k] ?? 0)}%` }}
              />
            </div>
          </div>
        ))}
        <div className="flex items-center justify-between pt-1 text-[10px] text-stone-400">
          <span>{ui("conflict_human", lang)} {state.conflict["인간"] ?? 0}</span>
          <span>{state.conflict["군인"] ?? 0} {ui("conflict_soldier", lang)}</span>
        </div>
        <div className="flex gap-1 pt-1">
          {GAME.constants.allFragments.map((f) => (
            <span
              key={f}
              className={`h-2 w-2 rotate-45 ${state.items.includes(f) ? "bg-amber-400" : "bg-stone-700"}`}
            />
          ))}
        </div>
      </div>

      {/* 클릭 진행 레이어 */}
      {clickToAdvance && (
        <button
          type="button"
          aria-label="advance"
          onClick={advance}
          className="absolute inset-0 z-0 cursor-pointer"
        />
      )}

      {/* 프레임별 UI */}
      <div className="absolute inset-x-0 bottom-0 z-10 p-4 sm:p-8 pointer-events-none">
        {frame?.type === "text" && (
          <div className="mx-auto max-w-3xl pointer-events-none">
            {frame.speaker && (
              <div className="mb-2 inline-block rounded-t-lg bg-amber-800/90 px-4 py-1 font-serif text-amber-50">
                {nm(frame.speaker, lang, profile.name)}
              </div>
            )}
            <div
              className={`rounded-lg bg-black/80 px-6 py-5 text-lg leading-relaxed ${
                frame.mode === "mono"
                  ? "italic text-stone-300"
                  : frame.mode === "narr"
                    ? "text-stone-200"
                    : frame.mode === "act"
                      ? "text-stone-400 text-base"
                      : "text-stone-50"
              }`}
            >
              {t(frame.text, lang)}
            </div>
            <p className="mt-2 text-right text-xs text-amber-500/70 animate-pulse">
              Click / Space »»
            </p>
          </div>
        )}

        {frame?.type === "title" && (
          <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/70 pointer-events-none">
            {frame.lines.map((ln, i) => (
              <h2 key={i} className="font-serif text-3xl sm:text-4xl text-amber-50 py-1">
                {t(ln, lang)}
              </h2>
            ))}
            {frame.sub && (
              <p className="mt-4 max-w-xl text-center text-sm text-stone-400 italic">
                {t(frame.sub, lang)}
              </p>
            )}
          </div>
        )}

        {frame?.type === "card" && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/60 pointer-events-none">
            <div className="w-full max-w-md rounded-xl border border-amber-700/60 bg-stone-900 p-6">
              <p className="text-xs tracking-widest text-amber-500 uppercase">
                {frame.cardKind}
              </p>
              <h3 className="mt-1 font-serif text-lg text-amber-100">
                {t(frame.title, lang)}
              </h3>
              <div className="mt-3 space-y-1 text-sm text-stone-300">
                {frame.body.map((b, i) => (
                  <p key={i}>{t(b, lang)}</p>
                ))}
              </div>
            </div>
          </div>
        )}

        {frame?.type === "result" && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/80 pointer-events-none">
            <h2 className="font-serif text-2xl text-amber-100 text-center px-6">
              {t(frame.title, lang)}
            </h2>
          </div>
        )}

        {frame?.type === "item" && (
          <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/80 pointer-events-none">
            <div className="h-16 w-16 rotate-45 bg-amber-400 animate-pulse" />
            <p className="mt-6 text-xs tracking-widest text-amber-500">MEMORY FRAGMENT</p>
            <h3 className="mt-2 font-serif text-2xl text-amber-100">{t(frame.name, lang)}</h3>
          </div>
        )}

        {frame?.type === "choice" && (
          <div className="mx-auto max-w-2xl space-y-2 pointer-events-auto">
            {frame.options.map((o) => (
              <button
                key={o.index}
                type="button"
                onClick={() => choose(o.index)}
                className="block w-full rounded-lg border border-amber-800/50 bg-black/80 px-5 py-3 text-left text-base text-stone-100 hover:border-amber-500 hover:bg-amber-900/40 transition-colors"
              >
                {t(o.label, lang)}
              </button>
            ))}
          </div>
        )}

        {frame?.type === "explore" && (
          <div className="mx-auto max-w-2xl pointer-events-auto">
            <p className="mb-3 text-center text-sm text-amber-300">
              {ui("explore_q", lang)}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {frame.places.map((p) => (
                <button
                  key={p.index}
                  type="button"
                  disabled={p.visited}
                  onClick={() => explore(p.index)}
                  className={`rounded-lg border px-4 py-4 text-center text-sm transition-colors ${
                    p.visited
                      ? "border-stone-800 bg-stone-900/50 text-stone-600"
                      : "border-amber-800/50 bg-black/80 text-stone-100 hover:border-amber-500 hover:bg-amber-900/40"
                  }`}
                >
                  {t(p.name, lang)}
                  {p.visited && " ✓"}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
