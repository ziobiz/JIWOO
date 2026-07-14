"use client";

import { useCallback, useEffect, useState } from "react";
import type { Lang } from "@/game/gameData";
import {
  SURVEY_DIMS,
  SURVEY_VARIANT_COUNT,
  type SurveyDim,
} from "@/game/surveyVariants";
import {
  SURVEY_DIM_LABEL,
  type SurveyCopy,
  type SurveyVariant,
} from "@/lib/surveyCopy";

const LANGS: Lang[] = ["KR", "EN", "CH", "JP"];

/** 관리자 — 사전 성향 설문 (3유형 × 5변종 × A/B) 편집 */
export function SurveyCard({ secret }: { secret: string }) {
  const [survey, setSurvey] = useState<SurveyCopy | null>(null);
  const [defaults, setDefaults] = useState<SurveyCopy | null>(null);
  const [dim, setDim] = useState<SurveyDim>("q1");
  const [lang, setLang] = useState<Lang>("KR");
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "error">(
    "loading",
  );
  const [msg, setMsg] = useState("");

  const load = useCallback(async () => {
    setStatus("loading");
    try {
      const res = await fetch("/api/survey", { cache: "no-store" });
      const j = (await res.json()) as { survey: SurveyCopy; defaults: SurveyCopy };
      setSurvey(j.survey);
      setDefaults(j.defaults);
      setStatus("idle");
    } catch {
      setStatus("error");
      setMsg("사전 문의 문항을 불러오지 못했습니다.");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const patch = useCallback(
    (variantIdx: number, part: keyof SurveyVariant, value: string) => {
      setSurvey((prev) => {
        if (!prev) return prev;
        const next: SurveyCopy = {
          q1: [...prev.q1],
          q2: [...prev.q2],
          q3: [...prev.q3],
        };
        const list = [...next[dim]];
        const cur = { ...list[variantIdx] };
        cur[part] = { ...cur[part], [lang]: value };
        list[variantIdx] = cur;
        next[dim] = list;
        return next;
      });
    },
    [dim, lang],
  );

  const save = useCallback(async () => {
    if (!survey) return;
    setStatus("saving");
    setMsg("");
    try {
      const res = await fetch(`/api/survey?secret=${encodeURIComponent(secret)}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "x-admin-secret": secret,
        },
        body: JSON.stringify({ survey }),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j.error || `HTTP ${res.status}`);
      setSurvey(j.survey ?? survey);
      setStatus("saved");
      setMsg("저장되었습니다. 새 플레이부터 반영됩니다.");
      setTimeout(() => setStatus("idle"), 2500);
    } catch (e) {
      setStatus("error");
      setMsg(e instanceof Error ? e.message : "저장 실패");
    }
  }, [secret, survey]);

  const resetDefaults = useCallback(() => {
    if (!defaults) return;
    setSurvey(structuredClone(defaults));
  }, [defaults]);

  if (status === "loading" || !survey) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        사전 문의 문항을 불러오는 중…
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <div className="rounded-xl border border-slate-200 bg-white p-5 space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-slate-900">사전 문의</h2>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              성향 설문 3유형 × 변종 5개 · 각 문항은 질문과 선택지 A/B 입니다.
              A/B 의미(원칙·진실·자기 / 공감·명예·이타)는 분석과 연결되므로 의미를 바꾸지 마세요.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={resetDefaults}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-50"
            >
              기본값으로
            </button>
            <button
              type="button"
              onClick={save}
              disabled={status === "saving"}
              className="rounded-lg bg-sky-700 px-4 py-1.5 text-xs font-medium text-white hover:bg-sky-600 disabled:opacity-50"
            >
              {status === "saving" ? "저장 중…" : "저장"}
            </button>
          </div>
        </div>
        {msg && (
          <p
            className={`text-xs ${
              status === "error" ? "text-rose-600" : "text-emerald-700"
            }`}
          >
            {msg}
          </p>
        )}

        <div className="flex flex-wrap gap-2">
          {SURVEY_DIMS.map((d) => (
            <button
              key={d}
              type="button"
              onClick={() => setDim(d)}
              className={`rounded-full px-3 py-1 text-xs font-medium border ${
                dim === d
                  ? "border-sky-600 bg-sky-50 text-sky-800"
                  : "border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              {SURVEY_DIM_LABEL[d]}
            </button>
          ))}
        </div>

        <div className="flex gap-1 border-b border-slate-200">
          {LANGS.map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => setLang(l)}
              className={`px-3 py-1.5 text-xs font-medium border-b-2 -mb-px ${
                lang === l
                  ? "border-sky-600 text-sky-800"
                  : "border-transparent text-slate-500 hover:text-slate-700"
              }`}
            >
              {l}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {Array.from({ length: SURVEY_VARIANT_COUNT }, (_, i) => {
          const v = survey[dim][i];
          return (
            <article
              key={`${dim}-${i}`}
              className="rounded-xl border border-slate-200 bg-white p-5 space-y-3"
            >
              <p className="text-[11px] font-semibold tracking-wide text-amber-700">
                변종 {i + 1} / {SURVEY_VARIANT_COUNT}
              </p>
              <label className="block space-y-1">
                <span className="text-xs text-slate-500">질문</span>
                <textarea
                  value={v.t[lang]}
                  onChange={(e) => patch(i, "t", e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500"
                />
              </label>
              <div className="grid sm:grid-cols-2 gap-3">
                <label className="block space-y-1">
                  <span className="text-xs font-medium text-sky-800">선택지 A</span>
                  <textarea
                    value={v.a[lang]}
                    onChange={(e) => patch(i, "a", e.target.value)}
                    rows={2}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500"
                  />
                </label>
                <label className="block space-y-1">
                  <span className="text-xs font-medium text-amber-800">선택지 B</span>
                  <textarea
                    value={v.b[lang]}
                    onChange={(e) => patch(i, "b", e.target.value)}
                    rows={2}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500"
                  />
                </label>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
