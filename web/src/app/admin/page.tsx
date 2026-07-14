"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { BASELINE, REFERENCE } from "@/lib/references";
import type { AnalysisReport, PlayResult } from "@/types/game";
import {
  byGender,
  byGrade,
  byMajor,
  byMbtiTF,
  byMbtiType,
  label,
  type GroupStat,
} from "@/lib/breakdown";
import { exportExcel, exportPptx, type AnalysisBundle } from "@/lib/exporters";
import { modelInsights } from "@/lib/interpret";
import { useBranding } from "@/lib/useBranding";
import { ChartBoard, type Series, type Slice } from "./Charts";
import { QRCard } from "./QRCard";
import { BrandCard } from "./BrandCard";

interface AdminReport extends AnalysisReport {
  rows?: PlayResult[];
  envStatus?: {
    url: boolean;
    anonKey: boolean;
    serviceRole: boolean;
    adminSecret: boolean;
    configured: boolean;
    error: string | null;
  };
}

type ViewMode = "both" | "chart" | "table";
type AdminPanel = "data" | "analysis" | "brand" | "qr";

type DeletePending =
  | { mode: "selected"; ids: string[]; step: 1 | 2 }
  | { mode: "all"; step: 1 | 2 }
  | { mode: "one"; ids: string[]; label: string; step: 1 | 2 };

const CHART = {
  baseline: "#94a3b8",
  ours: "#0284c7",
  good: "#059669",
  principle: "#0284c7",
  altruism: "#d97706",
  self: "#f97316",
};

function endingColor(code: string): string {
  if (["TRUE", "GOOD", "HIDDEN"].includes(code)) return "#059669";
  if (code === "BAD") return "#e11d48";
  return "#f59e0b";
}

/* ── 재사용 UI ─────────────────────────────────────────── */

function Bar({
  label: lbl,
  value,
  max = 100,
  color = "bg-amber-600",
  suffix = "%",
}: {
  label: string;
  value: number;
  max?: number;
  color?: string;
  suffix?: string;
}) {
  const w = max ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-600">
        <span>{lbl}</span>
        <span className="font-medium text-slate-800">
          {value}
          {suffix}
        </span>
      </div>
      <div className="h-2.5 rounded-full bg-slate-100">
        <div className={`h-2.5 rounded-full ${color}`} style={{ width: `${w}%` }} />
      </div>
    </div>
  );
}

function Card({
  title,
  desc,
  children,
}: {
  title: string;
  desc?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm break-inside-avoid">
      <h2 className="font-semibold text-lg text-slate-900">{title}</h2>
      {desc && <p className="mt-0.5 text-xs text-slate-500">{desc}</p>}
      <div className="mt-4 space-y-3">{children}</div>
    </section>
  );
}

function StatBox({ label: lbl, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 text-center shadow-sm">
      <p className="text-3xl font-bold text-amber-700">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{lbl}</p>
    </div>
  );
}

function Source({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-3 border-l-2 border-amber-300 pl-3 text-xs italic text-slate-500">
      출처 · {children}
    </p>
  );
}

function Verdict({
  baseline,
  ours,
  label: lbl,
  higherIsBaseline,
}: {
  baseline: number;
  ours: number;
  label: string;
  higherIsBaseline: boolean;
}) {
  const delta = Math.round((ours - baseline) * 10) / 10;
  const reversed = higherIsBaseline ? delta < 0 : delta > 0;
  return (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${
        Math.abs(delta) >= 5
          ? reversed
            ? "border-rose-200 bg-rose-50 text-rose-700"
            : "border-emerald-200 bg-emerald-50 text-emerald-700"
          : "border-slate-200 bg-slate-50 text-slate-600"
      }`}
    >
      <b>{lbl}</b> — 기준선 {baseline}% 대비 우리 {ours}% (차이 {delta > 0 ? "+" : ""}
      {delta}%)
      {Math.abs(delta) >= 5
        ? reversed
          ? " · 기존 통계와 반대 경향"
          : " · 기존 통계와 유사 경향"
        : " · 유의미한 차이 없음"}
    </div>
  );
}

function GroupTable({
  title,
  desc,
  stats,
  view,
}: {
  title: string;
  desc?: string;
  stats: GroupStat[];
  view: ViewMode;
}) {
  const maxN = Math.max(1, ...stats.map((s) => s.n));
  const categories = stats.map((s) => s.label);
  const series: Series[] = [
    { name: "진엔딩%", color: CHART.good, values: stats.map((s) => s.goodEndingPct) },
    { name: "원칙(Q1A)%", color: CHART.principle, values: stats.map((s) => s.principlePct) },
    { name: "이타심(Q3B)%", color: CHART.altruism, values: stats.map((s) => s.altruismPct) },
  ];
  return (
    <Card title={title} desc={desc}>
      {view !== "table" && (
        <ChartBoard context="comparison" categories={categories} series={series} />
      )}
      {view !== "chart" && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs text-slate-500">
                <th className="py-2 pr-3">구분</th>
                <th className="py-2 pr-3">표본</th>
                <th className="py-2 pr-3">진엔딩%</th>
                <th className="py-2 pr-3">원칙(Q1A)%</th>
                <th className="py-2 pr-3">이타심(Q3B)%</th>
                <th className="py-2 pr-3">평균 용기</th>
                <th className="py-2 pr-3">평균 공감</th>
                <th className="py-2">평균 일치</th>
              </tr>
            </thead>
            <tbody>
              {stats.map((s) => (
                <tr key={s.key} className="border-b border-slate-100 text-slate-700">
                  <td className="py-2 pr-3 font-medium text-slate-900">{s.label}</td>
                  <td className="py-2 pr-3">
                    <span className="inline-flex items-center gap-2">
                      {s.n}
                      <span className="hidden sm:inline-block h-1.5 w-16 rounded-full bg-slate-100">
                        <span
                          className="block h-1.5 rounded-full bg-sky-400"
                          style={{ width: `${(s.n / maxN) * 100}%` }}
                        />
                      </span>
                    </span>
                  </td>
                  <td className="py-2 pr-3">{s.goodEndingPct}</td>
                  <td className="py-2 pr-3">{s.principlePct}</td>
                  <td className="py-2 pr-3">{s.altruismPct}</td>
                  <td className="py-2 pr-3">{s.avgCourage}</td>
                  <td className="py-2 pr-3">{s.avgEmpathy}</td>
                  <td className="py-2">{s.avgMatches}/3</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}

/* ── 삭제 이중 확인 모달 ─────────────────────────────────── */

function DeleteConfirmModal({
  pending,
  busy,
  onCancel,
  onNext,
  onFinal,
}: {
  pending: DeletePending;
  busy: boolean;
  onCancel: () => void;
  onNext: () => void;
  onFinal: () => void;
}) {
  const count =
    pending.mode === "all"
      ? "전체"
      : pending.mode === "one"
        ? "1"
        : String(pending.ids.length);
  const target =
    pending.mode === "all"
      ? "수집된 모든 플레이 데이터"
      : pending.mode === "one"
        ? `"${pending.label}" 데이터`
        : `선택한 ${pending.ids.length}건`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 no-print">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl space-y-4">
        <p className="text-[10px] tracking-widest text-rose-500 font-semibold">
          {pending.step === 1 ? "1차 확인" : "2차 최종 확인"}
        </p>
        {pending.step === 1 ? (
          <>
            <h3 className="text-lg font-semibold text-slate-900">삭제할까요?</h3>
            <p className="text-sm text-slate-600 leading-relaxed">
              {target}을(를) 삭제합니다. 다음 단계에서 한 번 더 확인합니다.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onCancel}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
              >
                취소
              </button>
              <button
                type="button"
                onClick={onNext}
                className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white hover:bg-rose-500"
              >
                다음 (2차 확인)
              </button>
            </div>
          </>
        ) : (
          <>
            <h3 className="text-lg font-semibold text-slate-900">정말 삭제합니까?</h3>
            <p className="text-sm text-rose-700 leading-relaxed rounded-lg border border-rose-200 bg-rose-50 px-3 py-2">
              {count === "전체" ? "모든" : `${count}건의`} 데이터가 영구 삭제되며{" "}
              <b>되돌릴 수 없습니다</b>. 계속하려면 &quot;최종 삭제&quot;를 누르세요.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onCancel}
                disabled={busy}
                className="rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                취소
              </button>
              <button
                type="button"
                onClick={onFinal}
                disabled={busy}
                className="rounded-lg bg-rose-700 px-4 py-2 text-sm font-medium text-white hover:bg-rose-600 disabled:opacity-40"
              >
                {busy ? "삭제 중…" : "최종 삭제"}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ── 페이지 ─────────────────────────────────────────────── */

export default function AdminDashboard() {
  const [secret, setSecret] = useState("");
  const [report, setReport] = useState<AdminReport | null>(null);
  const [authed, setAuthed] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [view, setView] = useState<ViewMode>("both");
  const [panel, setPanel] = useState<AdminPanel>("data");
  const [pending, setPending] = useState<DeletePending | null>(null);

  const rows = useMemo(() => report?.rows ?? [], [report]);
  const grade = useMemo(() => byGrade(rows), [rows]);
  const gender = useMemo(() => byGender(rows), [rows]);
  const major = useMemo(() => byMajor(rows), [rows]);
  const mbtiTF = useMemo(() => byMbtiTF(rows), [rows]);
  const mbtiType = useMemo(() => byMbtiType(rows), [rows]);
  const insights = useMemo(
    () => (report?.data ? modelInsights(report.data, report.sampleSize) : null),
    [report],
  );

  const scatterPoints = useMemo(
    () =>
      rows.map((r) => ({
        x: r.courage,
        y: r.empathy,
        label: `${r.name} · ${r.ending}`,
        color: endingColor(r.ending),
      })),
    [rows],
  );

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
      setSelected(new Set());
      setPanel("data");
    } catch (e) {
      setError(e instanceof Error ? e.message : "로드 실패");
      setReport(null);
      setAuthed(false);
    } finally {
      setLoading(false);
    }
  }

  function bundle(): AnalysisBundle {
    return { report: report!, rows, grade, gender, major, mbtiTF, mbtiType };
  }

  async function doExcel() {
    setBusy("excel");
    try {
      await exportExcel(bundle());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Excel 생성 실패");
    } finally {
      setBusy("");
    }
  }

  async function doPptx() {
    setBusy("pptx");
    try {
      await exportPptx(bundle());
    } catch (e) {
      setError(e instanceof Error ? e.message : "PPT 생성 실패");
    } finally {
      setBusy("");
    }
  }

  async function del(payload: { all?: boolean; ids?: string[] }) {
    setBusy("delete");
    setError("");
    try {
      const res = await fetch(`/api/results?secret=${encodeURIComponent(secret)}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j.error || `HTTP ${res.status}`);
      setPending(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "삭제 실패");
    } finally {
      setBusy("");
    }
  }

  function requestDeleteSelected() {
    const ids = [...selected].filter(Boolean);
    if (!ids.length) return;
    setPending({ mode: "selected", ids, step: 1 });
  }

  function requestDeleteAll() {
    if (!rows.length) return;
    setPending({ mode: "all", step: 1 });
  }

  function requestDeleteOne(r: PlayResult) {
    if (!r.id) return;
    setPending({
      mode: "one",
      ids: [r.id],
      label: `${r.name || "無名"} · ${r.ending}`,
      step: 1,
    });
  }

  function confirmFinalDelete() {
    if (!pending || pending.step !== 2) return;
    if (pending.mode === "all") del({ all: true });
    else del({ ids: pending.ids });
  }

  function toggle(id?: string) {
    if (!id) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleAll() {
    if (selected.size === rows.filter((r) => r.id).length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(rows.map((r) => r.id).filter(Boolean) as string[]));
    }
  }

  const d = report?.data;

  /* ── 로그인 게이트 ── */
  if (!authed) {
    return (
      <div className="relative min-h-screen bg-slate-50 text-slate-800 flex flex-col items-center justify-center px-6 pb-24">
        <div className="w-full max-w-sm rounded-2xl border border-slate-200 bg-white p-8 shadow-sm space-y-6">
          <div className="text-center space-y-1">
            <p className="text-xs text-amber-600 tracking-[0.3em]">ADMIN ONLY</p>
            <h1 className="text-lg font-semibold text-slate-900">관리자 분석 접속</h1>
            <p className="text-xs text-slate-500 pt-1">연구·발표 담당자 전용 페이지입니다.</p>
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
              className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none focus:border-amber-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-amber-600 px-4 py-3 text-sm font-medium text-white hover:bg-amber-500 disabled:opacity-50"
            >
              {loading ? "확인 중…" : "접속"}
            </button>
          </form>
          {error && <p className="text-sm text-rose-500 text-center">{error}</p>}
        </div>
        <Link href="/" className="mt-6 text-xs text-slate-500 hover:text-slate-700">
          ← 게임 홈으로
        </Link>
        <CreditsFooter className="absolute bottom-0 inset-x-0" light />
      </div>
    );
  }

  const nav: [AdminPanel, string][] = [
    ["data", "데이터 목록"],
    ["analysis", "분석 · 그래프"],
    ["brand", "브랜드"],
    ["qr", "QR 배포"],
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 print:bg-white">
      {pending && (
        <DeleteConfirmModal
          pending={pending}
          busy={busy === "delete"}
          onCancel={() => setPending(null)}
          onNext={() => setPending({ ...pending, step: 2 })}
          onFinal={confirmFinalDelete}
        />
      )}

      <header className="no-print sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur px-6 py-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-[10px] text-amber-600 tracking-widest">ADMIN</p>
          <h1 className="text-lg font-semibold text-slate-900">학술 비교 분석 대시보드</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg border border-slate-300 overflow-hidden">
            {nav.map(([p, lbl]) => (
              <button
                key={p}
                type="button"
                onClick={() => setPanel(p)}
                className={`px-3 py-1.5 text-sm transition-colors ${
                  panel === p
                    ? "bg-amber-600 text-white"
                    : "bg-white text-slate-600 hover:bg-slate-100"
                }`}
              >
                {lbl}
              </button>
            ))}
          </div>

          {panel === "analysis" && (
            <div className="inline-flex rounded-lg border border-slate-300 overflow-hidden">
              {(
                [
                  ["both", "표+그래프"],
                  ["chart", "그래프"],
                  ["table", "표"],
                ] as [ViewMode, string][]
              ).map(([v, lbl]) => (
                <button
                  key={v}
                  type="button"
                  onClick={() => setView(v)}
                  className={`px-3 py-1.5 text-sm transition-colors ${
                    view === v
                      ? "bg-sky-600 text-white"
                      : "bg-white text-slate-600 hover:bg-slate-100"
                  }`}
                >
                  {lbl}
                </button>
              ))}
            </div>
          )}

          <ToolBtn onClick={() => window.print()}>PDF / 인쇄</ToolBtn>
          <ToolBtn onClick={doExcel} disabled={busy === "excel" || !d}>
            {busy === "excel" ? "생성 중…" : "Excel 내보내기"}
          </ToolBtn>
          <ToolBtn onClick={doPptx} disabled={busy === "pptx" || !d}>
            {busy === "pptx" ? "생성 중…" : "발표자료(PPT)"}
          </ToolBtn>
          <ToolBtn onClick={load} disabled={loading}>
            {loading ? "새로고침 중…" : "새로고침"}
          </ToolBtn>
          {panel === "data" && (
            <>
              <ToolBtn
                onClick={requestDeleteSelected}
                disabled={busy === "delete" || selected.size === 0}
                danger
              >
                선택 삭제 ({selected.size})
              </ToolBtn>
              <ToolBtn
                onClick={requestDeleteAll}
                disabled={busy === "delete" || rows.length === 0}
                danger
              >
                전체 삭제
              </ToolBtn>
            </>
          )}
          <button
            type="button"
            onClick={() => {
              setAuthed(false);
              setReport(null);
              setSecret("");
              setPanel("data");
            }}
            className="text-sm text-slate-400 hover:text-rose-500 px-2"
          >
            로그아웃
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        {report && (
          <p className="text-xs text-slate-500">
            데이터: {report.source} · 표본 n = {report.sampleSize} ·{" "}
            {new Date(report.generatedAt).toLocaleString("ko-KR")}
          </p>
        )}
        {report?.envStatus && !report.envStatus.configured && (
          <div className="rounded-xl border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-950 space-y-2">
            <p className="font-medium">플레이 결과가 DB에 저장되지 않고 있습니다</p>
            <p className="text-amber-900/90 text-xs leading-relaxed">
              원인: Vercel 환경변수에 Supabase URL/키가 <strong>없거나 값이 비어</strong> 있습니다.
              {report.envStatus.error ? ` (${report.envStatus.error})` : ""}
            </p>
            <ul className="text-xs text-amber-900/80 list-disc pl-4 space-y-1">
              <li>
                상태 — URL {report.envStatus.url ? "OK" : "없음"} · anon{" "}
                {report.envStatus.anonKey ? "OK" : "없음"} · service_role{" "}
                {report.envStatus.serviceRole ? "OK" : "없음"} · ADMIN_SECRET{" "}
                {report.envStatus.adminSecret ? "OK" : "없음"}
              </li>
              <li>
                Supabase → Project Settings → API 에서 Project URL, anon, service_role 복사
              </li>
              <li>
                Vercel → twc → Settings → Environment Variables 에 4개 다시 저장 후{" "}
                <strong>Redeploy</strong>
              </li>
              <li>
                또는 로컬 <code className="bg-amber-100 px-1 rounded">web/.env.local</code> 작성 후{" "}
                <code className="bg-amber-100 px-1 rounded">node scripts/push-env-vercel.mjs</code>
              </li>
            </ul>
          </div>
        )}
        {error && (
          <p className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-600">
            {error}
          </p>
        )}

        {/* ── 데이터 목록 (첫 화면) ── */}
        {panel === "data" && (
          <>
            {d && (
              <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <StatBox label="표본 n" value={String(report!.sampleSize)} />
                <StatBox label="진엔딩 비율" value={`${d.goodEndingPct}%`} />
                <StatBox label="공감(Q1 B)" value={`${d.model1.empathyPct}%`} />
                <StatBox label="이타심(Q3 B)" value={`${d.model3.altruismPct}%`} />
              </section>
            )}

            {rows.length === 0 ? (
              <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
                아직 수집된 플레이 데이터가 없습니다. 게임을 완료하면 결과가 이곳에 집계됩니다.
              </p>
            ) : (
              <Card
                title={`수집된 데이터 목록 (${rows.length}건)`}
                desc="체크 후 '선택 삭제', 행의 '삭제', 또는 '전체 삭제'로 정리합니다. 삭제는 이중 확인 후 실행됩니다."
              >
                <div className="no-print flex flex-wrap gap-2 mb-3">
                  <ToolBtn onClick={toggleAll}>
                    {selected.size === rows.filter((r) => r.id).length
                      ? "전체 선택 해제"
                      : "전체 선택"}
                  </ToolBtn>
                  <ToolBtn
                    onClick={requestDeleteSelected}
                    disabled={selected.size === 0}
                    danger
                  >
                    선택 삭제 ({selected.size})
                  </ToolBtn>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead>
                      <tr className="border-b border-slate-200 text-slate-500">
                        <th className="py-2 pr-2 no-print"></th>
                        <th className="py-2 pr-3">일시</th>
                        <th className="py-2 pr-3">이름</th>
                        <th className="py-2 pr-3">성별</th>
                        <th className="py-2 pr-3">학년</th>
                        <th className="py-2 pr-3">전공</th>
                        <th className="py-2 pr-3">MBTI</th>
                        <th className="py-2 pr-3">Q1/Q3</th>
                        <th className="py-2 pr-3">엔딩</th>
                        <th className="py-2 pr-3">인간/군인</th>
                        <th className="py-2 pr-3">용기</th>
                        <th className="py-2 pr-3">공감</th>
                        <th className="py-2 pr-3">조각</th>
                        <th className="py-2 pr-3">일치</th>
                        <th className="py-2 no-print">삭제</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r, i) => (
                        <tr key={r.id ?? i} className="border-b border-slate-100 text-slate-700">
                          <td className="py-1.5 pr-2 no-print">
                            <input
                              type="checkbox"
                              checked={r.id ? selected.has(r.id) : false}
                              onChange={() => toggle(r.id)}
                              disabled={!r.id}
                            />
                          </td>
                          <td className="py-1.5 pr-3 whitespace-nowrap">
                            {r.created_at
                              ? new Date(r.created_at).toLocaleString("ko-KR")
                              : "-"}
                          </td>
                          <td className="py-1.5 pr-3">{r.name}</td>
                          <td className="py-1.5 pr-3">{label(r.gender)}</td>
                          <td className="py-1.5 pr-3">{label(r.grade)}</td>
                          <td className="py-1.5 pr-3">{label(r.major)}</td>
                          <td className="py-1.5 pr-3">{r.mbti}</td>
                          <td className="py-1.5 pr-3">
                            {r.q1 || "-"}/{r.q3 || "-"}
                          </td>
                          <td className="py-1.5 pr-3">
                            <span
                              className={
                                ["TRUE", "GOOD", "HIDDEN"].includes(r.ending)
                                  ? "text-emerald-600 font-medium"
                                  : r.ending === "BAD"
                                    ? "text-rose-500 font-medium"
                                    : ""
                              }
                            >
                              {r.ending}
                            </span>
                          </td>
                          <td className="py-1.5 pr-3">
                            {r.human}/{r.soldier}
                          </td>
                          <td className="py-1.5 pr-3">{r.courage}</td>
                          <td className="py-1.5 pr-3">{r.empathy}</td>
                          <td className="py-1.5 pr-3">{r.fragments}</td>
                          <td className="py-1.5 pr-3">{r.matches}/3</td>
                          <td className="py-1.5 no-print">
                            <button
                              type="button"
                              disabled={!r.id || busy === "delete"}
                              onClick={() => requestDeleteOne(r)}
                              className="rounded border border-rose-200 px-2 py-0.5 text-[11px] text-rose-600 hover:bg-rose-50 disabled:opacity-40"
                            >
                              삭제
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </>
        )}

        {/* ── 분석 · 그래프 ── */}
        {panel === "analysis" && d && (
          <>
            <p className="text-xs text-slate-500 rounded-lg border border-slate-200 bg-white px-4 py-2">
              지원 도식:{" "}
              <b>막대 그래프 (Bar Chart)</b> · <b>꺾은선 그래프 (Line Graph)</b> ·{" "}
              <b>원 그래프 (Pie Chart)</b> · <b>산점도 (Scatter Plot)</b>. 각 도식
              하단에서 데이터에 적합한 추천 2가지를 안내합니다.
            </p>

            <section className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatBox label="표본 n" value={String(report!.sampleSize)} />
              <StatBox label="진엔딩 비율" value={`${d.goodEndingPct}%`} />
              <StatBox label="공감(Q1 B)" value={`${d.model1.empathyPct}%`} />
              <StatBox label="이타심(Q3 B)" value={`${d.model3.altruismPct}%`} />
            </section>

            {d.endingDistribution.length > 0 && (
              <Card title="엔딩 분포">
                {view !== "table" && (
                  <ChartBoard
                    context="composition"
                    categories={d.endingDistribution.map((e) => e.code)}
                    series={[
                      {
                        name: "건수",
                        color: CHART.ours,
                        values: d.endingDistribution.map((e) => e.count),
                      },
                    ]}
                    slices={d.endingDistribution.map<Slice>((e) => ({
                      label: e.code,
                      value: e.count,
                      color: endingColor(e.code),
                    }))}
                    unit="건"
                  />
                )}
                {view !== "chart" &&
                  d.endingDistribution.map((e) => (
                    <Bar
                      key={e.code}
                      label={`${e.code} (${e.count}건)`}
                      value={e.pct}
                      color={
                        ["TRUE", "GOOD", "HIDDEN"].includes(e.code)
                          ? "bg-emerald-600"
                          : e.code === "BAD"
                            ? "bg-rose-500"
                            : "bg-amber-500"
                      }
                    />
                  ))}
              </Card>
            )}

            {scatterPoints.length > 0 && view !== "table" && (
              <Card
                title="산점도 · 용기 vs 공감"
                desc="개별 플레이어의 용기(X)–공감(Y) 분포. 색은 엔딩 코드."
              >
                <ChartBoard
                  context="correlation"
                  categories={["용기→공감"]}
                  series={[
                    {
                      name: "공감",
                      color: CHART.ours,
                      values: scatterPoints.map((p) => p.y),
                    },
                  ]}
                  scatter={{
                    points: scatterPoints,
                    xLabel: "용기",
                    yLabel: "공감",
                  }}
                  unit=""
                />
              </Card>
            )}

            <Card
              title="① 콜버그 · 길리건 — 원칙 vs 공감"
              desc="사전 설문 Q1 · 게임 내 '갈등의 저울'(군인 vs 인간)"
            >
              <Verdict
                baseline={BASELINE.model1Principle}
                ours={d.model1.principlePct}
                label="원칙(A) 비율"
                higherIsBaseline
              />
              {view !== "table" && (
                <ChartBoard
                  context="comparison"
                  categories={["원칙(A)", "공감(B)"]}
                  series={[
                    {
                      name: "기존 통계",
                      color: CHART.baseline,
                      values: [BASELINE.model1Principle, 100 - BASELINE.model1Principle],
                    },
                    {
                      name: "우리 데이터",
                      color: CHART.ours,
                      values: [d.model1.principlePct, d.model1.empathyPct],
                    },
                  ]}
                />
              )}
              {view !== "chart" && (
                <>
                  <Bar
                    label={`기존 통계 · 규칙 우선 ≈ ${BASELINE.model1Principle}%`}
                    value={BASELINE.model1Principle}
                    color="bg-slate-400"
                  />
                  <Bar
                    label={`우리 데이터 · 원칙(A) n=${d.model1.n}`}
                    value={d.model1.principlePct}
                    color="bg-sky-600"
                  />
                  <Bar
                    label="우리 데이터 · 공감(B)"
                    value={d.model1.empathyPct}
                    color="bg-emerald-600"
                  />
                </>
              )}
              <p className="text-xs text-slate-500">
                평균 저울 — 인간 {d.model1.avgHuman} · 군인 {d.model1.avgSoldier}
              </p>
              <Hypothesis text={REFERENCE.model1.hypothesis} />
              {insights && (
                <Analysis result={insights.m1.result} meaning={insights.m1.meaning} />
              )}
              <Source>{REFERENCE.model1.baselines[0].source}</Source>
            </Card>

            <Card
              title="② MBTI 사고형(T) vs 감정형(F) — 엔딩 · 용기"
              desc="MBTI 3번째 지표(T/F) · 도달 엔딩 · 용기 스탯"
            >
              {view !== "table" && (
                <ChartBoard
                  context="comparison"
                  categories={["T형", "F형"]}
                  series={[
                    {
                      name: "진엔딩%",
                      color: CHART.good,
                      values: [d.model2.tGoodEndingPct, d.model2.fGoodEndingPct],
                    },
                    {
                      name: "평균 용기",
                      color: CHART.ours,
                      values: [d.model2.tAvgCourage, d.model2.fAvgCourage],
                    },
                  ]}
                />
              )}
              {view !== "chart" && (
                <>
                  <Bar
                    label={`기존 · 남성 T선호 ${BASELINE.model2MaleT}%`}
                    value={BASELINE.model2MaleT}
                    color="bg-slate-400"
                  />
                  <Bar
                    label={`우리 · T형 진엔딩 (n=${d.model2.tN})`}
                    value={d.model2.tGoodEndingPct}
                    color="bg-sky-600"
                  />
                  <Bar
                    label={`우리 · F형 진엔딩 (n=${d.model2.fN})`}
                    value={d.model2.fGoodEndingPct}
                    color="bg-emerald-600"
                  />
                </>
              )}
              <p className="text-xs text-slate-500">
                T형 평균 용기 {d.model2.tAvgCourage} · F형 평균 용기 {d.model2.fAvgCourage}
              </p>
              <Hypothesis text={REFERENCE.model2.hypothesis} />
              {insights && (
                <Analysis result={insights.m2.result} meaning={insights.m2.meaning} />
              )}
              <Source>{REFERENCE.model2.baselines[0].source}</Source>
            </Card>

            <Card
              title="③ 트롤리 · 행동경제학 — 이기심 vs 이타심"
              desc="사전 설문 Q3 · 인간본능 vs 공감 · 기억 조각"
            >
              <Verdict
                baseline={BASELINE.model3Dictator}
                ours={d.model3.altruismPct}
                label="이타심(B) 비율"
                higherIsBaseline={false}
              />
              {view !== "table" && (
                <ChartBoard
                  context="composition"
                  categories={["이기심(A)", "이타심(B)"]}
                  series={[
                    {
                      name: "기존 통계",
                      color: CHART.baseline,
                      values: [100 - BASELINE.model3Dictator, BASELINE.model3Dictator],
                    },
                    {
                      name: "우리 데이터",
                      color: CHART.ours,
                      values: [d.model3.selfPct, d.model3.altruismPct],
                    },
                  ]}
                />
              )}
              {view !== "chart" && (
                <>
                  <Bar
                    label={`기존 · 독재자 게임 양보 ${BASELINE.model3Dictator}%`}
                    value={BASELINE.model3Dictator}
                    color="bg-slate-400"
                  />
                  <Bar
                    label={`우리 · 이기심(A) n=${d.model3.n}`}
                    value={d.model3.selfPct}
                    color="bg-orange-500"
                  />
                  <Bar
                    label="우리 · 이타심(B)"
                    value={d.model3.altruismPct}
                    color="bg-emerald-600"
                  />
                </>
              )}
              <p className="text-xs text-slate-500">
                평균 인간본능 {d.model3.avgInstinct} · 공감 {d.model3.avgEmpathy} · 기억조각{" "}
                {d.model3.avgFragments}
              </p>
              <Hypothesis text={REFERENCE.model3.hypothesis} />
              {insights && (
                <Analysis result={insights.m3.result} meaning={insights.m3.meaning} />
              )}
              <Source>{REFERENCE.model3.baselines[2].source}</Source>
            </Card>

            <h2 className="pt-2 text-sm font-semibold tracking-widest text-slate-400">
              그룹별 교차분석
            </h2>
            <GroupTable title="학년별" stats={grade} view={view} />
            <GroupTable title="성별" stats={gender} view={view} />
            <GroupTable title="전공별" stats={major} view={view} />
            <GroupTable title="MBTI 사고형(T) vs 감정형(F)" stats={mbtiTF} view={view} />
            {mbtiType.length > 0 && (
              <GroupTable
                title="MBTI 유형별"
                desc="데이터가 있는 유형만 표본순으로 표시"
                stats={mbtiType}
                view={view}
              />
            )}

            <Card title="참고문헌">
              <ul className="space-y-2 text-xs text-slate-500">
                {Object.values(REFERENCE).flatMap((m) =>
                  m.sources.map((s) => (
                    <li key={s}>
                      [{m.title.split(" ")[0]}] {s}
                    </li>
                  )),
                )}
              </ul>
            </Card>
          </>
        )}

        {panel === "analysis" && !d && (
          <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
            분석할 데이터가 없습니다. 게임을 완료하면 그래프·교차분석이 여기에 표시됩니다.
          </p>
        )}

        {/* ── 브랜드 / QR — 메뉴 선택 시에만 ── */}
        {panel === "brand" && <BrandCard secret={secret} />}
        {panel === "qr" && <QRCard />}
      </main>
      <CreditsFooter light />
    </div>
  );
}

function ToolBtn({
  onClick,
  disabled,
  danger,
  children,
}: {
  onClick: () => void;
  disabled?: boolean;
  danger?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-40 ${
        danger
          ? "border border-rose-200 text-rose-600 hover:bg-rose-50"
          : "border border-slate-300 text-slate-700 hover:bg-slate-100"
      }`}
    >
      {children}
    </button>
  );
}

function Hypothesis({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
      <p className="text-xs leading-relaxed text-amber-800">
        <span className="font-semibold">가설 · </span>
        {text}
      </p>
    </div>
  );
}

function Analysis({ result, meaning }: { result: string; meaning: string }) {
  return (
    <>
      <div className="rounded-lg border border-sky-200 bg-sky-50 px-4 py-3">
        <p className="text-xs leading-relaxed text-sky-900">
          <span className="font-semibold">분석 결과 · </span>
          {result}
        </p>
      </div>
      <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
        <p className="text-xs leading-relaxed text-slate-700">
          <span className="font-semibold text-slate-900">이 부분이 뜻하는 내용 · </span>
          {meaning}
        </p>
      </div>
    </>
  );
}

function CreditsFooter({ className = "", light }: { className?: string; light?: boolean }) {
  const b = useBranding();
  return (
    <footer
      className={`px-6 py-6 text-center space-y-2 border-t ${
        light ? "border-slate-200" : "border-stone-900"
      } ${className}`}
    >
      <p
        className={`text-[11px] leading-relaxed whitespace-pre-line ${
          light ? "text-slate-500" : "text-stone-500"
        }`}
      >
        {b.credit}
      </p>
      <p className={`text-xs ${light ? "text-slate-400" : "text-stone-700"}`}>
        {b.copyright}
      </p>
    </footer>
  );
}
