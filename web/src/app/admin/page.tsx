"use client";

import { useState } from "react";
import Link from "next/link";
import { BASELINE, REFERENCE } from "@/lib/references";
import type { AnalysisReport } from "@/types/game";

interface AdminReport extends AnalysisReport {
  recentPlays?: Array<{
    name: string;
    gender: string;
    grade: string;
    mbti: string;
    ending: string;
    human: number;
    soldier: number;
    courage: number;
    empathy: number;
    fragments: number;
    matches: number;
    created_at?: string;
  }>;
}

function Bar({
  label,
  value,
  max = 100,
  color = "bg-amber-600",
}: {
  label: string;
  value: number;
  max?: number;
  color?: string;
}) {
  const w = max ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-stone-400">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 rounded bg-stone-800">
        <div
          className={`h-2 rounded ${color}`}
          style={{ width: `${w}%` }}
        />
      </div>
    </div>
  );
}

function Source({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs text-stone-500 italic border-l-2 border-amber-800 pl-3 mt-2">
      출처 · {children}
    </p>
  );
}

export default function AdminDashboard() {
  const [secret, setSecret] = useState("");
  const [report, setReport] = useState<AdminReport | null>(null);
  const [authed, setAuthed] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`/api/analyze?secret=${encodeURIComponent(secret)}`);
      if (!res.ok) {
        const j = await res.json().catch(() => ({}));
        if (res.status === 401) throw new Error("비밀번호가 올바르지 않습니다.");
        throw new Error(j.error || `HTTP ${res.status}`);
      }
      setReport(await res.json());
      setAuthed(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "로드 실패");
      setReport(null);
      setAuthed(false);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    setAuthed(false);
    setReport(null);
    setSecret("");
  }

  const d = report?.data;

  // ── 로그인 게이트 : 인증 전에는 대시보드를 노출하지 않는다 ──
  if (!authed) {
    return (
      <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col items-center justify-center px-6">
        <div className="w-full max-w-sm rounded-2xl border border-stone-800 bg-stone-900 p-8 space-y-6">
          <div className="text-center space-y-1">
            <p className="text-xs text-amber-600 tracking-[0.3em]">ADMIN ONLY</p>
            <h1 className="text-lg font-serif text-amber-100">관리자 분석 접속</h1>
            <p className="text-xs text-stone-500 pt-1">
              연구·발표 담당자 전용 페이지입니다.
            </p>
          </div>
          <form
            className="space-y-3"
            onSubmit={(e) => {
              e.preventDefault();
              load();
            }}
          >
            <input
              type="password"
              autoFocus
              placeholder="관리자 비밀번호"
              value={secret}
              onChange={(e) => setSecret(e.target.value)}
              className="w-full rounded-lg border border-stone-700 bg-stone-950 px-4 py-3 text-sm outline-none focus:border-amber-700"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-amber-700 px-4 py-3 text-sm font-medium hover:bg-amber-600 disabled:opacity-50"
            >
              {loading ? "확인 중…" : "접속"}
            </button>
          </form>
          {error && <p className="text-sm text-red-400 text-center">{error}</p>}
        </div>
        <Link
          href="/"
          className="mt-6 text-xs text-stone-600 hover:text-stone-400"
        >
          ← 게임 홈으로
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-950 text-stone-100">
      <header className="border-b border-stone-800 px-6 py-4 flex items-center justify-between">
        <div>
          <p className="text-xs text-amber-600 tracking-widest">ADMIN</p>
          <h1 className="text-xl font-serif text-amber-100">
            학술 비교 분석 대시보드
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <button
            type="button"
            onClick={load}
            disabled={loading}
            className="text-sm text-stone-300 hover:text-amber-200 disabled:opacity-50"
          >
            {loading ? "새로고침 중…" : "새로고침"}
          </button>
          <button
            type="button"
            onClick={logout}
            className="text-sm text-stone-500 hover:text-red-300"
          >
            로그아웃
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {report && (
          <p className="text-xs text-stone-500">
            데이터: {report.source} · 표본 n = {report.sampleSize} ·{" "}
            {new Date(report.generatedAt).toLocaleString("ko-KR")}
          </p>
        )}
        {error && <p className="text-sm text-red-400">{error}</p>}

        {d && (
          <>
            <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatBox label="표본 n" value={String(report!.sampleSize)} />
              <StatBox label="진엔딩 비율" value={`${d.goodEndingPct}%`} />
              <StatBox
                label="공감(Q1 B)"
                value={`${d.model1.empathyPct}%`}
              />
              <StatBox
                label="이타심(Q3 B)"
                value={`${d.model3.altruismPct}%`}
              />
            </section>

            {/* 엔딩 분포 */}
            {d.endingDistribution.length > 0 && (
              <ModelCard title="엔딩 분포">
                <div className="space-y-2">
                  {d.endingDistribution.map((e) => (
                    <Bar
                      key={e.code}
                      label={`${e.code} (${e.count}건)`}
                      value={e.pct}
                      color={
                        ["TRUE", "GOOD", "HIDDEN"].includes(e.code)
                          ? "bg-emerald-700"
                          : e.code === "BAD"
                            ? "bg-red-800"
                            : "bg-amber-700"
                      }
                    />
                  ))}
                </div>
              </ModelCard>
            )}

            <ModelCard title="① 콜버그 · 길리건 — 원칙 vs 공감">
              <Insight
                baseline={BASELINE.model1Principle}
                ours={d.model1.principlePct}
                label="원칙(A) 비율"
                higherIsBaseline
              />
              <Bar
                label={`기존 통계 · 규칙 우선 ≈ ${BASELINE.model1Principle}%`}
                value={BASELINE.model1Principle}
                color="bg-stone-500"
              />
              <Bar
                label={`우리 데이터 · 원칙(A) n=${d.model1.n}`}
                value={d.model1.principlePct}
                color="bg-sky-700"
              />
              <Bar
                label="우리 데이터 · 공감(B)"
                value={d.model1.empathyPct}
                color="bg-emerald-700"
              />
              <p className="text-xs text-stone-400">
                평균 저울 — 인간 {d.model1.avgHuman} · 군인 {d.model1.avgSoldier}
              </p>
              <Hypothesis text={REFERENCE.model1.hypothesis} />
              <Source>
                {REFERENCE.model1.baselines[0].source}
              </Source>
            </ModelCard>

            <ModelCard title="② MBTI T vs F — 엔딩 · 용기">
              <Bar
                label={`기존 · 남성 T선호 ${BASELINE.model2MaleT}%`}
                value={BASELINE.model2MaleT}
                color="bg-stone-500"
              />
              <Bar
                label={`우리 · T형 진엔딩 (n=${d.model2.tN})`}
                value={d.model2.tGoodEndingPct}
                color="bg-sky-700"
              />
              <Bar
                label={`우리 · F형 진엔딩 (n=${d.model2.fN})`}
                value={d.model2.fGoodEndingPct}
                color="bg-emerald-700"
              />
              <p className="text-xs text-stone-400 mt-2">
                T형 평균 용기 {d.model2.tAvgCourage} · F형 평균 용기{" "}
                {d.model2.fAvgCourage}
              </p>
              <Hypothesis text={REFERENCE.model2.hypothesis} />
              <Source>{REFERENCE.model2.baselines[0].source}</Source>
            </ModelCard>

            <ModelCard title="③ 트롤리 · 행동경제학 — 이기심 vs 이타심">
              <Insight
                baseline={BASELINE.model3Dictator}
                ours={d.model3.altruismPct}
                label="이타심(B) 비율"
                higherIsBaseline={false}
              />
              <Bar
                label={`기존 · 독재자 게임 양보 ${BASELINE.model3Dictator}%`}
                value={BASELINE.model3Dictator}
                color="bg-stone-500"
              />
              <Bar
                label={`우리 · 이기심(A) n=${d.model3.n}`}
                value={d.model3.selfPct}
                color="bg-orange-800"
              />
              <Bar
                label="우리 · 이타심(B)"
                value={d.model3.altruismPct}
                color="bg-emerald-700"
              />
              <p className="text-xs text-stone-400">
                평균 인간본능 {d.model3.avgInstinct} · 공감 {d.model3.avgEmpathy} ·
                기억조각 {d.model3.avgFragments}
              </p>
              <Hypothesis text={REFERENCE.model3.hypothesis} />
              <Source>{REFERENCE.model3.baselines[2].source}</Source>
            </ModelCard>

            {/* 최근 플레이 기록 */}
            {report.recentPlays && report.recentPlays.length > 0 && (
              <section className="rounded-lg border border-stone-800 bg-stone-900 p-5 overflow-x-auto">
                <h2 className="font-serif text-lg text-amber-100 mb-4">
                  최근 플레이 기록 (최대 100건)
                </h2>
                <table className="w-full text-xs text-left">
                  <thead>
                    <tr className="text-stone-500 border-b border-stone-800">
                      <th className="py-2 pr-3">이름</th>
                      <th className="py-2 pr-3">MBTI</th>
                      <th className="py-2 pr-3">엔딩</th>
                      <th className="py-2 pr-3">인간/군인</th>
                      <th className="py-2 pr-3">용기</th>
                      <th className="py-2 pr-3">공감</th>
                      <th className="py-2 pr-3">조각</th>
                      <th className="py-2">일치</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.recentPlays.map((r, i) => (
                      <tr key={i} className="border-b border-stone-800/50 text-stone-300">
                        <td className="py-2 pr-3">{r.name}</td>
                        <td className="py-2 pr-3">{r.mbti}</td>
                        <td className="py-2 pr-3">
                          <span
                            className={
                              ["TRUE", "GOOD", "HIDDEN"].includes(r.ending)
                                ? "text-emerald-400"
                                : r.ending === "BAD"
                                  ? "text-red-400"
                                  : ""
                            }
                          >
                            {r.ending}
                          </span>
                        </td>
                        <td className="py-2 pr-3">
                          {r.human}/{r.soldier}
                        </td>
                        <td className="py-2 pr-3">{r.courage}</td>
                        <td className="py-2 pr-3">{r.empathy}</td>
                        <td className="py-2 pr-3">{r.fragments}</td>
                        <td className="py-2">{r.matches}/3</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            )}

            <section className="rounded-lg border border-stone-800 bg-stone-900 p-5">
              <h2 className="font-serif text-amber-100 mb-4">참고문헌</h2>
              <ul className="space-y-2 text-xs text-stone-400">
                {Object.values(REFERENCE).flatMap((m) =>
                  m.sources.map((s, i) => (
                    <li key={s}>
                      [{m.title.split(" ")[0]}] {s}
                    </li>
                  )),
                )}
              </ul>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-stone-800 bg-stone-900 p-4 text-center">
      <p className="text-2xl font-semibold text-amber-100">{value}</p>
      <p className="text-xs text-stone-500 mt-1">{label}</p>
    </div>
  );
}

function ModelCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-stone-800 bg-stone-900 p-5 space-y-4">
      <h2 className="font-serif text-lg text-amber-100">{title}</h2>
      {children}
    </section>
  );
}

function Hypothesis({ text }: { text: string }) {
  return (
    <div className="rounded-lg bg-amber-900/15 border border-amber-800/30 px-4 py-3 mt-2">
      <p className="text-xs text-amber-200/80 leading-relaxed">
        <span className="text-amber-500 font-medium">가설 · </span>
        {text}
      </p>
    </div>
  );
}

function Insight({
  baseline,
  ours,
  label,
  higherIsBaseline,
}: {
  baseline: number;
  ours: number;
  label: string;
  higherIsBaseline: boolean;
}) {
  const delta = Math.round((ours - baseline) * 10) / 10;
  const reversed = higherIsBaseline ? delta < 0 : delta > 0;
  const interesting = Math.abs(delta) >= 5;
  if (!interesting) return null;
  return (
    <p className="text-xs text-emerald-300 bg-emerald-900/20 border border-emerald-800/30 rounded px-3 py-2">
      {label}: 기준선 {baseline}% 대비 우리 {ours}% (차이 {delta > 0 ? "+" : ""}
      {delta}%)
      {reversed
        ? " — 기존 통계와 반대 경향이 관찰됩니다."
        : " — 기존 통계와 유사한 경향입니다."}
    </p>
  );
}
