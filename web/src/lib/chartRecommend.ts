/** 데이터 형태에 따라 적절한 그래프 2종을 추천 */

export type ChartKind = "bar" | "line" | "pie" | "scatter";

export const CHART_LABEL: Record<ChartKind, string> = {
  bar: "막대 그래프 (Bar Chart)",
  line: "꺾은선 그래프 (Line Graph)",
  pie: "원 그래프 (Pie Chart)",
  scatter: "산점도 (Scatter Plot)",
};

export interface ChartRec {
  kind: ChartKind;
  reason: string;
}

export type ChartContext =
  | "composition" // 구성비·엔딩 분포 (소수의 범주 %/건수)
  | "comparison" // 그룹·기준선 비교 (여러 범주·여러 지표)
  | "trend" // 연속·순서 있는 변화
  | "correlation"; // 두 연속 변수 관계

/** 맥락별로 적합한 그래프 2가지를 추천 */
export function recommendCharts(ctx: ChartContext): ChartRec[] {
  switch (ctx) {
    case "composition":
      return [
        {
          kind: "pie",
          reason: "전체 대비 각 범주(엔딩·선택)의 구성 비율을 한눈에 보여 줍니다.",
        },
        {
          kind: "bar",
          reason: "범주별 비중을 나란히 비교할 때 수치 차이를 정확히 읽기 쉽습니다.",
        },
      ];
    case "comparison":
      return [
        {
          kind: "bar",
          reason: "그룹(학년·성별·MBTI 등) 간 지표를 나란히 비교하기에 가장 적합합니다.",
        },
        {
          kind: "line",
          reason: "여러 지표의 상대 패턴을 선으로 이으면 그룹 간 경향을 읽기 쉽습니다.",
        },
      ];
    case "trend":
      return [
        {
          kind: "line",
          reason: "순서·연속 변화(등급·누적)를 추세로 표현하기에 적합합니다.",
        },
        {
          kind: "bar",
          reason: "각 지점의 절대값을 명확히 비교할 때 보완적으로 사용합니다.",
        },
      ];
    case "correlation":
      return [
        {
          kind: "scatter",
          reason: "두 연속 변수(예: 용기–공감)의 관계·군집을 확인할 수 있습니다.",
        },
        {
          kind: "line",
          reason: "정렬된 추세선으로 대략적 경향을 보조적으로 제시합니다.",
        },
      ];
  }
}
