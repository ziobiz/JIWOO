# -*- coding: utf-8 -*-
"""
붉은 무공훈장 — 학술 분석 엔진
=================================
게임이 누적한 results.csv 를 읽어, 세 가지 고전 심리·통계 모델의
'기존 통계 기준선'과 우리 학생 플레이 데이터를 대조 분석한다.

  모델 1. 콜버그 도덕성 발달 + 길리건 '배려의 윤리'   ← 설문 Q1 / 갈등의 저울
  모델 2. MBTI 사고형(T) vs 감정형(F) 청소년 분포      ← MBTI / 엔딩·용기
  모델 3. 트롤리 딜레마 + 행동경제학(독재자 게임)       ← 설문 Q3 / 이타적 선택

출력:
  - analysis_report.json  (프레젠테이션 Canvas 가 그대로 사용하는 집계+출처)
  - 콘솔 요약 리포트

★ 모든 기준선 통계에는 출처(SOURCES)를 명시한다. 출처 없는 수치는 싣지 않는다.
"""

import csv
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "results.csv")
OUT_PATH = os.path.join(HERE, "analysis_report.json")

# ────────────────────────────────────────────────────────────────
# 기존 통계 기준선 + 출처 (Reference baselines with mandatory citations)
# ────────────────────────────────────────────────────────────────
REFERENCE = {
    "model1": {
        "title": "콜버그 도덕성 발달이론 · 길리건 '배려의 윤리'",
        "en": "Kohlberg's Moral Development & Gilligan's Ethics of Care",
        "dilemma": "원칙(규칙 준수) vs 공감(예외 허용)",
        "maps_to": "사전 설문 Q1 · 게임 내 '갈등의 저울'(군인 vs 인간)",
        # 기준선(대표 수치). 각 항목은 반드시 source 를 가진다.
        "baselines": [
            {"label": "인습적 수준(규칙·질서 우선)에 머무는 청소년 비율",
             "value": 65, "unit": "%", "note": "약 60~70% 범위의 대표값. 채점 방식에 따라 편차.",
             "source": "Colby, Kohlberg, Gibbs & Lieberman (1983), Monographs of the SRCD 48(1-2)"},
            {"label": "도덕 지향 성차(배려 지향)의 효과크기 d",
             "value": 0.28, "unit": "d", "note": "여성이 배려 지향에 다소 치우침(작은 효과).",
             "source": "Jaffee & Hyde (2000), Psychological Bulletin 126(5), 703-726 (메타분석)"},
        ],
        "sources": [
            "Kohlberg, L. (1984). The Psychology of Moral Development. Harper & Row.",
            "Colby, A., Kohlberg, L., Gibbs, J., & Lieberman, M. (1983). A Longitudinal Study of Moral Judgment. Monographs of the Society for Research in Child Development, 48(1-2).",
            "Gilligan, C. (1982). In a Different Voice. Harvard University Press.",
            "Jaffee, S., & Hyde, J. S. (2000). Gender Differences in Moral Orientation: A Meta-Analysis. Psychological Bulletin, 126(5), 703-726.",
        ],
        "hypothesis": "기존 통계는 청소년 다수가 '규칙(원칙)'을 우선한다고 본다. "
                      "내러티브 몰입이 도덕 판단을 유연하게 만든다면, 우리 데이터에서는 "
                      "'공감(예외)' 선택 비율이 기준선보다 높게 나타날 것이다.",
    },
    "model2": {
        "title": "MBTI 사고형(T) vs 감정형(F) 청소년 분포",
        "en": "MBTI Thinking vs Feeling — Adolescent Distribution",
        "dilemma": "논리·객관(T) vs 관계·맥락(F)",
        "maps_to": "MBTI 3번째 지표(T/F) · 도달 엔딩(TRUE/GOOD) · 용기 스탯",
        "baselines": [
            {"label": "남성 중 사고형(T) 선호 비율", "value": 56.5, "unit": "%",
             "note": "미국 전국 대표표본(N=3,009).",
             "source": "Myers, McCaulley, Quenk & Hammer (1998), MBTI Manual (3rd ed.), CPP"},
            {"label": "여성 중 감정형(F) 선호 비율", "value": 75.5, "unit": "%",
             "note": "미국 전국 대표표본(N=3,009).",
             "source": "Myers, McCaulley, Quenk & Hammer (1998), MBTI Manual (3rd ed.), CPP"},
        ],
        "sources": [
            "Myers, I. B., McCaulley, M. H., Quenk, N. L., & Hammer, A. L. (1998). MBTI Manual (3rd ed.). CPP/CAPT.",
            "한국MBTI연구소(어세스타), MBTI Form M/Q 한국 표준화 연구 — 한국 청소년 T/F 규준 대체 시 사용.",
        ],
        "hypothesis": "기존 통계상 T형은 '원칙·생존'을 중시한다고 알려져 있다. "
                      "전쟁 체험의 심리적 압박이 성향을 덮어쓴다면, T형 학생도 "
                      "'용기·희생'을 택해 진엔딩(TRUE/GOOD)에 도달하는 비율이 높아질 것이다.",
    },
    "model3": {
        "title": "트롤리 딜레마 · 행동경제학(독재자 게임)",
        "en": "Trolley Problem & Behavioral Economics (Dictator Game)",
        "dilemma": "개인의 안위(이기심) vs 집단·타인을 위한 희생(이타심)",
        "maps_to": "사전 설문 Q3 · 인간본능(자기 이익) vs 공감(이타) · 기억 조각 상호작용",
        "baselines": [
            {"label": "트롤리 '스위치'에서 공리주의적 선택(다수 구제) 비율", "value": 89, "unit": "%",
             "note": "온라인 대규모 표본(N>5,000).",
             "source": "Hauser, Cushman, Young, Jin & Mikhail (2007), Mind & Language 22(1)"},
            {"label": "트롤리 '육교(직접 밀기)'에서 허용 비율", "value": 11, "unit": "%",
             "note": "직접 개입 시 이타·도덕 판단으로 급반전.",
             "source": "Hauser et al. (2007), Mind & Language 22(1); Greene et al. (2001), Science 293"},
            {"label": "독재자 게임 평균 분배율(이타적 양보)", "value": 28.3, "unit": "%",
             "note": "익명성·사회적 거리 확대 시 자기 이익 경향 강화.",
             "source": "Engel, C. (2011), Dictator Games: A Meta Study, Experimental Economics 14(4)"},
        ],
        "sources": [
            "Foot, P. (1967). The Problem of Abortion and the Doctrine of Double Effect. Oxford Review, 5.",
            "Greene, J. D., et al. (2001). An fMRI Investigation of Emotional Engagement in Moral Judgment. Science, 293, 2105-2108.",
            "Hauser, M., Cushman, F., Young, L., Jin, R., & Mikhail, J. (2007). A Dissociation Between Moral Judgments and Justifications. Mind & Language, 22(1), 1-21.",
            "Awad, E., et al. (2018). The Moral Machine Experiment. Nature, 563, 59-64.",
            "Hoffman, E., McCabe, K., & Smith, V. (1996). Social Distance and Other-Regarding Behavior in Dictator Games. American Economic Review, 86(3).",
            "Engel, C. (2011). Dictator Games: A Meta Study. Experimental Economics, 14(4), 583-610.",
        ],
        "hypothesis": "행동경제학은 익명 상황에서 자기 이익 우선 경향을 보고한다. "
                      "그러나 전우와의 상호작용(기억 조각 수집)을 거치면, 자신의 위험(죄책감·패널티)을 "
                      "감수하고 타인을 돕는 이타적 선택이 늘어날 것이다.",
    },
}

ENDING_ORDER = ["TRUE", "GOOD", "NORMAL", "BAD", "HIDDEN"]
GOOD_ENDINGS = {"TRUE", "GOOD", "HIDDEN"}   # '용기·성장' 계열


def _f(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def pct(n, d):
    return round(100.0 * n / d, 1) if d else 0.0


def is_thinking(mbti):
    return len(mbti) >= 3 and mbti[2].upper() == "T"


def is_feeling(mbti):
    return len(mbti) >= 3 and mbti[2].upper() == "F"


def load_rows():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("ending")]


def analyze(rows):
    n = len(rows)

    # ── 모델 1: Q1 (원칙 A vs 공감 B), 성별 분해 ──
    q1 = [r for r in rows if r.get("q1") in ("A", "B")]
    q1_a = sum(1 for r in q1 if r["q1"] == "A")
    q1_b = len(q1) - q1_a
    male = [r for r in q1 if r.get("gender") == "g_m"]
    female = [r for r in q1 if r.get("gender") == "g_f"]
    model1 = {
        "n": len(q1),
        "principle_pct": pct(q1_a, len(q1)),     # 원칙(A)
        "empathy_pct": pct(q1_b, len(q1)),       # 공감(B)
        "male_principle_pct": pct(sum(1 for r in male if r["q1"] == "A"), len(male)),
        "female_principle_pct": pct(sum(1 for r in female if r["q1"] == "A"), len(female)),
        "male_n": len(male), "female_n": len(female),
        "avg_human": round(sum(_f(r.get("human")) for r in rows) / n, 1) if n else 0,
        "avg_soldier": round(sum(_f(r.get("soldier")) for r in rows) / n, 1) if n else 0,
    }

    # ── 모델 2: MBTI T/F × 엔딩·용기 ──
    t_rows = [r for r in rows if is_thinking(r.get("mbti", ""))]
    f_rows = [r for r in rows if is_feeling(r.get("mbti", ""))]
    model2 = {
        "t_n": len(t_rows), "f_n": len(f_rows),
        "t_good_ending_pct": pct(sum(1 for r in t_rows if r.get("ending") in GOOD_ENDINGS), len(t_rows)),
        "f_good_ending_pct": pct(sum(1 for r in f_rows if r.get("ending") in GOOD_ENDINGS), len(f_rows)),
        "t_avg_courage": round(sum(_f(r.get("courage")) for r in t_rows) / len(t_rows), 1) if t_rows else 0,
        "f_avg_courage": round(sum(_f(r.get("courage")) for r in f_rows) / len(f_rows), 1) if f_rows else 0,
    }

    # ── 모델 3: Q3 (이기심 A vs 이타심 B) + 인간본능 vs 공감 ──
    q3 = [r for r in rows if r.get("q3") in ("A", "B")]
    q3_a = sum(1 for r in q3 if r["q3"] == "A")
    q3_b = len(q3) - q3_a
    model3 = {
        "n": len(q3),
        "self_pct": pct(q3_a, len(q3)),          # 이기심(A)
        "altruism_pct": pct(q3_b, len(q3)),      # 이타심(B)
        "avg_instinct": round(sum(_f(r.get("instinct")) for r in rows) / n, 1) if n else 0,
        "avg_empathy": round(sum(_f(r.get("empathy")) for r in rows) / n, 1) if n else 0,
        "avg_fragments": round(sum(_f(r.get("fragments")) for r in rows) / n, 1) if n else 0,
    }

    endings = Counter(r.get("ending") for r in rows)
    ending_dist = [{"code": c, "count": endings.get(c, 0), "pct": pct(endings.get(c, 0), n)}
                   for c in ENDING_ORDER if endings.get(c, 0) or c in endings]
    # 정의된 순서 외 코드도 포함
    for c in endings:
        if c not in ENDING_ORDER:
            ending_dist.append({"code": c, "count": endings[c], "pct": pct(endings[c], n)})

    return {
        "sample_size": n,
        "ending_distribution": ending_dist,
        "model1": model1,
        "model2": model2,
        "model3": model3,
    }


def build_report():
    rows = load_rows()
    data = analyze(rows)
    report = {
        "generated_by": "analyze.py",
        "source_file": "results.csv",
        "sample_size": data["sample_size"],
        "reference": REFERENCE,
        "data": data,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


def print_report(report):
    d = report["data"]
    n = report["sample_size"]
    line = "=" * 64
    print(line)
    print(f" 붉은 무공훈장 — 학술 비교 분석 리포트   (표본 n = {n})")
    print(f" 데이터 출처: results.csv   ·   생성: analyze.py")
    print(line)
    if n == 0:
        print(" 아직 누적된 플레이 데이터가 없습니다. 게임을 플레이하면 자동 기록됩니다.")
        return

    print("\n[모델 1] 콜버그·길리건  —  원칙 vs 공감  (Q1)")
    m1 = d["model1"]
    print(f"  · 기준선 : 인습적 수준(규칙 우선) 청소년 ≈ 65%")
    print(f"            └ 출처: Colby, Kohlberg, Gibbs & Lieberman (1983), Monographs SRCD 48")
    print(f"  · 우리   : 원칙(A) {m1['principle_pct']}%  /  공감(B) {m1['empathy_pct']}%   (n={m1['n']})")
    print(f"  · 성차   : 남 원칙 {m1['male_principle_pct']}%(n={m1['male_n']}) · 여 원칙 {m1['female_principle_pct']}%(n={m1['female_n']})")
    print(f"  · 저울   : 인간 {m1['avg_human']}  /  군인 {m1['avg_soldier']} (평균)")

    print("\n[모델 2] MBTI  —  T vs F  ×  엔딩·용기")
    m2 = d["model2"]
    print(f"  · 기준선 : 남 T선호 56.5% · 여 F선호 75.5%")
    print(f"            └ 출처: Myers et al. (1998), MBTI Manual 3rd ed., CPP")
    print(f"  · T형(n={m2['t_n']}) 진엔딩 도달 {m2['t_good_ending_pct']}% · 평균 용기 {m2['t_avg_courage']}")
    print(f"  · F형(n={m2['f_n']}) 진엔딩 도달 {m2['f_good_ending_pct']}% · 평균 용기 {m2['f_avg_courage']}")

    print("\n[모델 3] 트롤리·행동경제학  —  이기심 vs 이타심  (Q3)")
    m3 = d["model3"]
    print(f"  · 기준선 : 독재자 게임 평균 양보 28.3% (익명 시 이기심↑)")
    print(f"            └ 출처: Engel (2011), Experimental Economics 14(4)")
    print(f"  · 우리   : 이기심(A) {m3['self_pct']}%  /  이타심(B) {m3['altruism_pct']}%   (n={m3['n']})")
    print(f"  · 스탯   : 인간본능 {m3['avg_instinct']}  /  공감 {m3['avg_empathy']} · 기억조각 평균 {m3['avg_fragments']}")

    print("\n[엔딩 분포]")
    for e in d["ending_distribution"]:
        print(f"  · {e['code']:<7} {e['count']:>3}건  ({e['pct']}%)")
    print("\n" + line)
    print(f" JSON 리포트 저장 완료 → {OUT_PATH}")
    print(line)


if __name__ == "__main__":
    print_report(build_report())
