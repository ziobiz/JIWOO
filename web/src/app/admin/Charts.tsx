"use client";

/** 의존성 없는 경량 SVG 차트 — 그룹 막대(세로) & 도넛 */

export interface Series {
  name: string;
  color: string;
  values: number[];
}

function niceMax(v: number): number {
  if (v <= 0) return 100;
  if (v <= 100) return 100;
  const pow = Math.pow(10, Math.floor(Math.log10(v)));
  return Math.ceil(v / pow) * pow;
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
  const m =
    max ?? niceMax(Math.max(1, ...series.flatMap((s) => s.values)));
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
      {series.length > 1 && (
        <div className="mb-2 flex flex-wrap gap-3">
          {series.map((s) => (
            <span key={s.name} className="inline-flex items-center gap-1.5 text-xs text-slate-600">
              <span className="inline-block h-2.5 w-2.5 rounded-sm" style={{ background: s.color }} />
              {s.name}
            </span>
          ))}
        </div>
      )}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img">
        {/* y 그리드 + 눈금 */}
        {ticks.map((t) => (
          <g key={t}>
            <line x1={padL} x2={W - padR} y1={yOf(t)} y2={yOf(t)} stroke="#e2e8f0" strokeWidth={1} />
            <text x={padL - 6} y={yOf(t) + 3} textAnchor="end" fontSize={10} fill="#94a3b8">
              {t}
            </text>
          </g>
        ))}
        {/* 막대 */}
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

export interface Slice {
  label: string;
  value: number;
  color: string;
}

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
