/** 3대 모델별 — 누적 데이터 기반 '분석 결과'와 '해석(뜻하는 내용)' 자동 생성 */
import type { AnalysisReport } from "@/types/game";
import { BASELINE } from "./references";

const SMALL = 30; // 표본이 이보다 적으면 잠정적 해석 안내

export interface ModelInsight {
  result: string; // 분석 결과 (수치 요약)
  meaning: string; // 이 부분이 뜻하는 내용 (해석)
}

const signed = (n: number) => `${n > 0 ? "+" : ""}${Math.round(n * 10) / 10}`;

export function modelInsights(
  d: AnalysisReport["data"],
  sampleSize: number,
): { m1: ModelInsight; m2: ModelInsight; m3: ModelInsight } {
  const note =
    sampleSize < SMALL
      ? ` (표본 n=${sampleSize}로 아직 적어 잠정적 해석이며, 데이터가 축적될수록 신뢰도가 높아집니다.)`
      : ` (표본 n=${sampleSize}로 경향 해석이 가능한 수준입니다.)`;

  // ① 콜버그·길리건 — 원칙 vs 공감
  const p = d.model1.principlePct;
  const e = d.model1.empathyPct;
  const b1 = BASELINE.model1Principle;
  const dl1 = Math.round((p - b1) * 10) / 10;
  const m1: ModelInsight = {
    result: `표본 n=${d.model1.n} · 원칙(A) ${p}% / 공감(B) ${e}%. 기준선(규칙 우선 ≈${b1}%) 대비 원칙 선택 ${signed(dl1)}%p. 평균 저울 — 인간 ${d.model1.avgHuman} · 군인 ${d.model1.avgSoldier}.`,
    meaning:
      (dl1 <= -5
        ? "기존 통계와 반대로 '공감(예외 허용)' 지향이 우세합니다. 1인칭 전쟁 서사 몰입이 규칙 중심의 도덕 판단을 관계·상황 중심으로 이동시킨다는 가설을 뒷받침합니다."
        : dl1 >= 5
          ? "기존 통계처럼 '원칙(규칙)' 지향이 유지·강화됩니다. 서사에 몰입해도 규범적 판단 경향이 견고함을 시사합니다."
          : "기준선과 유사한 분포로, 원칙과 공감 사이 뚜렷한 이동은 아직 관찰되지 않습니다.") + note,
  };

  // ② MBTI T vs F — 엔딩·용기
  const t = d.model2.tGoodEndingPct;
  const f = d.model2.fGoodEndingPct;
  const gap = Math.round((t - f) * 10) / 10;
  const m2: ModelInsight = {
    result: `T형(n=${d.model2.tN}) 진엔딩 ${t}% · F형(n=${d.model2.fN}) 진엔딩 ${f}%. 평균 용기 — T ${d.model2.tAvgCourage} · F ${d.model2.fAvgCourage}.`,
    meaning:
      (gap >= 5
        ? "사고형(T)이 감정형(F)보다 진엔딩(용기) 도달이 높습니다. 전쟁 상황의 심리적 압박이 기질적 성향을 덮어쓸 수 있다는 가설과 부합합니다."
        : gap <= -5
          ? "감정형(F)이 진엔딩 도달에서 우세합니다. 관계·공감 중심 성향이 용기 서사에 유리하게 작용했을 가능성을 시사합니다."
          : "T형과 F형의 진엔딩 도달률이 비슷합니다. 성향 차이보다 서사 경험 자체가 결과를 좌우했을 가능성이 있습니다.") + note,
  };

  // ③ 트롤리·행동경제학 — 이기심 vs 이타심
  const self = d.model3.selfPct;
  const alt = d.model3.altruismPct;
  const b3 = BASELINE.model3Dictator;
  const dl3 = Math.round((alt - b3) * 10) / 10;
  const m3: ModelInsight = {
    result: `표본 n=${d.model3.n} · 이기심(A) ${self}% / 이타심(B) ${alt}%. 기준선(독재자 게임 양보 ${b3}%) 대비 이타심 ${signed(dl3)}%p. 평균 인간본능 ${d.model3.avgInstinct} · 공감 ${d.model3.avgEmpathy} · 기억조각 ${d.model3.avgFragments}.`,
    meaning:
      (dl3 >= 5
        ? "익명 상황의 자기이익 우선 경향과 달리 이타적 선택이 늘었습니다. 전우 상호작용(기억 조각) 경험이 이타성을 촉진한다는 가설을 지지합니다."
        : dl3 <= -5
          ? "이타적 선택이 기준선보다 낮아, 생존 압박 속 자기이익 우선 경향이 강화됨을 시사합니다."
          : "기준선과 유사한 수준의 이타성이 관찰됩니다.") + note,
  };

  return { m1, m2, m3 };
}
