/** 기존 통계 기준선 + 출처 — analyze.py 와 동일 */

export const REFERENCE = {
  model1: {
    title: "콜버그 도덕성 발달이론 · 길리건 '배려의 윤리'",
    en: "Kohlberg's Moral Development & Gilligan's Ethics of Care",
    dilemma: "원칙(규칙 준수) vs 공감(예외 허용)",
    mapsTo: "사전 설문 Q1 · 게임 내 '갈등의 저울'(군인 vs 인간)",
    baselines: [
      {
        label: "인습적 수준(규칙·질서 우선)에 머무는 청소년 비율",
        value: 65,
        unit: "%",
        note: "약 60~70% 범위의 대표값.",
        source:
          "Colby, Kohlberg, Gibbs & Lieberman (1983), Monographs of the SRCD 48(1-2)",
      },
      {
        label: "도덕 지향 성차(배려 지향)의 효과크기 d",
        value: 0.28,
        unit: "d",
        note: "여성이 배려 지향에 다소 치우침(작은 효과).",
        source:
          "Jaffee & Hyde (2000), Psychological Bulletin 126(5), 703-726",
      },
    ],
    sources: [
      "Kohlberg, L. (1984). The Psychology of Moral Development. Harper & Row.",
      "Colby, A., Kohlberg, L., Gibbs, J., & Lieberman, M. (1983). A Longitudinal Study of Moral Judgment. Monographs SRCD 48(1-2).",
      "Gilligan, C. (1982). In a Different Voice. Harvard University Press.",
      "Jaffee, S., & Hyde, J. S. (2000). Gender Differences in Moral Orientation: A Meta-Analysis. Psychological Bulletin, 126(5), 703-726.",
    ],
    hypothesis:
      "기존 통계는 청소년 다수가 '규칙(원칙)'을 우선한다. 내러티브 몰입이 도덕 판단을 유연하게 만든다면, '공감(예외)' 선택 비율이 기준선보다 높게 나타날 것이다.",
  },
  model2: {
    title: "MBTI 사고형(T) vs 감정형(F) 청소년 분포",
    en: "MBTI Thinking vs Feeling — Adolescent Distribution",
    dilemma: "논리·객관(T) vs 관계·맥락(F)",
    mapsTo: "MBTI 3번째 지표(T/F) · 도달 엔딩 · 용기 스탯",
    baselines: [
      {
        label: "남성 중 사고형(T) 선호 비율",
        value: 56.5,
        unit: "%",
        source: "Myers et al. (1998), MBTI Manual (3rd ed.), CPP",
      },
      {
        label: "여성 중 감정형(F) 선호 비율",
        value: 75.5,
        unit: "%",
        source: "Myers et al. (1998), MBTI Manual (3rd ed.), CPP",
      },
    ],
    sources: [
      "Myers, I. B., McCaulley, M. H., Quenk, N. L., & Hammer, A. L. (1998). MBTI Manual (3rd ed.). CPP/CAPT.",
      "한국MBTI연구소(어세스타), MBTI Form M/Q 한국 표준화 연구.",
    ],
    hypothesis:
      "T형은 '원칙·생존'을 중시한다고 알려져 있다. 전쟁 체험의 심리적 압박이 성향을 덮어쓴다면, T형도 진엔딩에 도달하는 비율이 높아질 것이다.",
  },
  model3: {
    title: "트롤리 딜레마 · 행동경제학(독재자 게임)",
    en: "Trolley Problem & Behavioral Economics",
    dilemma: "개인의 안위(이기심) vs 집단·타인을 위한 희생(이타심)",
    mapsTo: "사전 설문 Q3 · 인간본능 vs 공감 · 기억 조각",
    baselines: [
      {
        label: "트롤리 '스위치' 공리주의적 선택 비율",
        value: 89,
        unit: "%",
        source: "Hauser et al. (2007), Mind & Language 22(1)",
      },
      {
        label: "트롤리 '육교(직접 밀기)' 허용 비율",
        value: 11,
        unit: "%",
        source: "Hauser et al. (2007); Greene et al. (2001), Science 293",
      },
      {
        label: "독재자 게임 평균 이타적 양보율",
        value: 28.3,
        unit: "%",
        source: "Engel (2011), Experimental Economics 14(4)",
      },
    ],
    sources: [
      "Foot, P. (1967). The Problem of Abortion and the Doctrine of Double Effect. Oxford Review, 5.",
      "Greene, J. D., et al. (2001). Science, 293, 2105-2108.",
      "Hauser, M., et al. (2007). Mind & Language, 22(1), 1-21.",
      "Engel, C. (2011). Experimental Economics, 14(4), 583-610.",
    ],
    hypothesis:
      "익명 상황에서 자기 이익 우선 경향이 보고되나, 전우 상호작용(기억 조각)을 거치면 이타적 선택이 늘어날 것이다.",
  },
} as const;

export const BASELINE = {
  model1Principle: 65,
  model2MaleT: 56.5,
  model2FemaleF: 75.5,
  model3TrolleySwitch: 89,
  model3TrolleyBridge: 11,
  model3Dictator: 28.3,
} as const;
