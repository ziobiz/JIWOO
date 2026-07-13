/** Excel(xlsx) · PowerPoint(pptx) 자동 생성 — 클라이언트에서 버튼 클릭 시 동적 로드 */
import type { AnalysisReport, PlayResult } from "@/types/game";
import type { GroupStat } from "./breakdown";
import { label } from "./breakdown";
import { BASELINE, REFERENCE } from "./references";

export interface AnalysisBundle {
  report: AnalysisReport;
  rows: PlayResult[];
  grade: GroupStat[];
  gender: GroupStat[];
  major: GroupStat[];
  mbtiTF: GroupStat[];
  mbtiType: GroupStat[];
}

const STAMP = () => new Date().toISOString().slice(0, 10);

const GROUP_HEADERS = [
  "구분",
  "표본 n",
  "진엔딩%",
  "원칙(Q1A)%",
  "이타심(Q3B)%",
  "평균 용기",
  "평균 공감",
  "평균 죄책감",
  "평균 인간",
  "평균 군인",
  "평균 조각",
  "평균 일치(/3)",
];

function groupRow(s: GroupStat): (string | number)[] {
  return [
    s.label,
    s.n,
    s.goodEndingPct,
    s.principlePct,
    s.altruismPct,
    s.avgCourage,
    s.avgEmpathy,
    s.avgGuilt,
    s.avgHuman,
    s.avgSoldier,
    s.avgFragments,
    s.avgMatches,
  ];
}

/* ─────────────────────────── Excel ─────────────────────────── */

export async function exportExcel(b: AnalysisBundle) {
  const XLSX = await import("xlsx");
  const wb = XLSX.utils.book_new();
  const d = b.report.data;

  // 1) 요약
  const summary: (string | number)[][] = [
    ["붉은 무공훈장 — 플레이 데이터 분석 요약"],
    ["생성일", b.report.generatedAt],
    ["데이터 소스", b.report.source],
    ["표본 n", b.report.sampleSize],
    [],
    ["모델", "지표", "기준선(기존통계)%", "우리 데이터%"],
    ["① 콜버그·길리건", "원칙(A) 비율", BASELINE.model1Principle, d.model1.principlePct],
    ["① 콜버그·길리건", "공감(B) 비율", 100 - BASELINE.model1Principle, d.model1.empathyPct],
    ["② MBTI T·F", "T형 진엔딩", BASELINE.model2MaleT, d.model2.tGoodEndingPct],
    ["② MBTI T·F", "F형 진엔딩", BASELINE.model2FemaleF, d.model2.fGoodEndingPct],
    ["③ 트롤리·행동경제학", "이타심(B) 비율", BASELINE.model3Dictator, d.model3.altruismPct],
  ];
  XLSX.utils.book_append_sheet(
    wb,
    XLSX.utils.aoa_to_sheet(summary),
    "요약",
  );

  // 2) 엔딩 분포
  const ending: (string | number)[][] = [
    ["엔딩", "건수", "비율%"],
    ...d.endingDistribution.map((e) => [e.code, e.count, e.pct]),
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(ending), "엔딩분포");

  // 3) 그룹별 교차분석
  const groupSheet = (title: string, stats: GroupStat[]) => {
    const aoa: (string | number)[][] = [GROUP_HEADERS, ...stats.map(groupRow)];
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(aoa), title);
  };
  groupSheet("학년별", b.grade);
  groupSheet("성별", b.gender);
  groupSheet("전공별", b.major);
  groupSheet("MBTI(T·F)", b.mbtiTF);
  groupSheet("MBTI유형별", b.mbtiType);

  // 4) 원자료
  const rawHeaders = [
    "생성일시", "이름", "성별", "학년", "전공", "MBTI",
    "Q1", "Q2", "Q3", "엔딩",
    "인간", "군인", "신뢰", "공감", "인간본능", "사회적역할", "죄책감", "용기", "조각", "일치",
  ];
  const raw: (string | number)[][] = [
    rawHeaders,
    ...b.rows.map((r) => [
      r.created_at ?? "",
      r.name,
      label(r.gender),
      label(r.grade),
      label(r.major),
      r.mbti,
      r.q1, r.q2, r.q3, r.ending,
      r.human, r.soldier, r.trust, r.empathy, r.instinct, r.duty, r.guilt, r.courage, r.fragments, r.matches,
    ]),
  ];
  XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(raw), "원자료");

  XLSX.writeFile(wb, `붉은무공훈장_분석_${STAMP()}.xlsx`);
}

/* ─────────────────────────── PowerPoint ─────────────────────────── */

const NAVY = "1E293B";
const AMBER = "B45309";
const SLATE = "475569";
const GREEN = "047857";
const GRAY = "94A3B8";

type PptxInstance = InstanceType<(typeof import("pptxgenjs"))["default"]>;
type PptxSlide = ReturnType<PptxInstance["addSlide"]>;

export async function exportPptx(b: AnalysisBundle) {
  const mod = await import("pptxgenjs");
  const PptxGen = mod.default;
  const pptx = new PptxGen();
  pptx.layout = "LAYOUT_WIDE";
  pptx.defineSlideMaster({
    title: "MAIN",
    background: { color: "FFFFFF" },
    objects: [
      { line: { x: 0.5, y: 6.9, w: 12.3, h: 0, line: { color: "E2E8F0", width: 1 } } },
    ],
  });
  const d = b.report.data;

  const foot = (slide: PptxSlide) => {
    slide.addText("근현대 미국 문학 탐구 연구회 · 동두천외국어고등학교", {
      x: 0.5, y: 6.95, w: 12.3, h: 0.35, fontSize: 9, color: GRAY, align: "left",
    });
  };
  const heading = (slide: PptxSlide, t: string) => {
    slide.addText(t, { x: 0.5, y: 0.35, w: 12.3, h: 0.7, fontSize: 26, bold: true, color: NAVY });
  };

  // 1) 타이틀
  {
    const s = pptx.addSlide({ masterName: "MAIN" });
    s.addText("붉은 무공훈장", { x: 0.5, y: 2.2, w: 12.3, h: 1, fontSize: 44, bold: true, color: NAVY, align: "center" });
    s.addText("플레이 데이터 학술 비교 분석", { x: 0.5, y: 3.3, w: 12.3, h: 0.6, fontSize: 22, color: AMBER, align: "center" });
    s.addText(
      `표본 n = ${b.report.sampleSize}   ·   ${STAMP()}`,
      { x: 0.5, y: 4.1, w: 12.3, h: 0.5, fontSize: 14, color: SLATE, align: "center" },
    );
    foot(s);
  }

  // 2) 엔딩 분포 (막대 차트)
  {
    const s = pptx.addSlide({ masterName: "MAIN" });
    heading(s, "엔딩 분포");
    if (d.endingDistribution.length) {
      s.addChart(
        pptx.ChartType.bar,
        [{
          name: "비율%",
          labels: d.endingDistribution.map((e) => e.code),
          values: d.endingDistribution.map((e) => e.pct),
        }],
        { x: 0.7, y: 1.4, w: 11.9, h: 5, showValue: true, chartColors: [AMBER], barDir: "col" },
      );
    } else {
      s.addText("데이터가 없습니다.", { x: 0.5, y: 3, w: 12, h: 1, fontSize: 18, color: SLATE });
    }
    foot(s);
  }

  // 3~5) 세 가지 모델 비교
  const modelSlide = (
    title: string,
    hypothesis: string,
    source: string,
    labels: string[],
    baseVals: number[],
    ourVals: number[],
  ) => {
    const s = pptx.addSlide({ masterName: "MAIN" });
    heading(s, title);
    s.addChart(
      pptx.ChartType.bar,
      [
        { name: "기존 통계(기준선)", labels, values: baseVals },
        { name: "우리 데이터", labels, values: ourVals },
      ],
      { x: 0.7, y: 1.3, w: 7.6, h: 4, showValue: true, chartColors: [GRAY, GREEN], barDir: "col" },
    );
    s.addText(
      [
        { text: "가설\n", options: { bold: true, color: AMBER, fontSize: 13 } },
        { text: hypothesis + "\n\n", options: { color: NAVY, fontSize: 12 } },
        { text: "출처\n", options: { bold: true, color: AMBER, fontSize: 13 } },
        { text: source, options: { color: SLATE, fontSize: 11, italic: true } },
      ],
      { x: 8.5, y: 1.3, w: 4.1, h: 4.5, valign: "top" },
    );
    foot(s);
  };
  modelSlide(
    "① 콜버그 · 길리건 — 원칙 vs 공감",
    REFERENCE.model1.hypothesis,
    REFERENCE.model1.baselines[0].source,
    ["원칙(A)", "공감(B)"],
    [BASELINE.model1Principle, 100 - BASELINE.model1Principle],
    [d.model1.principlePct, d.model1.empathyPct],
  );
  modelSlide(
    "② MBTI 사고형 vs 감정형 — 엔딩·용기",
    REFERENCE.model2.hypothesis,
    REFERENCE.model2.baselines[0].source,
    ["T형 진엔딩", "F형 진엔딩"],
    [BASELINE.model2MaleT, BASELINE.model2FemaleF],
    [d.model2.tGoodEndingPct, d.model2.fGoodEndingPct],
  );
  modelSlide(
    "③ 트롤리 · 행동경제학 — 이기심 vs 이타심",
    REFERENCE.model3.hypothesis,
    REFERENCE.model3.baselines[2].source,
    ["이타심(B)"],
    [BASELINE.model3Dictator],
    [d.model3.altruismPct],
  );

  // 6) 그룹별 교차분석 (그래프 + 표)
  const chartTableSlide = (title: string, stats: GroupStat[]) => {
    const s = pptx.addSlide({ masterName: "MAIN" });
    heading(s, title);
    const labels = stats.map((g) => g.label);
    // 왼쪽: 막대 그래프(진엔딩%/원칙%/이타심%)
    s.addChart(
      pptx.ChartType.bar,
      [
        { name: "진엔딩%", labels, values: stats.map((g) => g.goodEndingPct) },
        { name: "원칙(Q1A)%", labels, values: stats.map((g) => g.principlePct) },
        { name: "이타심(Q3B)%", labels, values: stats.map((g) => g.altruismPct) },
      ],
      {
        x: 0.55, y: 1.35, w: 7.6, h: 5,
        barDir: "col", showValue: true, showLegend: true, legendPos: "b",
        chartColors: [GREEN, "0284C7", AMBER],
        valAxisMaxVal: 100, valAxisMinVal: 0,
      },
    );
    // 오른쪽: 요약 표
    const head = ["구분", "n", "진엔딩%", "용기", "일치"];
    const body = stats.map((g) => [g.label, g.n, g.goodEndingPct, g.avgCourage, g.avgMatches]);
    const rows = [head, ...body].map((r, ri) =>
      r.map((c) => ({
        text: String(c),
        options: {
          fontSize: 11,
          bold: ri === 0,
          color: ri === 0 ? "FFFFFF" : NAVY,
          fill: ri === 0 ? { color: NAVY } : { color: ri % 2 ? "F1F5F9" : "FFFFFF" },
          align: "center" as const,
        },
      })),
    );
    s.addTable(rows, { x: 8.4, y: 1.5, w: 4.3, border: { type: "solid", color: "E2E8F0", pt: 1 } });
    foot(s);
  };
  chartTableSlide("학년별 교차분석", b.grade);
  chartTableSlide("성별 교차분석", b.gender);
  chartTableSlide("전공별 교차분석", b.major);
  chartTableSlide("MBTI(T·F) 교차분석", b.mbtiTF);
  if (b.mbtiType.length) chartTableSlide("MBTI 유형별 교차분석", b.mbtiType);

  // 7) 참고문헌
  {
    const s = pptx.addSlide({ masterName: "MAIN" });
    heading(s, "참고문헌");
    const refs = Object.values(REFERENCE).flatMap((m) =>
      m.sources.map((src) => `· ${src}`),
    );
    s.addText(refs.join("\n"), { x: 0.6, y: 1.4, w: 12.1, h: 5, fontSize: 11, color: SLATE, valign: "top", lineSpacingMultiple: 1.2 });
    foot(s);
  }

  await pptx.writeFile({ fileName: `붉은무공훈장_발표자료_${STAMP()}.pptx` });
}
