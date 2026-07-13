"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useLang } from "./useLang";
import { ui, t, statLabel, type Lang } from "./gameData";
import type { Profile } from "./profile";
import type { GameState } from "./engine";
import type { EngineSnapshot } from "./engine";
import { CharacterCreator } from "./CharacterCreator";
import { PlayView } from "./PlayView";
import { LangSelector } from "./LangSelector";
import { CreditsFooter } from "./CreditsFooter";
import { readSaveMeta, hasSave, deleteSave, loadSnapshot } from "./save";

type Phase =
  | "title"
  | "create"
  | "play"
  | "final"
  | "analysis"
  | "result";

function computeMatches(
  profile: Profile,
  state: GameState,
  ending: string,
): number {
  const s = state.conflict["군인"] ?? 0;
  const h = state.conflict["인간"] ?? 0;
  const C = state.stats["용기"] ?? 0;
  const G = state.stats["죄책감"] ?? 0;
  const I = state.stats["인간본능"] ?? 0;
  const E = state.stats["공감"] ?? 0;
  const sv = profile.survey;
  let m = 0;
  if (sv.q1 === "A" && s >= h) m++;
  else if (sv.q1 === "B" && h >= s) m++;
  const cover = ending === "BAD" || G >= 60 || C < 60;
  if (sv.q2 === "A" && !cover) m++;
  else if (sv.q2 === "B" && cover) m++;
  if (sv.q3 === "A" && I >= E) m++;
  else if (sv.q3 === "B" && E >= I) m++;
  return m;
}

function buildAnalysisRows(
  profile: Profile,
  state: GameState,
  ending: string,
  lang: Lang,
) {
  const s = state.conflict["군인"] ?? 0;
  const h = state.conflict["인간"] ?? 0;
  const C = state.stats["용기"] ?? 0;
  const G = state.stats["죄책감"] ?? 0;
  const I = state.stats["인간본능"] ?? 0;
  const E = state.stats["공감"] ?? 0;
  const sv = profile.survey;
  const rows: {
    dim: string;
    pre: string;
    ingame: string;
    match: boolean;
  }[] = [];

  if (sv.q1) {
    const lean = s >= h ? ui("an_lean_s", lang) : ui("an_lean_h", lang);
    rows.push({
      dim: ui("an_q1dim", lang),
      pre: ui(sv.q1 === "A" ? "an_q1A" : "an_q1B", lang),
      ingame: ui("an_q1meas", lang, { s, h, lean }),
      match:
        (sv.q1 === "A" && s >= h) || (sv.q1 === "B" && h >= s),
    });
  }
  if (sv.q2) {
    const cover = ending === "BAD" || G >= 60 || C < 60;
    rows.push({
      dim: ui("an_q2dim", lang),
      pre: ui(sv.q2 === "A" ? "an_q2A" : "an_q2B", lang),
      ingame: ui("an_q2meas", lang, { c: C, g: G, end: ending }),
      match:
        (sv.q2 === "A" && !cover) || (sv.q2 === "B" && cover),
    });
  }
  if (sv.q3) {
    const lean = I >= E ? ui("an_lean_i", lang) : ui("an_lean_e", lang);
    rows.push({
      dim: ui("an_q3dim", lang),
      pre: ui(sv.q3 === "A" ? "an_q3A" : "an_q3B", lang),
      ingame: ui("an_q3meas", lang, { i: I, e: E, lean }),
      match:
        (sv.q3 === "A" && I >= E) || (sv.q3 === "B" && E >= I),
    });
  }
  return rows;
}

export function GameClient() {
  const [lang, setLang] = useLang();
  const [phase, setPhase] = useState<Phase>("title");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [ending, setEnding] = useState<string>("NORMAL");
  const [finalState, setFinalState] = useState<GameState | null>(null);
  const [saveMsg, setSaveMsg] = useState<string>("");
  const [continueSnap, setContinueSnap] = useState<EngineSnapshot | null>(null);
  const [matches, setMatches] = useState(0);

  const saveMeta = readSaveMeta();

  function handleCreated(p: Profile) {
    setProfile(p);
    setContinueSnap(null);
    setPhase("play");
  }

  function handleEnd(code: string, state: GameState) {
    setEnding(code);
    setFinalState(state);
    setPhase("final");
  }

  async function submitResult(
    state: GameState,
    p: Profile,
    code: string,
    m: number,
  ) {
    const payload = {
      name: p.name,
      gender: p.gender,
      grade: p.grade,
      major: p.major,
      mbti: p.mbti,
      q1: p.survey.q1 ?? "",
      q2: p.survey.q2 ?? "",
      q3: p.survey.q3 ?? "",
      ending: code,
      human: state.conflict["인간"] ?? 0,
      soldier: state.conflict["군인"] ?? 0,
      trust: state.stats["신뢰"] ?? 0,
      empathy: state.stats["공감"] ?? 0,
      instinct: state.stats["인간본능"] ?? 0,
      duty: state.stats["사회적역할"] ?? 0,
      guilt: state.stats["죄책감"] ?? 0,
      courage: state.stats["용기"] ?? 0,
      fragments: state.items.length,
      matches: m,
    };
    try {
      const res = await fetch("/api/results", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) setSaveMsg("saved");
      else setSaveMsg("skip");
    } catch {
      setSaveMsg("skip");
    }
  }

  if (phase === "title") {
    return (
      <TitleScreen
        lang={lang}
        setLang={setLang}
        hasSave={hasSave()}
        saveMeta={saveMeta}
        onNew={() => setPhase("create")}
        onContinue={() => {
          const snap = loadSnapshot();
          if (snap) {
            setProfile(snap.profile);
            setContinueSnap(snap);
            setPhase("play");
          }
        }}
      />
    );
  }

  if (phase === "create") {
    return (
      <CharacterCreator lang={lang} setLang={setLang} onDone={handleCreated} />
    );
  }

  if (phase === "play" && (profile || continueSnap)) {
    const p = profile ?? continueSnap!.profile;
    return (
      <PlayView
        lang={lang}
        setLang={setLang}
        profile={p}
        initialSnapshot={continueSnap}
        onEnd={handleEnd}
        onTitle={() => {
          setPhase("title");
          setProfile(null);
          setContinueSnap(null);
        }}
      />
    );
  }

  if (phase === "final" && profile && finalState) {
    return (
      <FinalQuestion
        lang={lang}
        onPick={() => {
          const m = computeMatches(profile, finalState, ending);
          setMatches(m);
          submitResult(finalState, profile, ending, m);
          deleteSave();
          setPhase("analysis");
        }}
      />
    );
  }

  if (phase === "analysis" && profile && finalState) {
    const rows = buildAnalysisRows(profile, finalState, ending, lang);
    const consistent = matches >= 2;
    return (
      <AnalysisScreen
        lang={lang}
        profile={profile}
        ending={ending}
        rows={rows}
        matches={matches}
        consistent={consistent}
        onDone={() => setPhase("result")}
      />
    );
  }

  if (phase === "result" && profile && finalState) {
    return (
      <ResultScreen
        lang={lang}
        setLang={setLang}
        profile={profile}
        state={finalState}
        ending={ending}
        saveMsg={saveMsg}
        matches={matches}
      />
    );
  }

  return null;
}

function TitleScreen({
  lang,
  setLang,
  hasSave: saved,
  saveMeta,
  onNew,
  onContinue,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  hasSave: boolean;
  saveMeta: { label: string; savedAt: number; name: string } | null;
  onNew: () => void;
  onContinue: () => void;
}) {
  return (
    <div className="relative min-h-screen bg-black text-stone-100 flex flex-col overflow-hidden">
      {/* '붉은 무공훈장'을 상징하는 움직이는 배경 (바람에 나부끼는 연출) */}
      <div className="absolute inset-0 overflow-hidden" aria-hidden>
        <Image
          src="/assets/title_bg.png"
          alt=""
          fill
          priority
          sizes="100vw"
          className="title-bg-wind object-cover"
        />
        {/* 흐르는 전장의 연기 */}
        <div className="absolute inset-0 title-bg-smoke bg-[radial-gradient(ellipse_at_50%_58%,rgba(205,205,215,0.14),transparent_62%)]" />
        {/* 은은히 맥동하는 핏빛 */}
        <div className="absolute inset-0 title-bg-blood bg-[radial-gradient(circle_at_28%_46%,rgba(150,22,22,0.55),transparent_52%)]" />
        {/* 가독성용 어둠 그라디언트 */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/35 to-black/90" />
      </div>

      <div className="relative z-10 flex justify-end px-6 py-4">
        <LangSelector lang={lang} setLang={setLang} />
      </div>
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 text-center gap-8">
        <div>
          <h1 className="font-serif text-4xl sm:text-5xl text-amber-100 tracking-wide drop-shadow-[0_2px_12px_rgba(0,0,0,0.9)]">
            {ui("title_main", lang)}
          </h1>
          <p className="mt-4 text-lg text-amber-200/80 font-serif tracking-widest drop-shadow-[0_2px_8px_rgba(0,0,0,0.9)]">
            The Weight of Courage
          </p>
          <p className="mt-6 text-xs text-stone-300/80 drop-shadow-[0_1px_6px_rgba(0,0,0,0.9)]">
            {ui("menu_credit", lang)}
          </p>
        </div>
        <div className="flex flex-col gap-3 w-full max-w-xs">
          <button
            type="button"
            onClick={onNew}
            className="rounded-full bg-amber-700 px-8 py-3.5 text-base font-medium hover:bg-amber-600 transition-colors shadow-lg shadow-amber-900/30"
          >
            {ui("menu_start", lang)}
          </button>
          {saved && saveMeta && (
            <button
              type="button"
              onClick={onContinue}
              className="rounded-full border border-amber-800/60 px-8 py-3 text-sm text-amber-200 hover:border-amber-600 hover:bg-amber-900/20 transition-colors"
            >
              {ui("menu_continue", lang)}
              <span className="block text-xs text-stone-500 mt-0.5">
                {saveMeta.name} · {saveMeta.label || "..."}
              </span>
            </button>
          )}
        </div>
        <Link
          href="/"
          className="text-xs text-stone-300/80 hover:text-amber-200 drop-shadow-[0_1px_6px_rgba(0,0,0,0.9)]"
        >
          ← 홈으로
        </Link>
      </main>
      <CreditsFooter className="relative z-10 bg-black/45 backdrop-blur-sm" />
    </div>
  );
}

function FinalQuestion({
  lang,
  onPick,
}: {
  lang: Lang;
  onPick: () => void;
}) {
  const opts = ["fq1", "fq2", "fq3", "fq4"];
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col items-center justify-center px-6">
      <div className="max-w-xl w-full">
        <h1 className="text-center font-serif text-2xl text-amber-100 mb-8">
          {ui("fq_title", lang)}
        </h1>
        <div className="space-y-3">
          {opts.map((k) => (
            <button
              key={k}
              type="button"
              onClick={onPick}
              className="w-full rounded-lg border border-amber-800/50 bg-stone-900 px-5 py-4 text-left text-base hover:border-amber-500 hover:bg-amber-900/30 transition-colors"
            >
              {ui(k, lang)}
            </button>
          ))}
        </div>
        <p className="mt-6 text-center text-xs text-stone-600">
          {ui("fq_note", lang)}
        </p>
      </div>
    </div>
  );
}

function AnalysisScreen({
  lang,
  profile,
  ending,
  rows,
  matches,
  consistent,
  onDone,
}: {
  lang: Lang;
  profile: Profile;
  ending: string;
  rows: { dim: string; pre: string; ingame: string; match: boolean }[];
  matches: number;
  consistent: boolean;
  onDone: () => void;
}) {
  return (
    <div
      className="min-h-screen bg-stone-950 text-stone-100 flex flex-col items-center justify-center px-6 cursor-pointer"
      onClick={onDone}
    >
      <div className="max-w-2xl w-full space-y-6">
        <div className="text-center">
          <h1 className="font-serif text-2xl text-amber-100">
            {ui("an_title", lang)}
          </h1>
          <p className="mt-2 text-sm text-stone-400">
            {profile.name} · {ui(profile.grade, lang)} · {profile.mbti}
          </p>
          <p className="mt-1 text-xs text-amber-600">
            {ui("an_ending", lang)}: {ui(`end_${ending}`, lang)}
          </p>
        </div>

        <div className="rounded-xl border border-stone-800 bg-stone-900 overflow-hidden">
          <div className="grid grid-cols-4 gap-2 px-4 py-2 bg-stone-800/50 text-xs text-stone-500">
            <span>{ui("an_pre", lang)}</span>
            <span className="col-span-2">{ui("an_ingame", lang)}</span>
            <span className="text-right">판정</span>
          </div>
          {rows.map((r, i) => (
            <div
              key={i}
              className="grid grid-cols-4 gap-2 px-4 py-3 border-t border-stone-800 text-sm"
            >
              <span className="text-amber-300 text-xs">{r.dim}</span>
              <span className="text-stone-400 text-xs">{r.pre}</span>
              <span className="text-stone-200 text-xs">{r.ingame}</span>
              <span
                className={`text-right text-xs font-medium ${r.match ? "text-emerald-400" : "text-orange-400"}`}
              >
                {r.match ? ui("an_match", lang) : ui("an_diff", lang)}
              </span>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-amber-800/40 bg-amber-900/10 p-5 text-center">
          <p className="text-sm text-amber-100 leading-relaxed">
            {consistent
              ? ui("an_sum_consistent", lang)
              : ui("an_sum_mixed", lang)}
          </p>
          <p className="mt-2 text-xs text-stone-500">
            {matches}/3 {ui("an_match", lang)}
          </p>
        </div>

        <p className="text-center text-xs text-stone-600 animate-pulse">
          {ui("an_footer", lang)}
        </p>
      </div>
    </div>
  );
}

function ResultScreen({
  lang,
  setLang,
  profile,
  state,
  ending,
  saveMsg,
  matches,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  profile: Profile;
  state: GameState;
  ending: string;
  saveMsg: string;
  matches: number;
}) {
  const stats: [string, number][] = [
    ["신뢰", state.stats["신뢰"] ?? 0],
    ["공감", state.stats["공감"] ?? 0],
    ["인간본능", state.stats["인간본능"] ?? 0],
    ["사회적역할", state.stats["사회적역할"] ?? 0],
    ["죄책감", state.stats["죄책감"] ?? 0],
    ["용기", state.stats["용기"] ?? 0],
  ];
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col">
      <div className="flex justify-end px-6 py-4">
        <LangSelector lang={lang} setLang={setLang} />
      </div>
      <div className="flex-1 max-w-xl w-full mx-auto px-6 pb-16 text-center">
        <p className="text-xs tracking-widest text-amber-600">ENDING</p>
        <h1 className="mt-2 font-serif text-3xl text-amber-100">
          {ui(`end_${ending}`, lang)}
        </h1>
        <p className="mt-4 text-sm text-stone-400">
          {profile.name} · {ui(profile.grade, lang)} · {ui(profile.major, lang)} ·{" "}
          {profile.mbti}
        </p>

        <div className="mt-8 rounded-xl border border-stone-800 bg-stone-900 p-6 text-left">
          <div className="grid grid-cols-2 gap-x-8 gap-y-3">
            {stats.map(([k, v]) => (
              <div key={k}>
                <div className="flex justify-between text-xs text-stone-400">
                  <span>{statLabel(k, lang)}</span>
                  <span>{v}</span>
                </div>
                <div className="h-1.5 rounded bg-stone-800 mt-1">
                  <div
                    className="h-1.5 rounded bg-amber-600"
                    style={{ width: `${v}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex justify-between text-xs text-stone-400 border-t border-stone-800 pt-3">
            <span>
              {ui("conflict_human", lang)} {state.conflict["인간"] ?? 0} /{" "}
              {ui("conflict_soldier", lang)} {state.conflict["군인"] ?? 0}
            </span>
            <span>
              {ui("frag_result", lang, {
                n: state.items.length,
                t: 5,
              })}
            </span>
          </div>
          <p className="mt-2 text-xs text-stone-500 text-center">
            {ui("an_match", lang)}: {matches}/3
          </p>
        </div>

        {saveMsg === "saved" && (
          <p className="mt-4 text-xs text-emerald-500">
            연구 데이터가 저장되었습니다.
          </p>
        )}
        {saveMsg === "skip" && (
          <p className="mt-4 text-xs text-stone-600">
            (Supabase 미설정: 배포 환경에서 결과가 자동 저장됩니다)
          </p>
        )}

        <div className="mt-8 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg bg-amber-700 px-6 py-2.5 text-sm font-medium hover:bg-amber-600"
          >
            {ui("menu_new", lang)}
          </button>
          <Link
            href="/"
            className="rounded-lg border border-stone-700 px-6 py-2.5 text-sm text-stone-300 hover:border-amber-800"
          >
            홈으로
          </Link>
        </div>
      </div>
      <CreditsFooter />
    </div>
  );
}
