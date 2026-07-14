# -*- coding: utf-8 -*-
"""
웹(Next.js) 이식용 데이터 export
=================================
story.py / i18n.py / game.py 의 게임 데이터를 하나의 JSON 으로 덤프한다.
웹 게임 엔진(web/src/game/)이 이 JSON 을 그대로 해석해 플레이한다.

  python export_web.py
  → ../web/src/data/game-data.json  생성

노드 튜플은 [kind, ...args] 리스트로 직렬화된다.
"""

import json
import os

import story
import i18n

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "src", "data", "game-data.json")

# 게임 상수 (game.py 와 동기화)
INITIAL_STATS = story.INITIAL_STATS
ALL_FRAGMENTS = ["군복", "짐의 군번줄", "붉은 손수건", "탄피", "마지막 깃발"]
FRAGMENT_ICON = {
    "군복": "clothes", "짐의 군번줄": "ballchain", "붉은 손수건": "scarf",
    "탄피": "empshell", "마지막 깃발": "flag",
}
MBTI_TYPES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
              "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
GENDER_KEYS = ["g_m", "g_f", "g_x"]
GRADE_KEYS = ["grade_1", "grade_2", "grade_3"]
MAJOR_KEYS = ["maj_ec", "maj_ej", "maj_ch", "maj_jp"]
PORTRAIT_COUNT = 16


def node_to_list(node):
    """튜플 노드를 JSON 배열로. 중첩 노드(분기/탐색/선택지)도 재귀 변환."""
    kind = node[0]
    if kind == "choice":
        # ("choice", [(label, effects, [subnodes]), ...])
        opts = []
        for label, effects, sub in node[1]:
            opts.append({
                "label": label,
                "effects": effects,
                "nodes": [node_to_list(n) for n in sub],
            })
        return ["choice", opts]
    if kind == "explore":
        # ("explore", [(name, [subnodes]), ...])
        places = []
        for name, sub in node[1]:
            places.append({
                "name": name,
                "nodes": [node_to_list(n) for n in sub],
            })
        return ["explore", places]
    if kind == "cond":
        # ("cond", (key, op, val), [then], [else])
        key, op, val = node[1]
        then_nodes = [node_to_list(n) for n in node[2]]
        else_nodes = [node_to_list(n) for n in node[3]] if len(node) > 3 else []
        return ["cond", [key, op, val], then_nodes, else_nodes]
    # 그 외: 그대로 배열화 (None 유지)
    return [kind] + list(node[1:])


def convert(nodes):
    return [node_to_list(n) for n in nodes]


def build():
    data = {
        "meta": {
            "title": "붉은 무공훈장",
            "subtitle": "The Weight of Courage",
            "langs": i18n.LANGS,
            "langNative": i18n.LANG_NATIVE,
        },
        "constants": {
            "initialStats": INITIAL_STATS,
            "allFragments": ALL_FRAGMENTS,
            "fragmentIcon": FRAGMENT_ICON,
            "mbtiTypes": MBTI_TYPES,
            "genderKeys": GENDER_KEYS,
            "gradeKeys": GRADE_KEYS,
            "majorKeys": MAJOR_KEYS,
            "portraitCount": PORTRAIT_COUNT,
            "surveyDims": list(i18n.SURVEY_DIMS),
            "surveyVariantCount": i18n.SURVEY_VARIANT_COUNT,
        },
        "story": convert(story.STORY),
        "endings": {code: convert(nodes) for code, nodes in story.ENDINGS.items()},
        "i18n": {
            "UI": i18n.UI,
            "TR": i18n.TR,
            "NAMES": i18n.NAMES,
            "STAT": i18n.STAT,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    # 통계
    n_story = len(data["story"])
    n_tr = len(i18n.TR)
    n_ui = len(i18n.UI)
    print(f"[ok] story nodes : {n_story}")
    print(f"[ok] endings     : {list(data['endings'])}")
    print(f"[ok] i18n TR/UI  : {n_tr} / {n_ui}")
    print(f"[ok] saved       : {os.path.normpath(OUT)}")


if __name__ == "__main__":
    build()
