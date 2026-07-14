"use client";

import { useMemo, useState } from "react";
import {
  CHART_LABEL,
  recommendCharts,
  type ChartContext,
  type ChartKind,
} from "@/lib/chartRecommend";

/** 의존성 없는 경량 SVG 차트 — 막대 · 꺾은선 · 원 · 산점도 */

export interface Series {
  name: string;
  color: string;
  values: number[];
}

export interface Slice {
  label: string;
  value: number;
  color: string;
}

export interface ScatterPoint {
  x: number;
  y: number;
  label?: string;
  color?: string;
}

function niceMax(v: number): number {
  if (v <= 0) return 100;
  if (v <= 100) return 100;
  const pow = Math.pow(10, Math.floor(Math.log10(v)));
  return Math.ceil(v / pow) * pow;
}

function Legend({ series }: { series: { name: string; color: string }[] }) {
  if (series.length <= 1) return null;
  return (
    <div className="mb-2 flex flex-wrap gap-3">
      {series.map((s) => (
        <span key={s.name} className="inline-flex items-center gap-1.5 text-xs text-slate-600">
          <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: s.color }} />
          {s.name}
        </span>
      ))}
    </div>
  );
}

export function ColumnChart({
  categories,
  series,
  max,
  unit = "%",
  height = 300,
}: {
  categories: string[];
  series: Series[];
  max?: number;
  unit?: string;
  height?: number;
}) {
  const W = 680;
  const H = height;
  const padL = 38;
  const padR = 14;
  const padT = 18;
  const padB = 52;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;
  const m = max ?? niceMax(Math.max(1, ...series.flatMap((s) => s.values)));
  const n = Math.max(1, categories.length);
  const groupW = plotW / n;
  const innerPad = groupW * 0.16;
  const barsW = groupW - innerPad * 2;
  const gap = series.length > 1 ? 4 : 0;
  const bw = Math.max(2, (barsW - gap * (series.length - 1)) / series.length);
  const yOf = (v: number) => padT + plotH - (v / m) * plotH;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(m * f));

  return (
    <div className="w-full">
      <Legend series={series} />
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={padL} x2={W - padR} y1={yOf(t)} y2={yOf(t)} stroke="#e2e8f0" strokeWidth={1} />
            <text x={padL - 6} y={yOf(t) + 3} textAnchor="end" fontSize={10} fill="#94a3b8">
              {t}
            </text>
          </g>
        ))}
        {categories.map((cat, ci) => {
          const gx = padL + ci * groupW + innerPad;
          return (
            <g key={cat + ci}>
              {series.map((s, si) => {
                const v = s.values[ci] ?? 0;
                const x = gx + si * (bw + gap);
                const y = yOf(v);
                const h = padT + plotH - y;
                return (
                  <g key={s.name}>
                    <rect x={x} y={y} width={bw} height={Math.max(0, h)} rx={2} fill={s.color} />
                    {bw >= 16 && (
                      <text x={x + bw / 2} y={y - 3} textAnchor="middle" fontSize={9} fill="#475569">
                        {v}
                      </text>
                    )}
                  </g>
                );
              })}
              <text
                x={padL + ci * groupW + groupW / 2}
                y={H - padB + 16}
                textAnchor="middle"
                fontSize={11}
                fill="#334155"
              >
                {cat.length > 8 ? cat.slice(0, 8) : cat}
              </text>
            </g>
          );
        })}
        <text x={padL - 26} y={padT - 4} fontSize={9} fill="#94a3b8">
          {unit}
        </text>
      </svg>
    </div>
  );
}

export function LineChart({
  categories,
  series,
  max,
  unit = "%",
  height = 300,
}: {
  categories: string[];
  series: Series[];
  max?: number;
  unit?: string;
  height?: number;
}) {
  const W = 680;
  const H = height;
  const padL = 38;
  const padR = 14;
  const padT = 18;
  const padB = 52;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;
  const m = max ?? niceMax(Math.max(1, ...series.flatMap((s) => s.values)));
  const n = Math.max(1, categories.length);
  const xOf = (i: number) => padL + (n === 1 ? plotW / 2 : (i / (n - 1)) * plotW);
  const yOf = (v: number) => padT + plotH - (v / m) * plotH;
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(m * f));

  return (
    <div className="w-full">
      <Legend series={series} />
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img">
        {ticks.map((t) => (
          <g key={t}>
            <line x1={padL} x2={W - padR} y1={yOf(t)} y2={yOf(t)} stroke="#e2e8f0" strokeWidth={1} />
            <text x={padL - 6} y={yOf(t) + 3} textAnchor="end" fontSize={10} fill="#94a3b8">
              {t}
            </text>
          </g>
        ))}
        {series.map((s) => {
          const pts = s.values
            .map((v, i) => `${xOf(i)},${yOf(v)}`)
            .join(" ");
          return (
            <g key={s.name}>
              <polyline
                fill="none"
                stroke={s.color}
                strokeWidth={2.5}
                strokeLinejoin="round"
                strokeLinecap="round"
                points={pts}
              />
              {s.values.map((v, i) => (
                <circle key={i} cx={xOf(i)} cy={yOf(v)} r={3.5} fill={s.color} />
              ))}
            </g>
          );
        })}
        {categories.map((cat, i) => (
          <text
            key={cat + i}
            x={xOf(i)}
            y={H - padB + 16}
            textAnchor="middle"
            fontSize={11}
            fill="#334155"
          >
            {cat.length > 8 ? cat.slice(0, 8) : cat}
          </text>
        ))}
        <text x={padL - 26} y={padT - 4} fontSize={9} fill="#94a3b8">
          {unit}
        </text>
      </svg>
    </div>
  );
}

export function PieChart({ data, size = 220 }: { data: Slice[]; size?: number }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const cx = 100;
  const cy = 100;
  const r = 80;
  let angle = -Math.PI / 2;

  const slices = data.map((d) => {
    const frac = d.value / total;
    const start = angle;
    const end = angle + frac * Math.PI * 2;
    angle = end;
    const large = end - start > Math.PI ? 1 : 0;
    const x1 = cx + r * Math.cos(start);
    const y1 = cy + r * Math.sin(start);
    const x2 = cx + r * Math.cos(end);
    const y2 = cy + r * Math.sin(end);
    const dPath =
      frac >= 0.999
        ? `M ${cx} ${cy - r} A ${r} ${r} 0 1 1 ${cx - 0.01} ${cy - r} Z`
        : `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} Z`;
    return { ...d, dPath, pct: Math.round(frac * 1000) / 10 };
  });

  return (
    <div className="flex flex-wrap items-center gap-6">
      <svg viewBox="0 0 200 200" width={size} height={size} role="img">
        {slices.map((s) => (
          <path key={s.label} d={s.dPath} fill={s.color} stroke="#fff" strokeWidth={1.5} />
        ))}
      </svg>
      <div className="space-y-1.5">
        {slices.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-sm text-slate-600">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ background: d.color }} />
            <span className="font-medium text-slate-800">{d.label}</span>
            <span className="text-slate-400">
              {d.value} · {d.pct}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/** 기존 Donut — Pie와 병행 유지 */
export function DonutChart({ data, size = 200 }: { data: Slice[]; size?: number }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const r = 70;
  const c = 2 * Math.PI * r;
  let acc = 0;
  return (
    <div className="flex flex-wrap items-center gap-6">
      <svg viewBox="0 0 200 200" width={size} height={size} role="img">
        <g transform="rotate(-90 100 100)">
          <circle cx={100} cy={100} r={r} fill="none" stroke="#f1f5f9" strokeWidth={26} />
          {data.map((d) => {
            const len = (d.value / total) * c;
            const seg = (
              <circle
                key={d.label}
                cx={100}
                cy={100}
                r={r}
                fill="none"
                stroke={d.color}
                strokeWidth={26}
                strokeDasharray={`${len} ${c - len}`}
                strokeDashoffset={-acc}
              />
            );
            acc += len;
            return seg;
          })}
        </g>
        <text x={100} y={96} textAnchor="middle" fontSize={13} fill="#64748b">
          합계
        </text>
        <text x={100} y={116} textAnchor="middle" fontSize={20} fontWeight={700} fill="#0f172a">
          {total}
        </text>
      </svg>
      <div className="space-y-1.5">
        {data.map((d) => (
          <div key={d.label} className="flex items-center gap-2 text-sm text-slate-600">
            <span className="inline-block h-3 w-3 rounded-sm" style={{ background: d.color }} />
            <span className="font-medium text-slate-800">{d.label}</span>
            <span className="text-slate-400">
              {d.value}건 · {Math.round((d.value / total) * 1000) / 10}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ScatterPlot({
  points,
  xLabel = "X",
  yLabel = "Y",
  maxX,
  maxY,
  height = 300,
}: {
  points: ScatterPoint[];
  xLabel?: string;
  yLabel?: string;
  maxX?: number;
  maxY?: number;
  height?: number;
}) {
  const W = 680;
  const H = height;
  const padL = 48;
  const padR = 18;
  const padT = 18;
  const padB = 48;
  const plotW = W - padL - padR;
  const plotH = H - padT - padB;
  const mx = maxX ?? niceMax(Math.max(1, ...points.map((p) => p.x)));
  const my = maxY ?? niceMax(Math.max(1, ...points.map((p) => p.y)));
  const xOf = (v: number) => padL + (v / mx) * plotW;
  const yOf = (v: number) => padT + plotH - (v / my) * plotH;

  return (
    <div className="w-full">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img">
        {[0, 0.25, 0.5, 0.75, 1].map((f) => (
          <g key={f}>
            <line
              x1={padL}
              x2={W - padR}
              y1={yOf(my * f)}
              y2={yOf(my * f)}
              stroke="#e2e8f0"
              strokeWidth={1}
            />
            <text x={padL - 6} y={yOf(my * f) + 3} textAnchor="end" fontSize={10} fill="#94a3b8">
              {Math.round(my * f)}
            </text>
          </g>
        ))}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={xOf(p.x)}
            cy={yOf(p.y)}
            r={5}
            fill={p.color ?? "#0284c7"}
            fillOpacity={0.75}
            stroke="#fff"
            strokeWidth={1}
          >
            {p.label ? <title>{p.label}</title> : null}
          </circle>
        ))}
        <text x={W / 2} y={H - 8} textAnchor="middle" fontSize={11} fill="#64748b">
          {xLabel}
        </text>
        <text
          x={14}
          y={H / 2}
          textAnchor="middle"
          fontSize={11}
          fill="#64748b"
          transform={`rotate(-90 14 ${H / 2})`}
        >
          {yLabel}
        </text>
      </svg>
    </div>
  );
}

const KINDS: ChartKind[] = ["bar", "line", "pie", "scatter"];

/**
 * 도식화 보드 — 4종 그래프 선택 + 하단 추천 2가지
 * categories/series : 막대·꺾은선
 * slices : 원 그래프
 * scatter : 산점도 (없으면 산점도 비활성)
 */
export function ChartBoard({
  context,
  categories,
  series,
  slices,
  scatter,
  unit = "%",
}: {
  context: ChartContext;
  categories: string[];
  series: Series[];
  slices?: Slice[];
  scatter?: {
    points: ScatterPoint[];
    xLabel?: string;
    yLabel?: string;
  };
  unit?: string;
}) {
  const recs = useMemo(() => recommendCharts(context), [context]);
  const [kind, setKind] = useState<ChartKind>(recs[0].kind);

  const pieData: Slice[] =
    slices ??
    (series.length === 1
      ? categories.map((c, i) => ({
          label: c,
          value: series[0].values[i] ?? 0,
          color: series[0].color,
        }))
      : categories.map((c, i) => ({
          label: c,
          value: series.reduce((s, ser) => s + (ser.values[i] ?? 0), 0) / Math.max(1, series.length),
          color: series[0]?.color ?? "#0284c7",
        })));

  const scatterPts =
    scatter?.points ??
    categories.map((c, i) => ({
      x: i + 1,
      y: series[0]?.values[i] ?? 0,
      label: c,
      color: series[0]?.color ?? "#0284c7",
    }));

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="mr-1 text-[11px] font-semibold text-slate-500">도식 유형</span>
        {KINDS.map((k) => (
          <button
            key={k}
            type="button"
            onClick={() => setKind(k)}
            className={`rounded-md border px-2.5 py-1 text-[11px] transition-colors ${
              kind === k
                ? "border-amber-500 bg-amber-50 text-amber-800 font-medium"
                : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
            }`}
          >
            {CHART_LABEL[k]}
          </button>
        ))}
      </div>

      <div className="rounded-xl border border-slate-100 bg-slate-50/50 p-3">
        {kind === "bar" && (
          <ColumnChart categories={categories} series={series} unit={unit} />
        )}
        {kind === "line" && (
          <LineChart categories={categories} series={series} unit={unit} />
        )}
        {kind === "pie" && <PieChart data={pieData} />}
        {kind === "scatter" && (
          <ScatterPlot
            points={scatterPts}
            xLabel={scatter?.xLabel ?? "범주 순서"}
            yLabel={scatter?.yLabel ?? unit}
          />
        )}
      </div>

      <div className="rounded-lg border border-violet-200 bg-violet-50 px-3 py-2.5">
        <p className="text-[11px] font-semibold text-violet-800 mb-1.5">
          추천 도식 (분석 결과 · 2가지)
        </p>
        <ol className="space-y-1 list-decimal list-inside">
          {recs.map((r, i) => (
            <li key={r.kind} className="text-[11px] leading-relaxed text-violet-900">
              <button
                type="button"
                onClick={() => setKind(r.kind)}
                className="font-semibold underline-offset-2 hover:underline"
              >
                {i + 1}. {CHART_LABEL[r.kind]}
              </button>
              <span className="text-violet-700"> — {r.reason}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
