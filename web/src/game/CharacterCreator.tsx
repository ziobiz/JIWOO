"use client";

import { useState } from "react";
import Image from "next/image";
import { GAME, ui, portraitSrc, type Lang } from "./gameData";
import { NAME_MAX } from "./useLang";
import { defaultProfile, type Profile } from "./profile";
import { LangSelector } from "./LangSelector";

const C = GAME.constants;

function OptionRow({
  keys,
  value,
  onPick,
  lang,
  cols = 4,
}: {
  keys: string[];
  value: string;
  onPick: (k: string) => void;
  lang: Lang;
  cols?: number;
}) {
  return (
    <div className="grid gap-2" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0,1fr))` }}>
      {keys.map((k) => (
        <button
          key={k}
          type="button"
          onClick={() => onPick(k)}
          className={`rounded-lg border px-2 py-2 text-sm transition-colors ${
            value === k
              ? "border-amber-600 bg-amber-700/30 text-amber-100"
              : "border-stone-700 bg-stone-900 text-stone-300 hover:border-stone-500"
          }`}
        >
          {ui(k, lang)}
        </button>
      ))}
    </div>
  );
}

export function CharacterCreator({
  lang,
  setLang,
  onDone,
}: {
  lang: Lang;
  setLang: (l: Lang) => void;
  onDone: (p: Profile) => void;
}) {
  const [profile, setProfile] = useState<Profile>(defaultProfile());
  const [phase, setPhase] = useState<"info" | "survey">("info");
  const [surveyIdx, setSurveyIdx] = useState(0);
  const [error, setError] = useState("");

  const upd = (patch: Partial<Profile>) => setProfile((p) => ({ ...p, ...patch }));

  function randomize() {
    const pick = <T,>(arr: T[]) => arr[Math.floor(Math.random() * arr.length)];
    upd({
      portrait: 1 + Math.floor(Math.random() * C.portraitCount),
      gender: pick(C.genderKeys),
      grade: pick(C.gradeKeys),
      major: pick(C.majorKeys),
      mbti: pick(C.mbtiTypes),
    });
  }

  function toSurvey() {
    if (!profile.name.trim()) {
      setError(ui("cc_need_name", lang));
      return;
    }
    setError("");
    setPhase("survey");
  }

  const surveyKeys = ["q1", "q2", "q3"] as const;
  const qk = surveyKeys[surveyIdx];
  const answer = profile.survey[qk];

  function pickAnswer(v: "A" | "B") {
    const next = { ...profile.survey, [qk]: v };
    upd({ survey: next });
    if (surveyIdx < 2) {
      setSurveyIdx((i) => i + 1);
    } else {
      onDone({ ...profile, survey: next });
    }
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100">
      <div className="flex justify-end px-6 py-4">
        <LangSelector lang={lang} setLang={setLang} />
      </div>

      {phase === "info" && (
        <div className="max-w-4xl mx-auto px-6 pb-16">
          <div className="text-center mb-8">
            <h1 className="text-2xl font-serif text-amber-100">
              {ui("cc_title", lang)}
            </h1>
            <p className="text-sm text-stone-500 mt-1">{ui("cc_subtitle", lang)}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* 초상 선택 */}
            <div>
              <p className="text-sm text-amber-200 mb-3">{ui("cc_portrait", lang)}</p>
              <div className="grid grid-cols-4 gap-2">
                {Array.from({ length: C.portraitCount }, (_, i) => i + 1).map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => upd({ portrait: n })}
                    className={`relative aspect-[3/4] overflow-hidden rounded-lg border-2 transition-all ${
                      profile.portrait === n
                        ? "border-amber-500 ring-2 ring-amber-600/50"
                        : "border-stone-700 opacity-70 hover:opacity-100"
                    }`}
                  >
                    <Image
                      src={portraitSrc(n)}
                      alt={`portrait ${n}`}
                      fill
                      sizes="120px"
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            </div>

            {/* 정보 입력 */}
            <div className="space-y-4">
              <div>
                <label className="text-sm text-amber-200">{ui("cc_name", lang)}</label>
                <input
                  type="text"
                  maxLength={NAME_MAX[lang]}
                  value={profile.name}
                  placeholder={ui("cc_name_ph", lang, { n: NAME_MAX[lang] })}
                  onChange={(e) => upd({ name: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-sm outline-none focus:border-amber-600"
                />
                <p className="text-xs text-stone-600 mt-1">
                  {ui("cc_hint", lang)} · {NAME_MAX[lang]}
                </p>
              </div>

              <div>
                <label className="text-sm text-amber-200">{ui("cc_gender", lang)}</label>
                <div className="mt-1">
                  <OptionRow keys={C.genderKeys} value={profile.gender} onPick={(k) => upd({ gender: k })} lang={lang} cols={3} />
                </div>
              </div>

              <div>
                <label className="text-sm text-amber-200">{ui("cc_grade", lang)}</label>
                <div className="mt-1">
                  <OptionRow keys={C.gradeKeys} value={profile.grade} onPick={(k) => upd({ grade: k })} lang={lang} cols={3} />
                </div>
              </div>

              <div>
                <label className="text-sm text-amber-200">{ui("cc_major", lang)}</label>
                <div className="mt-1">
                  <OptionRow keys={C.majorKeys} value={profile.major} onPick={(k) => upd({ major: k })} lang={lang} cols={4} />
                </div>
              </div>

              <div>
                <label className="text-sm text-amber-200">{ui("cc_mbti", lang)}</label>
                <select
                  value={profile.mbti}
                  onChange={(e) => upd({ mbti: e.target.value })}
                  className="mt-1 w-full rounded-lg border border-stone-700 bg-stone-900 px-3 py-2 text-sm outline-none focus:border-amber-600"
                >
                  {C.mbtiTypes.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {error && <p className="text-sm text-red-400 text-center mt-4">{error}</p>}

          <div className="flex justify-center gap-3 mt-8">
            <button
              type="button"
              onClick={randomize}
              className="rounded-lg border border-stone-700 px-5 py-2.5 text-sm text-stone-300 hover:border-amber-800"
            >
              {ui("cc_random", lang)}
            </button>
            <button
              type="button"
              onClick={toSurvey}
              className="rounded-lg bg-amber-700 px-8 py-2.5 text-sm font-medium hover:bg-amber-600"
            >
              {ui("cc_next", lang)}
            </button>
          </div>
        </div>
      )}

      {phase === "survey" && (
        <div className="max-w-2xl mx-auto px-6 pb-16">
          <div className="text-center mb-8">
            <p className="text-xs tracking-widest text-amber-600">
              {surveyIdx + 1} / 3
            </p>
            <h1 className="text-xl font-serif text-amber-100 mt-2">
              {ui("cc_subtitle", lang)}
            </h1>
          </div>

          <div className="rounded-xl border border-stone-800 bg-stone-900 p-6">
            <p className="text-base leading-relaxed text-stone-200 mb-6">
              {ui(`${qk}_t`, lang)}
            </p>
            <div className="space-y-3">
              {(["A", "B"] as const).map((v) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => pickAnswer(v)}
                  className={`w-full rounded-lg border px-4 py-3 text-left text-sm transition-colors ${
                    answer === v
                      ? "border-amber-600 bg-amber-700/30"
                      : "border-stone-700 bg-stone-950 hover:border-stone-500"
                  }`}
                >
                  <span className="text-amber-400 font-medium mr-2">{v}.</span>
                  {ui(`${qk}_${v.toLowerCase()}`, lang)}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-between mt-6">
            <button
              type="button"
              onClick={() => (surveyIdx > 0 ? setSurveyIdx((i) => i - 1) : setPhase("info"))}
              className="text-sm text-stone-500 hover:text-stone-300"
            >
              ← {ui("cc_prev", lang)}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
