"use client";

import { useState } from "react";
import Link from "next/link";
import { useLang } from "./useLang";
import { ui, t, statLabel, type Lang } from "./gameData";
import type { Profile } from "./profile";
import type { GameState } from "./engine";
import { CharacterCreator } from "./CharacterCreator";
import { PlayView } from "./PlayView";
import { LangSelector } from "./LangSelector";

type Phase = "create" | "play" | "final" | "result";

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

export function GameClient() {
  const [lang, setLang] = useLang();
  const [phase, setPhase] = useState<Phase>("create");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [ending, setEnding] = useState<string>("NORMAL");
  const [finalState, setFinalState] = useState<GameState | null>(null);
  const [saveMsg, setSaveMsg] = useState<string>("");

  function handleCreated(p: Profile) {
    setProfile(p);
    setPhase("play");
  }

  function handleEnd(code: string, state: GameState) {
    setEnding(code);
    setFinalState(state);
    setPhase("final");
  }

  async function submitResult(state: GameState, p: Profile, code: string) {
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
      matches: computeMatches(p, state, code),
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

  if (phase === "create") {
    return (
      <CharacterCreator lang={lang} setLang={setLang} onDone={handleCreated} />
    );
  }

  if (phase === "play" && profile) {
    return (
      <PlayView
        lang={lang}
        setLang={setLang}
        profile={profile}
        onEnd={handleEnd}
      />
    );
  }

  if (phase === "final" && profile && finalState) {
    return (
      <FinalQuestion
        lang={lang}
        onPick={() => {
          submitResult(finalState, profile, ending);
          setPhase("result");
        }}
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
      />
    );
  }

  return null;
}

function FinalQuestion({
  lang,
  onPick,
}: {
  lang: Lang;
  onPick: (v: string) => void;
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
              onClick={() => onPick(k)}
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

function ResultScreen({
  lang,
  setLang,
  profile,
  state,
  ending,
  saveMsg,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  profile: Profile;
  state: GameState;
  ending: string;
  saveMsg: string;
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
    <div className="min-h-screen bg-stone-950 text-stone-100">
      <div className="flex justify-end px-6 py-4">
        <LangSelector lang={lang} setLang={setLang} />
      </div>
      <div className="max-w-xl mx-auto px-6 pb-16 text-center">
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
                  <div className="h-1.5 rounded bg-amber-600" style={{ width: `${v}%` }} />
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
              {t("기억 조각", lang) ?? "기억 조각"} {state.items.length}/5
            </span>
          </div>
        </div>

        {saveMsg === "saved" && (
          <p className="mt-4 text-xs text-emerald-500">기록이 저장되었습니다.</p>
        )}
        {saveMsg === "skip" && (
          <p className="mt-4 text-xs text-stone-600">
            (로컬 미설정: 결과 저장은 배포 환경에서 활성화됩니다)
          </p>
        )}

        <div className="mt-8 flex justify-center gap-3">
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-lg bg-amber-700 px-6 py-2.5 text-sm font-medium hover:bg-amber-600"
          >
            다시 플레이
          </button>
          <Link
            href="/"
            className="rounded-lg border border-stone-700 px-6 py-2.5 text-sm text-stone-300 hover:border-amber-800"
          >
            홈으로
          </Link>
        </div>
      </div>
    </div>
  );
}
