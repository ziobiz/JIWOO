"use client";

import { useCallback, useEffect, useMemo, useReducer, useRef, useState } from "react";
import Image from "next/image";
import { Engine, type EngineSnapshot, type GameState } from "./engine";
import {
  GAME,
  t,
  nm,
  ui,
  imgSrc,
  portraitSrc,
  type Lang,
} from "./gameData";
import type { Profile } from "./profile";
import { LangSelector } from "./LangSelector";
import { HudPanel } from "./HudPanel";
import { PauseMenu } from "./PauseMenu";
import { BacklogPanel } from "./BacklogPanel";
import { getAudio } from "./audio";
import { saveSnapshot, loadSnapshot, saveSettings, loadSettings } from "./save";

export function PlayView({
  lang,
  setLang,
  profile,
  initialSnapshot,
  onEnd,
  onTitle,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  profile: Profile;
  initialSnapshot?: EngineSnapshot | null;
  onEnd: (code: string, state: GameState) => void;
  onTitle: () => void;
}) {
  const engineRef = useRef<Engine | null>(null);
  if (engineRef.current === null) {
    engineRef.current = initialSnapshot
      ? Engine.fromSnapshot({ ...initialSnapshot, profile })
      : new Engine();
  }
  const engine = engineRef.current;
  const audio = getAudio();
  const [, force] = useReducer((x) => x + 1, 0);
  const endedRef = useRef(false);

  const [paused, setPaused] = useState(false);
  const [backlogOpen, setBacklogOpen] = useState(false);
  const [pauseMsg, setPauseMsg] = useState("");
  const [bgmVol, setBgmVol] = useState(() => loadSettings().bgm);
  const [sfxVol, setSfxVol] = useState(() => loadSettings().sfx);
  const [fade, setFade] = useState(false);
  const [displayBg, setDisplayBg] = useState(engine.state.bg);
  const prevBg = useRef(engine.state.bg);

  // 오디오 훅 연결
  useEffect(() => {
    engine.onBgm = (k) => audio.playBgm(k);
    engine.onAmb = (k) => audio.playAmb(k);
    engine.onSfx = (k) => audio.playSfx(k);
    engine.onBgChange = (bg) => {
      if (bg !== prevBg.current) {
        prevBg.current = bg;
        setFade(true);
        setTimeout(() => {
          setDisplayBg(bg);
          setFade(false);
        }, 350);
      }
    };
    audio.setBgmVol(bgmVol);
    audio.setSfxVol(sfxVol);
    if (engine.currentBgm) audio.playBgm(engine.currentBgm);
    if (engine.currentAmb) audio.playAmb(engine.currentAmb);

    // 자동재생 정책 대비: 첫 상호작용(클릭/키/터치)에서 반드시 오디오를 깨운다
    const prime = () => primeAudio();
    window.addEventListener("pointerdown", prime, { once: true });
    window.addEventListener("keydown", prime, { once: true });
    window.addEventListener("touchstart", prime, { once: true });
    return () => {
      window.removeEventListener("pointerdown", prime);
      window.removeEventListener("keydown", prime);
      window.removeEventListener("touchstart", prime);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const tick = useCallback(() => {
    if (engine.done && !endedRef.current) {
      endedRef.current = true;
      audio.stopAll();
      onEnd(engine.endingCode ?? "NORMAL", engine.state);
      return;
    }
    force();
  }, [engine, audio, onEnd]);

  // 첫 사용자 상호작용 시 오디오 잠금 해제 + 현재 BGM/앰비언스 즉시 재생.
  // (프롤로그 bgm 노드는 엔진 생성자에서 소비되므로 여기서 동기화해야 소리가 난다)
  const primeAudio = useCallback(() => {
    audio.unlock();
    if (engine.currentBgm) audio.playBgm(engine.currentBgm);
    if (engine.currentAmb) audio.playAmb(engine.currentAmb);
  }, [audio, engine]);

  const unlockAndAdvance = () => {
    primeAudio();
    engine.advance();
    tick();
  };

  const choose = (i: number) => {
    primeAudio();
    audio.playSfx("click");
    engine.choose(i);
    tick();
  };

  const explore = (i: number) => {
    primeAudio();
    audio.playSfx("click");
    engine.selectExplore(i);
    tick();
  };

  // 키보드
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (backlogOpen) setBacklogOpen(false);
        else setPaused((p) => !p);
        return;
      }
      if (paused || backlogOpen) return;
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        if (
          engine.frame &&
          ["text", "title", "card", "result", "item"].includes(engine.frame.type)
        )
          unlockAndAdvance();
      }
    };
    const onWheel = (e: WheelEvent) => {
      if (e.deltaY < -30 && !paused) setBacklogOpen(true);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("wheel", onWheel, { passive: true });
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("wheel", onWheel);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paused, backlogOpen]);

  const handleBgmVol = (v: number) => {
    setBgmVol(v);
    audio.setBgmVol(v);
    saveSettings({ bgm: v, sfx: sfxVol, lang });
  };
  const handleSfxVol = (v: number) => {
    setSfxVol(v);
    audio.setSfxVol(v);
    saveSettings({ bgm: bgmVol, sfx: v, lang });
  };

  const handleSave = () => {
    saveSnapshot(engine.getCheckpoint(profile));
    setPauseMsg(ui("saved_msg", lang));
    audio.playSfx("item");
    setTimeout(() => setPauseMsg(""), 2000);
  };

  const handleLoad = () => {
    const snap = loadSnapshot();
    if (!snap) {
      setPauseMsg(ui("no_save", lang));
      setTimeout(() => setPauseMsg(""), 2000);
      return;
    }
    engineRef.current = Engine.fromSnapshot({ ...snap, profile: snap.profile });
    prevBg.current = engineRef.current.state.bg;
    setDisplayBg(engineRef.current.state.bg);
    if (engineRef.current.currentBgm)
      audio.playBgm(engineRef.current.currentBgm);
    if (engineRef.current.currentAmb)
      audio.playAmb(engineRef.current.currentAmb);
    setPaused(false);
    setPauseMsg(ui("load", lang));
    setTimeout(() => setPauseMsg(""), 1500);
    force();
  };

  const frame = engine.frame;
  const state = engine.state;
  const bgSrc = imgSrc(displayBg);

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
      {/* 배경 + 페이드 */}
      {bgSrc && (
        <Image
          src={bgSrc}
          alt="bg"
          fill
          priority
          sizes="100vw"
          className={`object-cover transition-opacity duration-700 ${fade ? "opacity-0" : "opacity-100"}`}
        />
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/20 to-black/40" />

      {centerChar && (
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 h-[78%] w-[40%]">
          <Image src={centerChar} alt="char" fill sizes="40vw" className="object-contain object-bottom" />
        </div>
      )}
      {leftPortrait && (
        <div className="absolute bottom-0 left-4 h-[72%] w-[30%] max-w-[380px]">
          <Image src={leftPortrait} alt="speaker" fill sizes="30vw" className="object-contain object-bottom" />
        </div>
      )}

      <div className="absolute top-0 inset-x-0 flex items-start justify-between p-4 z-20">
        <LangSelector lang={lang} setLang={setLang} />
        <div className="rounded-lg bg-black/50 px-3 py-1.5 text-right border border-stone-800/50">
          <p className="text-sm text-amber-100">{profile.name}</p>
          <p className="text-[10px] text-stone-400">
            {ui(profile.grade, lang)} · {ui(profile.major, lang)} · {profile.mbti}
          </p>
        </div>
      </div>

      <HudPanel lang={lang} state={state} />

      {clickToAdvance && !paused && (
        <button
          type="button"
          aria-label="advance"
          onClick={unlockAndAdvance}
          className="absolute inset-0 z-0 cursor-pointer"
        />
      )}

      {/* 프레임 UI */}
      <div className="absolute inset-x-0 bottom-0 z-10 p-4 sm:p-8 pointer-events-none">
        {frame?.type === "text" && (
          <div className="mx-auto max-w-3xl">
            {frame.speaker && (
              <div className="mb-1 inline-block rounded-t-lg bg-amber-800/90 px-4 py-1 font-serif text-amber-50 text-sm">
                {nm(frame.speaker, lang, profile.name)}
              </div>
            )}
            <div
              className={`rounded-lg border border-stone-700/50 bg-black/85 px-6 py-5 text-lg leading-relaxed backdrop-blur-sm ${
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
            <p className="mt-2 text-right text-xs text-amber-500/70">
              <span className="animate-pulse">Click / Space »»</span>
            </p>
          </div>
        )}

        {frame?.type === "title" && (
          <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/70">
            {frame.lines.map((ln, i) => (
              <h2 key={i} className="font-serif text-3xl sm:text-5xl text-amber-50 py-1 tracking-wide">
                {t(ln, lang)}
              </h2>
            ))}
            {frame.sub && (
              <p className="mt-6 max-w-xl text-center text-sm text-stone-400 italic px-6">
                {t(frame.sub, lang)}
              </p>
            )}
          </div>
        )}

        {frame?.type === "card" && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/60">
            <div className="w-full max-w-md rounded-xl border border-amber-700/60 bg-stone-900/95 p-6 shadow-2xl">
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
          <div className="fixed inset-0 flex items-center justify-center bg-black/80">
            <h2 className="font-serif text-2xl text-amber-100 text-center px-6">
              {t(frame.title, lang)}
            </h2>
          </div>
        )}

        {frame?.type === "item" && (
          <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/85">
            <div className="relative">
              <div className="h-20 w-20 rotate-45 bg-amber-400 animate-pulse shadow-[0_0_30px_rgba(251,191,36,0.6)]" />
              <div className="absolute inset-0 animate-ping h-20 w-20 rotate-45 bg-amber-300/30" />
            </div>
            <p className="mt-8 text-xs tracking-[0.3em] text-amber-500">
              {ui("frag_get", lang)}
            </p>
            <h3 className="mt-2 font-serif text-2xl text-amber-100">
              {t(frame.name, lang)}
            </h3>
            <p className="mt-4 text-xs text-stone-500">{ui("frag_get_hint", lang)}</p>
          </div>
        )}

        {frame?.type === "choice" && (
          <div className="mx-auto max-w-2xl space-y-2 pointer-events-auto">
            {frame.options.map((o) => (
              <button
                key={o.index}
                type="button"
                onClick={() => choose(o.index)}
                className="block w-full rounded-lg border border-amber-800/50 bg-black/85 px-5 py-3.5 text-left text-base text-stone-100 hover:border-amber-500 hover:bg-amber-900/40 transition-all backdrop-blur-sm"
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
            <p className="mt-2 text-center text-xs text-stone-600">
              {ui("explore_footer", lang, {
                done: frame.places.filter((p) => p.visited).length,
                total: frame.places.length,
              })}
            </p>
          </div>
        )}
      </div>

      {paused && (
        <PauseMenu
          lang={lang}
          bgmVol={bgmVol}
          sfxVol={sfxVol}
          onBgmVol={handleBgmVol}
          onSfxVol={handleSfxVol}
          onResume={() => setPaused(false)}
          onSave={handleSave}
          onLoad={handleLoad}
          onTitle={() => {
            audio.stopAll();
            onTitle();
          }}
          message={pauseMsg}
        />
      )}

      {backlogOpen && (
        <BacklogPanel
          lang={lang}
          entries={engine.backlog}
          playerName={profile.name}
          onClose={() => setBacklogOpen(false)}
        />
      )}
    </div>
  );
}
