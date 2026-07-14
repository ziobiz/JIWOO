# -*- coding: utf-8 -*-
"""
붉은 무공훈장 : The Weight of Courage
pygame 비주얼 노벨 엔진 (UI/UX 리디자인 v3)

디자인 컨셉 : "한 권의 소설을 읽는 듯한" 몰입형 인터페이스
  · 세리프(바탕체) 본문 + 산세리프(맑은고딕) UI 라벨
  · 시네마 레터박스 · 비네트 · 장면 크로스페이드 전환
  · 하단 그라데이션 대사창(테두리 없는 몰입형) · 우아한 이름표
  · 마우스/키보드(↑↓·Enter·숫자키) 겸용 선택 UX

실행:  python game.py       (TAB: 스탯 패널, ESC: 종료)
필요:  pip install pygame-ce
"""
import io
import os
import sys
import csv
import math
import json
import time

try:
    import pygame
except ImportError:
    print("pygame 이 필요합니다.  터미널에서:  pip install pygame-ce")
    sys.exit(1)

import i18n

# ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 60
TYPE_SPEED = 46          # 초당 글자 수
FONT_FILE = None

if getattr(sys, "frozen", False):
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")
SAVE_PATH = os.path.join(HERE, "savegame.json")
SETTINGS_PATH = os.path.join(HERE, "settings.json")

# ── 팔레트 (따뜻한 양피지 / 잉크) ──────────────────────
INK        = (16, 14, 12)
PARCH      = (234, 225, 207)     # 본문 (따뜻한 미색)
PARCH_DIM  = (188, 179, 162)
GOLD       = (203, 165, 92)
GOLD_SOFT  = (161, 132, 80)
BLUE       = (150, 186, 224)
GRAY       = (150, 145, 136)
RED        = (172, 62, 54)
GREEN      = (132, 170, 122)
PANEL_BG   = (18, 17, 15)

# 하위 호환용 별칭 (엔진 내부에서 쓰던 이름)
WHITE = PARCH
BLACK = INK
BOX_BG = (13, 12, 10)

STAT_COLOR = {
    "신뢰": (205, 152, 92),
    "공감": (150, 186, 224),
    "인간본능": (132, 178, 128),
    "사회적역할": (152, 154, 194),
    "죄책감": (180, 92, 92),
    "용기": (203, 165, 92),
}
STAT_LABEL = {
    "신뢰": "신뢰도", "공감": "공감",
    "인간본능": "인간 본능", "사회적역할": "사회적 역할",
    "죄책감": "죄책감", "용기": "용기",
}
HUD_GROUPS = [
    ("grp_relation", ["신뢰", "공감"]),      # 헨리 ↔ 플레이어 관계
    ("grp_player", ["인간본능", "사회적역할"]),  # 플레이어 능력치
    ("grp_henry", ["죄책감", "용기"]),        # 헨리의 상태
]
ALL_FRAGMENTS = ["군복", "짐의 군번줄", "붉은 손수건", "탄피", "마지막 깃발"]

# ── 캐릭터 생성 옵션 (i18n 키) ─────────────────────────
MBTI_TYPES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP",
              "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
GENDER_KEYS = ["g_m", "g_f", "g_x"]
GRADE_KEYS = ["grade_1", "grade_2", "grade_3"]     # 학년 (1·2·3학년)
MAJOR_KEYS = ["maj_ec", "maj_ej", "maj_ch", "maj_jp"]
PORTRAIT_COUNT = 16                                # 유화풍 초상 프리셋 개수
# ── (구) 벡터 아바타 폴백용 상수 ──
FACE_KEYS = ["round", "square"]
HAIR_COUNT = 5
HAIR_COLORS = [(38, 30, 26), (96, 62, 40), (170, 132, 74),
               (78, 80, 88), (150, 96, 128)]
SKIN = (238, 205, 176)
NAME_MAX = {"KR": 5, "JP": 5, "CH": 5, "EN": 10}   # 언어별 이름 글자수 제한

IMG_BASE = {
    "henry": "henry", "jim": "jim", "wilson": "wilson",
    "henry_afraid": "henry_afraid", "henry_brave": "henry_brave",
    "henry_guilt": "henry_guilt", "henry_grief": "henry_grief",
    "henry_hope": "henry_hope", "henry_warm": "henry_warm", "henry_hurt": "henry_hurt",
    "commander": "commander", "soldier": "soldier", "daniel": "daniel",
    "mark": "mark", "veteran": "veteran", "wounded": "wounded", "medic": "medic",
    "player1": "player(1)", "player2": "player(2)",
    "talk": "talk",
    "clothes": "clothes", "ballchain": "ballchain", "scarf": "scarf",
    "empshell": "empshell", "flag": "flag",
}

# 화자(원문 이름) → 좌측 유화풍 초상 키. 헨리는 대사 감정으로 변형 선택.
SPEAKER_PORTRAIT = {
    "헨리": "henry", "윌슨": "wilson", "짐": "jim",
    "지휘관": "commander", "병사": "soldier", "병사A": "soldier", "병사B": "soldier",
    "대니얼": "daniel", "마크": "mark", "노병": "veteran",
    "부상병": "wounded", "의무병": "medic",
}
# 헨리 감정 분류: 위에서부터 우선순위대로 검사 (구체적 상태 우선).
#   hurt(배드엔딩 상처) → warm(감사·치유) → grief(짐의 죽음/비탄)
#   → guilt(도망·겁쟁이·죄책감) → brave(결의) → afraid(공포) → hope(희망) → neutral
_HENRY_EMOTION = [
    ("henry_hurt",   ("겁쟁이로만", "다른 사람들처럼", "날 겁쟁이로")),
    ("henry_warm",   ("미워하지 않아", "용서", "들려주고 싶", "듣고 싶었", "고마워",
                      "네가 있어서", "이제 나는")),
    ("henry_grief",  ("짐이", "돌아오지 못한", "죽었잖아", "끝까지 싸우다", "먼저 떠올")),
    ("henry_guilt",  ("겁쟁이", "비겁", "죄인", "도망쳤", "비웃", "도망친")),
    ("henry_brave",  ("버텨", "앞으로", "이번엔", "이번에", "내가 가", "구하자",
                      "같이 들자", "지킬", "해낼", "가자", "알겠어")),
    ("henry_afraid", ("무섭", "무서", "두려", "겁나", "도망가고 싶", "도망칠까", "떨려")),
    ("henry_hope",   ("믿어 볼게", "버틸 수 있", "그러길 바라", "다행", "정말?", "바랄게")),
]


def resolve_speaker_portrait(speaker, text):
    """화자와 대사 내용을 분석해 좌측에 세울 초상 키를 결정."""
    if not speaker or speaker == "나":
        return None
    base = SPEAKER_PORTRAIT.get(speaker)
    if base == "henry":
        t = text or ""
        for key, kws in _HENRY_EMOTION:
            if any(k in t for k in kws):
                return key
        return "henry"
    return base
for i in range(1, 17):
    IMG_BASE[f"bg{i}"] = f"bg({i})"
for i in range(1, 17):
    IMG_BASE[f"portrait{i}"] = f"portrait{i}"
for k in ("end_true", "end_good", "end_normal", "end_bad", "end_hidden"):
    IMG_BASE[k] = k

FRAGMENT_ICON = {
    "군복": "clothes", "짐의 군번줄": "ballchain", "붉은 손수건": "scarf",
    "탄피": "empshell", "마지막 깃발": "flag",
}
CAMP_BGS = {"bg6", "bg7", "bg8", "bg10", "bg11"}
CARD_ACCENT = {
    "time": GRAY, "mission": GOLD, "system": BLUE,
    "quest": GREEN, "item": GOLD, "question": PARCH, "fear": RED,
}

# ────────────────────────────────────────────────────────────────
pygame.init()
pygame.display.set_caption("붉은 무공훈장 : The Weight of Courage")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# ── 폰트 : 언어별 세리프(본문) + 산세리프(UI) ───────────
#   KR 한글 · EN 라틴 · CH 중문(간체) · JP 일문 글리프를 각각 지원하는 폰트
_FD = r"C:\Windows\Fonts"
FONT_SETS = {
    "KR": {"serif": ["batang.ttc", "gungsuh.ttc"],
           "sans":  ["malgun.ttf"], "sans_bd": ["malgunbd.ttf", "malgun.ttf"]},
    "EN": {"serif": ["georgia.ttf", "times.ttf", "batang.ttc"], "serif_bd": ["georgiab.ttf", "timesbd.ttf"],
           "sans":  ["segoeui.ttf", "arial.ttf"], "sans_bd": ["segoeuib.ttf", "arialbd.ttf", "arial.ttf"]},
    "CH": {"serif": ["simsun.ttc", "msyh.ttc"],
           "sans":  ["msyh.ttc", "simsun.ttc"], "sans_bd": ["msyhbd.ttc", "msyh.ttc"]},
    "JP": {"serif": ["yumin.ttf", "msmincho.ttc", "YuGothM.ttc"], "serif_bd": ["yumin.ttf"],
           "sans":  ["YuGothM.ttc", "YuGothR.ttc", "msgothic.ttc"], "sans_bd": ["YuGothM.ttc", "YuGothR.ttc"]},
}
_FALLBACK = ["malgun.ttf", "arial.ttf", "batang.ttc"]


def _font_path(serif, bold, lang):
    fs = FONT_SETS.get(lang, FONT_SETS["KR"])
    if serif:
        cands = (fs.get("serif_bd", []) if bold else []) + fs.get("serif", [])
    else:
        cands = (fs.get("sans_bd", []) if bold else []) + fs.get("sans", [])
    for name in cands + _FALLBACK:
        p = os.path.join(_FD, name)
        if os.path.exists(p):
            return p, name
    return None, None


_FONT_CACHE = {}


def _script_lang(s):
    """문자열의 문자로부터 알맞은 글꼴 언어를 추정 (이름 등 고유명사용)."""
    for ch in s or "":
        o = ord(ch)
        if 0x3040 <= o <= 0x30FF:            # 가나 → 일본어 글꼴
            return "JP"
        if 0xAC00 <= o <= 0xD7A3:            # 한글
            return "KR"
        if 0x4E00 <= o <= 0x9FFF:            # 한자
            return "CH"
    return "EN"


def get_font(size, bold=False, serif=False, lang=None):
    lang = lang or i18n.current
    key = (size, bold, serif, lang)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path, name = _font_path(serif, bold, lang)
    if path:
        f = pygame.font.Font(path, size)
        # 볼드 파일이 따로 없는 폰트(바탕/명조/유고딕 등)는 합성 볼드로 보강
        if bold and name and not name.lower().endswith(("b.ttf", "bd.ttf", "bd.ttc")):
            f.set_bold(True)
    else:
        f = pygame.font.SysFont("malgungothic,batang,gulim,arial", size, bold=bold)
    _FONT_CACHE[key] = f
    return f


def fit_font(text, base_size, max_w, bold=False, serif=False, min_size=18, lang=None):
    """text 가 max_w 를 넘지 않도록 폰트 크기를 줄여서 반환."""
    size = base_size
    while size > min_size:
        f = get_font(size, bold=bold, serif=serif, lang=lang)
        if f.size(text)[0] <= max_w:
            return f
        size -= 2
    return get_font(min_size, bold=bold, serif=serif, lang=lang)


def name_font(name, size, bold=False, serif=True):
    """플레이어 이름 등 고유명사를 그 문자에 맞는 글꼴로 렌더."""
    return get_font(size, bold=bold, serif=serif, lang=_script_lang(name))


# ── 이미지 로드 ──────────────────────────────────────
_IMG_CACHE = {}
_ASSET_INDEX = None
_IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
_GRAD_CACHE = {}


def _find_asset(key):
    global _ASSET_INDEX
    if _ASSET_INDEX is None:
        _ASSET_INDEX = {}
        if os.path.isdir(ASSET_DIR):
            for fn in os.listdir(ASSET_DIR):
                stem, ext = os.path.splitext(fn)
                if ext.lower() in _IMG_EXTS:
                    _ASSET_INDEX[stem.lower()] = os.path.join(ASSET_DIR, fn)
    base = IMG_BASE.get(key)
    if not base:
        return None
    return _ASSET_INDEX.get(base.lower())


def _safe_load(path):
    with open(path, "rb") as f:
        data = f.read()
    return pygame.image.load(io.BytesIO(data), path)


def _placeholder(key):
    """이미지가 없을 때: 톤 있는 그라데이션 + 라벨 (조잡하지 않게)."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    h = (abs(hash(key)) % 360)
    top = pygame.Color(0); top.hsva = (h, 30, 30, 100)
    bot = pygame.Color(0); bot.hsva = (h, 40, 12, 100)
    for y in range(HEIGHT):
        r = y / HEIGHT
        col = (int(top.r + (bot.r - top.r) * r),
               int(top.g + (bot.g - top.g) * r),
               int(top.b + (bot.b - top.b) * r))
        pygame.draw.line(surf, col, (0, y), (WIDTH, y))
    label = get_font(30, serif=True).render(i18n.ui("placeholder"), True, (210, 205, 195))
    surf.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    return surf


def load_bg(key):
    ck = ("bg", key)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    if path:
        try:
            img = pygame.transform.smoothscale(_safe_load(path).convert(), (WIDTH, HEIGHT))
        except Exception as e:
            print(f"[경고] 배경 로드 실패 {path}: {e}")
            img = _placeholder(key)
    else:
        img = _placeholder(key)
    _IMG_CACHE[ck] = img
    return img


def _edge_gradients(w, h):
    """캐릭터 페더링용 알파 그라데이션(하단·상단·좌우) 캐시."""
    if (w, h) in _GRAD_CACHE:
        return _GRAD_CACHE[(w, h)]
    g = pygame.Surface((w, h), pygame.SRCALPHA)
    g.fill((255, 255, 255, 255))
    fb = max(1, int(h * 0.20))          # 하단 페이드
    for i in range(fb):
        a = int(255 * (i / fb))
        pygame.draw.line(g, (255, 255, 255, a), (0, h - 1 - i), (w, h - 1 - i))
    ft = max(1, int(h * 0.05))          # 상단 살짝
    for i in range(ft):
        a = int(255 * (i / ft))
        pygame.draw.line(g, (255, 255, 255, a), (0, i), (w, i))
    side = pygame.Surface((w, h), pygame.SRCALPHA)
    side.fill((255, 255, 255, 255))
    fs = max(1, int(w * 0.10))
    for i in range(fs):
        a = int(255 * (i / fs))
        pygame.draw.line(side, (255, 255, 255, a), (i, 0), (i, h))
        pygame.draw.line(side, (255, 255, 255, a), (w - 1 - i, 0), (w - 1 - i, h))
    _GRAD_CACHE[(w, h)] = (g, side)
    return g, side


def load_char(key):
    ck = ("char", key)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    img = None
    if path:
        try:
            src = _safe_load(path).convert_alpha()
            target_h = int(HEIGHT * 0.82)
            ratio = target_h / src.get_height()
            target_w = int(src.get_width() * ratio)
            if target_w > WIDTH * 0.58:
                target_w = int(WIDTH * 0.58)
                ratio = target_w / src.get_width()
                target_h = int(src.get_height() * ratio)
            img = pygame.transform.smoothscale(src, (target_w, target_h)).convert_alpha()
            # 가장자리 페더링 → 배경과 자연스럽게 녹아든다
            vg, sg = _edge_gradients(img.get_width(), img.get_height())
            img.blit(vg, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            img.blit(sg, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        except Exception as e:
            print(f"[경고] 캐릭터 로드 실패 {path}: {e}")
            img = None
    if img is None:
        img = pygame.Surface((360, 520), pygame.SRCALPHA)
        pygame.draw.rect(img, (46, 44, 52, 210), (0, 0, 360, 520), border_radius=20)
        pygame.draw.rect(img, (150, 145, 136, 255), (0, 0, 360, 520), 2, border_radius=20)
        label = get_font(28, serif=True).render(key, True, PARCH)
        img.blit(label, label.get_rect(center=(180, 260)))
    _IMG_CACHE[ck] = img
    return img


def load_ui(key, size):
    ck = ("ui", key, size)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    img = None
    if path:
        try:
            img = pygame.transform.smoothscale(_safe_load(path).convert_alpha(), size)
        except Exception:
            img = None
    _IMG_CACHE[ck] = img
    return img


def load_icon(frag_name, px=44):
    key = FRAGMENT_ICON.get(frag_name)
    if not key:
        return None
    ck = ("icon", key, px)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    img = None
    if path:
        try:
            img = pygame.transform.smoothscale(_safe_load(path).convert_alpha(), (px, px))
        except Exception:
            img = None
    _IMG_CACHE[ck] = img
    return img


# ── 비네트(장면 가장자리 어둠) 사전 생성 ────────────────
def _make_vignette():
    v = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    edge, depth_x, depth_y = 150, int(WIDTH * 0.34), int(HEIGHT * 0.40)
    for i in range(depth_y):                 # 상/하
        a = int(edge * ((depth_y - i) / depth_y) ** 2)
        pygame.draw.line(v, (0, 0, 0, a), (0, i), (WIDTH, i))
        pygame.draw.line(v, (0, 0, 0, a), (0, HEIGHT - 1 - i), (WIDTH, HEIGHT - 1 - i))
    for i in range(depth_x):                 # 좌/우
        a = int(edge * ((depth_x - i) / depth_x) ** 2 * 0.7)
        pygame.draw.line(v, (0, 0, 0, a), (i, 0), (i, HEIGHT))
        pygame.draw.line(v, (0, 0, 0, a), (WIDTH - 1 - i, 0), (WIDTH - 1 - i, HEIGHT))
    return v


VIGNETTE = _make_vignette()


# ── 오디오 ───────────────────────────────────────────
AUDIO_OK = False
_AMB_CHAN_ID = 15
try:
    pygame.mixer.init()
    pygame.mixer.set_num_channels(24)        # 앰비언스용 전용 채널 확보
    pygame.mixer.set_reserved(1)             # 채널 0 은 자동 재생에서 예약
    AUDIO_OK = True
except Exception as _e:
    print(f"[알림] 오디오 장치를 열 수 없어 소리 없이 실행합니다: {_e}")

_SFX_CACHE = {}
_AUDIO_EXTS = (".mp3", ".ogg", ".wav")

# 사용자 볼륨 설정 (0.0 ~ 1.0 배율) — 일시정지 메뉴에서 조절, settings.json 에 저장
settings = {"bgm": 0.8, "sfx": 0.8}


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in ("bgm", "sfx"):
            if k in data:
                settings[k] = max(0.0, min(1.0, float(data[k])))
        if data.get("lang") in i18n.LANGS:
            i18n.set_lang(data["lang"])
    except Exception:
        pass


def save_settings():
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump({"bgm": settings["bgm"], "sfx": settings["sfx"], "lang": i18n.current},
                      f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# 효과음은 "조금 작게" — 소리별 상대 음량 × 마스터
SFX_MASTER = 0.55
# 전장 사운드(포성·총성·북·나팔)는 크고 명확하게 — 높은 기준값(재생 시 [0,1] 클램프)
SFX_VOL = {
    "page": 0.45, "wind": 0.5, "bugle": 2.5, "shifting": 0.6, "heartbeat": 0.6,
    "gun": 2.4, "volley": 2.6, "bomb": 2.2, "foot": 0.55, "item": 0.6, "click": 0.32,
    "scream": 1.0, "shout": 0.55, "rustle": 0.42, "drum": 2.5, "impact": 1.6,
    "cough": 0.55, "cannon": 2.6, "splash": 0.6,
}
# 앰비언스(장소 분위기) 상대 음량 — 전장은 아비규환처럼 크게
AMB_VOL = {"warfield": 1.6, "campfire": 0.5, "wagon": 0.5, "river": 0.55}
# 배경음악 감정별 음량 (전투는 조금 크게, 애도는 은은하게)
MUSIC_VOL = {
    "prologue": 0.38, "bgm": 0.4, "campfirebgm": 0.42, "tension": 0.4,
    "battle": 0.5, "sorrow": 0.42, "hope": 0.46,
}


def _find_audio(name):
    for ext in _AUDIO_EXTS:
        p = os.path.join(ASSET_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def play_sfx(name, vol=None):
    if not AUDIO_OK:
        return
    if name not in _SFX_CACHE:
        p = _find_audio(name)
        try:
            _SFX_CACHE[name] = pygame.mixer.Sound(p) if p else None
        except Exception:
            _SFX_CACHE[name] = None
    snd = _SFX_CACHE[name]
    if snd:
        try:
            if vol is None:
                vol = SFX_VOL.get(name, 0.55) * SFX_MASTER
            snd.set_volume(vol * settings["sfx"])
            snd.play()
        except Exception:
            pass


# ── 전장 앰비언스(아비규환) : 전용 채널에서 루프 재생, BGM 위에 겹침 ──
_ambience = {"cur": None, "base_vol": 0.5}
_amb_chan = None


def _get_amb_channel():
    global _amb_chan
    if _amb_chan is None and AUDIO_OK:
        try:
            _amb_chan = pygame.mixer.Channel(_AMB_CHAN_ID)
        except Exception:
            _amb_chan = None
    return _amb_chan


def _load_sound(name):
    if name not in _SFX_CACHE:
        p = _find_audio(name)
        try:
            _SFX_CACHE[name] = pygame.mixer.Sound(p) if p else None
        except Exception:
            _SFX_CACHE[name] = None
    return _SFX_CACHE.get(name)


def play_ambience(name):
    if not AUDIO_OK or _ambience["cur"] == name:
        return
    ch = _get_amb_channel()
    snd = _load_sound(name)
    if not ch or not snd:
        return
    base = AMB_VOL.get(name, 0.5) * SFX_MASTER
    _ambience["cur"] = name
    _ambience["base_vol"] = base
    try:
        ch.set_volume(base * settings["sfx"])
        ch.play(snd, loops=-1, fade_ms=900)
    except Exception:
        pass


def stop_ambience(fade_ms=800):
    _ambience["cur"] = None
    ch = _amb_chan
    if ch:
        try:
            ch.fadeout(fade_ms)
        except Exception:
            pass


def apply_ambience_volume():
    ch = _amb_chan
    if ch and _ambience["cur"]:
        try:
            ch.set_volume(_ambience["base_vol"] * settings["sfx"])
        except Exception:
            pass


_music = {"cur": None, "base": None, "base_on": False, "base_vol": 0.4}


def apply_music_volume():
    """현재 재생 중인 BGM 볼륨을 사용자 설정에 맞춰 갱신."""
    if AUDIO_OK:
        try:
            pygame.mixer.music.set_volume(_music["base_vol"] * settings["bgm"])
        except Exception:
            pass


def _pump_wait(ms):
    """짧은 대기(이벤트 펌프 유지). 오디오 페이드가 실제로 진행되도록 블로킹."""
    end = pygame.time.get_ticks() + ms
    while pygame.time.get_ticks() < end:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        clock.tick(FPS)


def _play_music_file(name, vol=None):
    """감정선에 맞춰 곡을 전환 : 이전 곡을 실제로 페이드아웃(무음까지 딥)한 뒤
    새 곡을 페이드인 → 감성적인 크로스-딥 전환. 같은 곡이면 유지."""
    if not AUDIO_OK or _music["cur"] == name:
        return
    p = _find_audio(name)
    if not p:
        return
    if vol is None:
        vol = MUSIC_VOL.get(name, 0.4)
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(420)      # 이전 곡을 실제 무음까지 낮춤
            _pump_wait(440)                       # 페이드가 끝날 시간을 확보
    except Exception:
        pass
    try:
        pygame.mixer.music.load(p)
        _music["base_vol"] = vol
        pygame.mixer.music.set_volume(vol * settings["bgm"])
        pygame.mixer.music.play(-1, fade_ms=1000)  # 새 곡 페이드인
        _music["cur"] = name
    except Exception:
        pass


def start_base_bgm(name="bgm"):
    _music["base"] = name
    _music["base_on"] = True
    _play_music_file(name)


def update_bgm_for_bg(bgkey):
    """배경 전환 시 호출. BGM 은 story 의 ('bgm', ...) 노드로 명시 제어하므로
    여기서는 자동 전환하지 않는다(감정선 유지). 하위 호환용으로만 남김."""
    return


# ────────────────────────────────────────────────────────────────
class Scene:
    bg_key = None
    char_key = None
    char_pos = "center"


stats = {}
conflict = {"인간": 0, "군인": 0}
items = []
toasts = []

PROFILE_PATH = os.path.join(HERE, "profile.json")
RESULT_PATH = os.path.join(HERE, "results.csv")
SURVEY_SEEN_PATH = os.path.join(HERE, "survey_seen.json")


def default_profile():
    return {
        "name": "", "gender": "g_x", "grade": "grade_1", "major": "maj_ec", "mbti": "INTJ",
        "portrait": 0,
        "survey": {"q1": None, "q2": None, "q3": None},
    }


profile = default_profile()


def _load_survey_seen():
    if not os.path.exists(SURVEY_SEEN_PATH):
        return {}
    try:
        with open(SURVEY_SEEN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_survey_seen(seen):
    try:
        with open(SURVEY_SEEN_PATH, "w", encoding="utf-8") as f:
            json.dump(seen, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def pick_survey_variants():
    """유형당 미사용 변종 1개씩. 5개 소진 시 리셋(직전 문항 제외)."""
    import random as _rnd
    seen = _load_survey_seen()
    picks = {}
    n = i18n.SURVEY_VARIANT_COUNT
    for dim in i18n.SURVEY_DIMS:
        used = [int(x) for x in seen.get(dim, []) if str(x).isdigit() and 1 <= int(x) <= n]
        pool = [i for i in range(1, n + 1) if i not in used]
        if not pool:
            last = used[-1] if used else None
            used = []
            pool = [i for i in range(1, n + 1) if i != last] or list(range(1, n + 1))
        v = _rnd.choice(pool)
        picks[dim] = v
        if v not in used:
            used.append(v)
        seen[dim] = used
    _save_survey_seen(seen)
    return picks


def apply_profile_name():
    i18n.set_player_name(profile.get("name", ""))


def save_profile():
    try:
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[경고] 프로필 저장 실패: {e}")


def load_profile():
    if not os.path.exists(PROFILE_PATH):
        return False
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = default_profile()
        base.update({k: data.get(k, base[k]) for k in base})
        base["survey"] = {**base["survey"], **(data.get("survey") or {})}
        profile.clear(); profile.update(base)
        apply_profile_name()
        return True
    except Exception as e:
        print(f"[경고] 프로필 불러오기 실패: {e}")
        return False
hud_visible = True
letterbox = 0.0          # 0~1 시네마 레터박스 양
_player_turn = False     # 현재 대사 화자가 '나'(플레이어)인지 — 좌측 아바타 표시용
_speaker_portrait = None  # 현재 대사 화자(NPC)의 좌측 초상 키

dialog_log = []          # 대사 백로그 [(name, text, color), ...]
progress = {"index": 0}  # STORY 최상위 노드 진행 인덱스(세이브 지점)
in_game = False          # 실제 플레이 중일 때만 ESC=일시정지 / 휠=백로그
_MAX_LOG = 300

# 세이브 체크포인트 : "노드 시작 시점" 상태를 스냅샷해 두어, 로드 후 재실행 시
# 선택지 효과가 두 번 적용되는 문제(스탯 중복)를 방지한다.
_checkpoint = {}
_chapter_label = ""      # 현재 챕터 제목(원문) — 세이브 캡션용
_pending_fadein = False  # 로드 직후 장면을 페이드인으로 등장시킬지


# ── 흐름 제어 예외 (일시정지 메뉴 → 언와인드) ────────────
class ReturnToTitle(Exception):
    """일시정지 메뉴에서 '메인 화면으로' 선택 시."""


class ReloadStory(Exception):
    """일시정지 메뉴에서 '불러오기' 성공 시(상태는 이미 적용됨)."""


def _toast(text, color):
    toasts.append([text, color, pygame.time.get_ticks() + 1900])


def apply_effects(changes):
    for k, v in changes.items():
        if k in ("인간", "군인"):
            conflict[k] = max(0, conflict[k] + v)
            label = i18n.ui("conflict_human") if k == "인간" else i18n.ui("conflict_soldier")
            _toast(f"{label} {'+' if v >= 0 else ''}{v}",
                   GREEN if k == "인간" else STAT_COLOR["사회적역할"])
        else:
            stats[k] = max(0, min(100, stats.get(k, 0) + v))
            if k != "전쟁체험도":
                sign = "+" if v >= 0 else ""
                _toast(f"{i18n.stat(k)} {sign}{v}", GREEN if v >= 0 else RED)


def grant_item(name):
    if name not in items:
        items.append(name)
        _toast(i18n.ui("frag_toast", name=i18n.t(name)), GOLD)
        # 획득 효과음은 앞선 '기억 조각 획득' 연출(show_fragment_get)에서 재생하므로
        # 여기서는 중복 재생하지 않는다.


# ── 텍스트 줄바꿈 ────────────────────────────────────
def wrap_text(text, font, max_w):
    lines = []
    for para in text.split("\n"):
        if para == "":
            lines.append("")
            continue
        cur = ""
        for ch in para:
            if font.size(cur + ch)[0] <= max_w:
                cur += ch
            else:
                if " " in cur.rstrip() and ch != " ":
                    idx = cur.rstrip().rfind(" ")
                    lines.append(cur[:idx])
                    cur = cur[idx + 1:] + ch
                else:
                    lines.append(cur)
                    cur = ch
        lines.append(cur)
    return lines


def _text_shadow(font, text, color, ox, oy, shadow=(0, 0, 0), sa=150):
    sh = font.render(text, True, shadow)
    sh.set_alpha(sa)
    screen.blit(sh, (ox + 2, oy + 2))
    screen.blit(font.render(text, True, color), (ox, oy))


# ── 장면 그리기 ──────────────────────────────────────
# ── 플레이어 아바타 (절차적 벡터 초상) ─────────────────
_avatar_cache = {}


def _dark(c, f=0.62):
    return tuple(max(0, int(x * f)) for x in c)


def _lite(c, f=1.22):
    return tuple(min(255, int(x * f)) for x in c)


def render_avatar(size, look, gender="g_x"):
    """머리 스타일·색, 안경, 헤어밴드, 얼굴형, 성별에 따라 초상(버스트)을 그린다."""
    style = look.get("hair", 0) % HAIR_COUNT
    face = look.get("face", "round")
    key = (size, style, look.get("haircol", 0), bool(look.get("glasses")),
           bool(look.get("band")), face, gender)
    if key in _avatar_cache:
        return _avatar_cache[key]

    S = size
    surf = pygame.Surface((S, S), pygame.SRCALPHA)
    cx = S // 2
    hair = HAIR_COLORS[look.get("haircol", 0) % len(HAIR_COLORS)]
    cloth = {"g_m": (72, 84, 116), "g_f": (156, 92, 112)}.get(gender, (96, 92, 112))

    hy = int(S * 0.44); hw = int(S * 0.235); hh = int(S * 0.285)
    top = hy - hh

    # 어깨/상의 (버스트)
    pygame.draw.ellipse(surf, cloth, (cx - int(S * 0.40), int(S * 0.82), int(S * 0.80), int(S * 0.46)))
    pygame.draw.ellipse(surf, _lite(cloth, 1.12), (cx - int(S * 0.40), int(S * 0.82), int(S * 0.80), int(S * 0.16)))
    # 목
    pygame.draw.rect(surf, _dark(SKIN, 0.9), (cx - int(S * 0.058), hy + hh - int(S * 0.05), int(S * 0.116), int(S * 0.15)))

    # 뒷머리 (긴 스타일은 어깨까지)
    if style in (2, 3):
        bh = int(S * 0.58) if style == 2 else int(S * 0.42)
        pygame.draw.ellipse(surf, _dark(hair, 0.82),
                            (cx - hw - int(S * 0.04), top + int(S * 0.02), 2 * hw + int(S * 0.08), bh + hh))

    # 머리 윗부분(캡)
    bang = {0: 0.30, 1: 0.24, 2: 0.34, 3: 0.32, 4: 0.10}[style]
    cap = pygame.Rect(cx - hw - int(S * 0.012), top - int(S * 0.02),
                      2 * hw + int(S * 0.024), int(hh * 1.35))
    if style == 4:                                   # 아주 짧은 머리
        pygame.draw.ellipse(surf, hair, (cx - hw, top, 2 * hw, int(hh * 0.9)))
    elif face == "square":
        pygame.draw.rect(surf, hair, cap, border_radius=int(S * 0.10))
    else:
        pygame.draw.ellipse(surf, hair, cap)

    # 얼굴 (뱅 아래로 내려 이마를 머리로 덮음)
    foff = int(hh * bang)
    fw = int(hw * (0.94 if style == 4 else 0.86))
    frect = (cx - fw, top + foff, 2 * fw, 2 * hh - foff)
    if face == "square":
        pygame.draw.rect(surf, SKIN, frect, border_radius=int(S * 0.085))
    else:
        pygame.draw.ellipse(surf, SKIN, frect)

    # 귀
    er = int(S * 0.032)
    pygame.draw.circle(surf, _dark(SKIN, 0.95), (cx - fw, hy + int(S * 0.02)), er)
    pygame.draw.circle(surf, _dark(SKIN, 0.95), (cx + fw, hy + int(S * 0.02)), er)

    # 보브: 볼 옆 머리
    if style == 3:
        for sx in (cx - hw, cx + hw - int(hw * 0.42)):
            pygame.draw.rect(surf, hair, (sx, top + int(hh * 0.5), int(hw * 0.42), int(hh * 1.3)),
                             border_radius=int(S * 0.05))

    # 눈
    ey = hy + int(hh * 0.16); ex = int(fw * 0.5); ew = int(S * 0.05); eh = int(S * 0.06)
    for sx in (cx - ex, cx + ex):
        pygame.draw.ellipse(surf, (250, 250, 250), (sx - ew, ey - eh // 2, 2 * ew, eh))
        pygame.draw.circle(surf, (46, 36, 32), (sx, ey), int(ew * 0.8))
        pygame.draw.circle(surf, (250, 250, 250), (sx + 2, ey - 2), max(1, int(ew * 0.28)))
        # 눈썹
        pygame.draw.line(surf, _dark(hair, 0.7), (sx - ew, ey - eh), (sx + ew, ey - eh - 2), 3)

    # 코 · 입
    pygame.draw.line(surf, _dark(SKIN, 0.8), (cx, hy + int(hh * 0.30)), (cx + int(S * 0.012), hy + int(hh * 0.42)), 2)
    mouth = (188, 96, 96) if gender == "g_f" else (170, 110, 96)
    pygame.draw.arc(surf, mouth, (cx - int(S * 0.05), hy + int(hh * 0.42), int(S * 0.10), int(S * 0.09)),
                    math.pi + 0.4, 2 * math.pi - 0.4, 3)
    if gender == "g_f":                              # 볼터치
        for sx in (cx - int(fw * 0.7), cx + int(fw * 0.7)):
            bl = pygame.Surface((int(S * 0.09), int(S * 0.05)), pygame.SRCALPHA)
            pygame.draw.ellipse(bl, (230, 150, 150, 90), bl.get_rect())
            surf.blit(bl, (sx - int(S * 0.045), hy + int(hh * 0.30)))

    # 안경
    if look.get("glasses"):
        gr = int(S * 0.072)
        col = (54, 48, 44)
        for sx in (cx - ex, cx + ex):
            pygame.draw.rect(surf, col, (sx - gr, ey - gr + 4, 2 * gr, 2 * gr - 6), 3, border_radius=int(S * 0.03))
        pygame.draw.line(surf, col, (cx - ex + gr, ey), (cx + ex - gr, ey), 3)
        pygame.draw.line(surf, col, (cx - ex - gr, ey - 2), (cx - fw, ey - 4), 3)
        pygame.draw.line(surf, col, (cx + ex + gr, ey - 2), (cx + fw, ey - 4), 3)

    # 헤어밴드
    if look.get("band"):
        band_col = (196, 74, 68) if gender != "g_m" else (70, 120, 150)
        br = pygame.Rect(cx - hw - int(S * 0.014), top + int(hh * 0.30),
                         2 * hw + int(S * 0.028), int(hh * 0.22))
        pygame.draw.rect(surf, band_col, br, border_radius=int(S * 0.03))
        pygame.draw.rect(surf, _lite(band_col), (br.x, br.y, br.w, max(2, br.h // 3)), border_radius=int(S * 0.03))

    _avatar_cache[key] = surf
    return surf


def _portrait_raw(index):
    key = f"portrait{int(index) + 1}"
    path = _find_asset(key)
    if not path:
        return None
    try:
        return _safe_load(path).convert_alpha()
    except Exception:
        return None


def _fit_cover(raw, w, h, top_bias=0.12):
    """raw 이미지를 w×h 를 채우도록 확대 후 중앙(상단 편향) 크롭."""
    rw, rh = raw.get_size()
    scale = max(w / rw, h / rh)
    sw, sh = max(1, int(rw * scale)), max(1, int(rh * scale))
    scaled = pygame.transform.smoothscale(raw, (sw, sh))
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    ox = (sw - w) // 2
    oy = int((sh - h) * top_bias)                 # 얼굴이 상단에 오도록 위쪽을 남긴다
    out.blit(scaled, (-ox, -oy))
    return out


def portrait_cameo(index, w, h, radius=16):
    """액자형 초상 (둥근 모서리 + 금색 테두리) — 생성 화면 미리보기/썸네일용."""
    ck = ("cameo", int(index), w, h, radius)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    raw = _portrait_raw(index)
    if raw is None:
        surf.fill((30, 28, 26, 255))
        av = render_avatar(min(w, h), {}, profile.get("gender", "g_x"))
        surf.blit(av, av.get_rect(center=(w // 2, h // 2)))
    else:
        img = _fit_cover(raw, w, h)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
        img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(img, (0, 0))
    pygame.draw.rect(surf, (*GOLD_SOFT, 220), (0, 0, w, h), 2, border_radius=radius)
    _IMG_CACHE[ck] = surf
    return surf


def load_player_portrait(index):
    """플레이어 대사용 버스트 : 초상을 세로로 세우고 가장자리를 페더링해 장면에 녹인다."""
    ck = ("pbust", int(index))
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    raw = _portrait_raw(index)
    if raw is None:
        img = render_avatar(360, {}, profile.get("gender", "g_x"))
        _IMG_CACHE[ck] = img
        return img
    img = _feather_bust(raw)
    _IMG_CACHE[ck] = img
    return img


def _feather_bust(raw):
    """초상 원본을 세로 버스트로 스케일하고 사방을 페더링해 장면에 녹인다."""
    h = int(HEIGHT * 0.66)
    w = int(h * raw.get_width() / raw.get_height())
    img = pygame.transform.smoothscale(raw, (w, h)).convert_alpha()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((255, 255, 255, 255))
    for i in range(max(1, int(h * 0.22))):        # 상단
        a = int(255 * i / int(h * 0.22))
        pygame.draw.line(mask, (255, 255, 255, a), (0, i), (w, i))
    for i in range(max(1, int(h * 0.26))):        # 하단
        a = int(255 * i / int(h * 0.26))
        pygame.draw.line(mask, (255, 255, 255, a), (0, h - 1 - i), (w, h - 1 - i))
    fs = max(1, int(w * 0.16))
    side = pygame.Surface((w, h), pygame.SRCALPHA); side.fill((255, 255, 255, 255))
    for i in range(fs):                            # 좌우
        a = int(255 * i / fs)
        pygame.draw.line(side, (255, 255, 255, a), (i, 0), (i, h))
        pygame.draw.line(side, (255, 255, 255, a), (w - 1 - i, 0), (w - 1 - i, h))
    img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    img.blit(side, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return img


def load_speaker_bust(key):
    """화자 초상(에셋 키)을 좌측 버스트로 로드 (페더링, 캐시)."""
    ck = ("sbust", key)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    img = None
    if path:
        try:
            img = _feather_bust(_safe_load(path).convert_alpha())
        except Exception as e:
            print(f"[경고] 화자 초상 로드 실패 {path}: {e}")
    _IMG_CACHE[ck] = img
    return img


def draw_player_bust():
    """플레이어 대사 시 좌측에 세워지는 초상(유화풍)."""
    img = load_player_portrait(profile.get("portrait", 0))
    rect = img.get_rect()
    rect.midbottom = (int(WIDTH * 0.16), HEIGHT - 24)
    screen.blit(img, rect)


def draw_speaker_bust(key):
    """화자(NPC) 대사 시 좌측에 세워지는 초상(유화풍)."""
    img = load_speaker_bust(key)
    if img is None:
        return
    rect = img.get_rect()
    rect.midbottom = (int(WIDTH * 0.16), HEIGHT - 24)
    screen.blit(img, rect)


def draw_scene_base(vignette=True):
    if Scene.bg_key:
        screen.blit(load_bg(Scene.bg_key), (0, 0))
    else:
        screen.fill(INK)
    # 좌측 화자 버스트 : 대사 중에는 말하는 인물이 왼쪽에 등장
    left_player = _player_turn and profile.get("name")
    left_npc = (not _player_turn) and _speaker_portrait
    if Scene.char_key and not (left_player or left_npc):
        # 대사 화자 버스트가 없을 때(내레이션 등)만 중앙 장면 인물 노출
        img = load_char(Scene.char_key)
        xpos = {"left": 0.28, "center": 0.5, "right": 0.72}.get(Scene.char_pos, 0.5)
        rect = img.get_rect()
        rect.midbottom = (int(WIDTH * xpos), HEIGHT - 120)
        screen.blit(img, rect)
    if left_player:
        draw_player_bust()
    elif left_npc:
        draw_speaker_bust(_speaker_portrait)
    if vignette:
        screen.blit(VIGNETTE, (0, 0))
    _draw_letterbox()


def _draw_letterbox():
    if letterbox <= 0:
        return
    bar = int(HEIGHT * 0.12 * letterbox)
    if bar > 0:
        pygame.draw.rect(screen, INK, (0, 0, WIDTH, bar))
        pygame.draw.rect(screen, INK, (0, HEIGHT - bar, WIDTH, bar))


def _vgrad(surface, rect, top_a, bot_a, color=INK):
    """rect 영역에 세로 그라데이션(위 top_a → 아래 bot_a) 오버레이."""
    x, y, w, h = rect
    strip = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(h):
        a = int(top_a + (bot_a - top_a) * (i / max(1, h - 1)))
        pygame.draw.line(strip, (*color, a), (0, i), (w, i))
    surface.blit(strip, (x, y))


# ── 상단 HUD ─────────────────────────────────────────
_PANEL_CACHE = {}


def _panel(x, y, w, h, alpha=180, radius=12):
    """입체감 있는 라운드 패널 (그림자 + 세로 그라데이션 + 이중 테두리)."""
    body = _PANEL_CACHE.get((w, h, alpha, radius))
    if body is None:
        body = pygame.Surface((w, h), pygame.SRCALPHA)
        top, bot = (36, 33, 28), (15, 14, 12)
        for i in range(h):
            t = i / max(1, h - 1)
            col = (int(top[0] + (bot[0] - top[0]) * t),
                   int(top[1] + (bot[1] - top[1]) * t),
                   int(top[2] + (bot[2] - top[2]) * t), alpha)
            pygame.draw.line(body, col, (0, i), (w, i))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        body.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(body, (0, 0, 0, 150), body.get_rect(), 1, border_radius=radius)
        inner = body.get_rect().inflate(-2, -2)
        pygame.draw.rect(body, (*GOLD_SOFT, 120), inner, 1, border_radius=radius - 1)
        _PANEL_CACHE[(w, h, alpha, radius)] = body
    shadow = _PANEL_CACHE.get(("sh", w, h, radius))
    if shadow is None:
        shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=radius)
        _PANEL_CACHE[("sh", w, h, radius)] = shadow
    screen.blit(shadow, (x + 3, y + 5))
    screen.blit(body, (x, y))


def _bar(x, y, w, val, color, maxv=100, h=8):
    """가로 그라데이션 + 상단 하이라이트 + 눈금이 있는 스탯 바."""
    r = h // 2
    track = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(track, (38, 36, 32, 240), track.get_rect(), border_radius=r)
    pygame.draw.rect(track, (0, 0, 0, 120), track.get_rect(), 1, border_radius=r)
    screen.blit(track, (x, y))
    for tk in (0.25, 0.5, 0.75):                 # 눈금
        tx = x + int(w * tk)
        pygame.draw.line(screen, (28, 26, 23), (tx, y + 1), (tx, y + h - 1), 1)
    fw = int(w * max(0, min(1, val / maxv)))
    if fw > 0:
        fill = pygame.Surface((fw, h), pygame.SRCALPHA)
        dark = tuple(int(c * 0.5) for c in color)
        for i in range(fw):
            t = i / max(1, fw - 1)
            fill.fill((int(dark[0] + (color[0] - dark[0]) * t),
                       int(dark[1] + (color[1] - dark[1]) * t),
                       int(dark[2] + (color[2] - dark[2]) * t), 255),
                      (i, 0, 1, h))
        m = pygame.Surface((fw, h), pygame.SRCALPHA)
        pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(), border_radius=r)
        fill.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(fill, (255, 255, 255, 70), (0, 0, fw, max(1, h // 2)), border_radius=r)
        screen.blit(fill, (x, y))
        tipx = x + fw                            # 진행 끝의 밝은 캡
        cap = tuple(min(255, c + 60) for c in color)
        pygame.draw.circle(screen, cap, (tipx - r, y + r), max(2, r - 1))
    pygame.draw.rect(screen, (112, 104, 90), (x, y, w, h), 1, border_radius=r)


def _diamond(cx, cy, rad, color, filled=True):
    pts = [(cx, cy - rad), (cx + rad, cy), (cx, cy + rad), (cx - rad, cy)]
    pygame.draw.polygon(screen, color, pts, 0 if filled else 1)


def _num_badge(bx, by, text, color, align="l"):
    """숫자 배지 (어두운 라운드 + 색 테두리)."""
    f = get_font(16, bold=True)
    ts = f.render(text, True, tuple(min(255, c + 30) for c in color))
    bw, bh = ts.get_width() + 18, 24
    x0 = bx if align == "l" else bx - bw
    s = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(s, (18, 17, 15, 235), s.get_rect(), border_radius=8)
    pygame.draw.rect(s, (*color, 170), s.get_rect(), 1, border_radius=8)
    s.blit(ts, (9, bh // 2 - ts.get_height() // 2))
    screen.blit(s, (x0, by))


def draw_conflict_scale():
    """갈등 지표 : 인간 ↔ 군인 사이 마음의 긴장을 나타내는 저울(텐션 미터)."""
    x, y, w, h = 20, 16, 336, 150
    _panel(x, y, w, h, alpha=216)
    cx = x + w // 2
    green, purple = GREEN, STAT_COLOR["사회적역할"]

    pygame.draw.rect(screen, GOLD, (x + 16, y + 14, 3, 16), border_radius=2)
    screen.blit(get_font(15, bold=True).render(i18n.ui("conflict_title"), True, GOLD), (x + 26, y + 13))

    h_val, s_val = conflict["인간"], conflict["군인"]
    scale = max(100, h_val, s_val)
    max_ext = w // 2 - 26
    hlen = int(max_ext * min(1.0, h_val / scale))
    slen = int(max_ext * min(1.0, s_val / scale))

    _num_badge(x + 18, y + 40, str(h_val), green, "l")
    _num_badge(x + w - 18, y + 40, str(s_val), purple, "r")

    bar_y, bar_h = y + 76, 18
    r = bar_h // 2
    track = pygame.Surface((max_ext * 2 + 4, bar_h), pygame.SRCALPHA)
    pygame.draw.rect(track, (34, 32, 29, 245), track.get_rect(), border_radius=r)
    pygame.draw.rect(track, (0, 0, 0, 130), track.get_rect(), 1, border_radius=r)
    screen.blit(track, (cx - max_ext - 2, bar_y))

    def _fill(to_right, length, color):
        if length <= 0:
            return
        fx = cx if to_right else cx - length
        s = pygame.Surface((length, bar_h), pygame.SRCALPHA)
        for i in range(length):
            t = i / max(1, length - 1)
            d = (1 - t) if to_right else t       # 중앙에서 바깥으로의 거리
            b = 1.0 - d * 0.5                     # 중앙일수록 밝게
            s.fill((int(color[0] * b), int(color[1] * b), int(color[2] * b), 255),
                   (i, 0, 1, bar_h))
        m = pygame.Surface((length, bar_h), pygame.SRCALPHA)
        pygame.draw.rect(m, (255, 255, 255, 255), m.get_rect(), border_radius=r)
        s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        pygame.draw.rect(s, (255, 255, 255, 60), (0, 0, length, bar_h // 2), border_radius=r)
        screen.blit(s, (fx, bar_y))

    _fill(False, hlen, green)               # 인간(왼쪽)
    _fill(True, slen, purple)               # 군인(오른쪽)
    pygame.draw.rect(screen, (112, 104, 90),
                     (cx - max_ext - 2, bar_y, max_ext * 2 + 4, bar_h), 1, border_radius=r)

    # 중앙 피벗
    pygame.draw.line(screen, (86, 80, 68), (cx, bar_y - 4), (cx, bar_y + bar_h + 4), 2)

    # 기울기 표시 노브 : 우세한 쪽으로 이동
    lean = max(-1.0, min(1.0, (s_val - h_val) / scale))
    px = cx + int(max_ext * lean)
    kcol = purple if lean > 0.02 else green if lean < -0.02 else GOLD
    pygame.draw.polygon(screen, kcol,                     # 아래를 가리키는 삼각형
                        [(px, bar_y - 3), (px - 6, bar_y - 13), (px + 6, bar_y - 13)])
    pygame.draw.circle(screen, (16, 15, 13), (px, bar_y + bar_h // 2), r + 2)
    pygame.draw.circle(screen, kcol, (px, bar_y + bar_h // 2), r)
    pygame.draw.circle(screen, tuple(min(255, c + 70) for c in kcol),
                       (px, bar_y + bar_h // 2), max(2, r - 3))

    # 하단 라벨(색 칩) — 우세한 쪽 강조
    lf = get_font(13, bold=True)
    ly = y + h - 26
    lead_h = lean < -0.02
    lead_s = lean > 0.02
    pygame.draw.rect(screen, green, (x + 16, ly + 1, 3, 13), border_radius=2)
    hc = tuple(min(255, c + 30) for c in green) if lead_h else PARCH_DIM
    screen.blit(lf.render(i18n.ui("conflict_human"), True, hc), (x + 24, ly))
    ls = lf.render(i18n.ui("conflict_soldier"), True,
                   tuple(min(255, c + 30) for c in purple) if lead_s else PARCH_DIM)
    pygame.draw.rect(screen, purple, (x + w - 19, ly + 1, 3, 13), border_radius=2)
    screen.blit(ls, (x + w - 24 - ls.get_width(), ly))


def draw_gauges():
    x, w = WIDTH - 272, 256
    y = 16
    name_txt = i18n.nm("나")               # 생성한 캐릭터 이름(없으면 '나')
    name_block = 40
    h = 12 + name_block
    for gi, (_, keys) in enumerate(HUD_GROUPS):
        if gi > 0:
            h += 16                        # 그룹 사이 구분선 + 여백
        h += 26 + len(keys) * 30
    h += 58                                # 기억 조각 블록
    _panel(x, y, w, h, alpha=214)
    cy = y + 12
    # ── 플레이어(캐릭터) 이름 헤더 ──
    _diamond(x + 20, cy + 12, 5, GOLD, filled=True)
    ns = name_font(name_txt, 21, bold=True, serif=True)
    nsurf = ns.render(name_txt, True, PARCH)
    if nsurf.get_width() > w - 52:
        ns = name_font(name_txt, 17, bold=True, serif=True)
        nsurf = ns.render(name_txt, True, PARCH)
    screen.blit(nsurf, (x + 34, cy + 12 - nsurf.get_height() // 2))
    sub_txt = f"{i18n.ui(profile.get('grade', 'grade_1'))} · {i18n.ui(profile.get('major', 'maj_ec'))}"
    subf = get_font(12, bold=True).render(sub_txt, True, GOLD_SOFT)
    screen.blit(subf, (x + w - 16 - subf.get_width(), cy + 12 - subf.get_height() // 2))
    cy += 28
    pygame.draw.line(screen, (*GOLD_SOFT, 110), (x + 14, cy), (x + w - 14, cy), 1)
    cy += 12
    for gi, (header, keys) in enumerate(HUD_GROUPS):
        if gi > 0:                         # 플레이어 능력치·헨리의 상태 위에도 동일한 구분선
            cy += 6
            pygame.draw.line(screen, (*GOLD_SOFT, 90), (x + 14, cy), (x + w - 14, cy), 1)
            cy += 10
        accent = STAT_COLOR[keys[0]]
        pygame.draw.rect(screen, accent, (x + 14, cy + 1, 3, 16), border_radius=2)
        screen.blit(get_font(14, bold=True).render(i18n.ui(header), True, GOLD), (x + 24, cy))
        cy += 26
        for k in keys:
            val = stats.get(k, 0)
            screen.blit(get_font(15).render(i18n.stat(k), True, PARCH), (x + 22, cy))
            vs = get_font(14, bold=True).render(str(val), True,
                                                tuple(min(255, c + 40) for c in STAT_COLOR[k]))
            bw = vs.get_width() + 14
            bx = x + w - 16 - bw
            badge = pygame.Surface((bw, 20), pygame.SRCALPHA)
            pygame.draw.rect(badge, (0, 0, 0, 150), badge.get_rect(), border_radius=6)
            pygame.draw.rect(badge, (*STAT_COLOR[k], 130), badge.get_rect(), 1, border_radius=6)
            badge.blit(vs, (7, 10 - vs.get_height() // 2))
            screen.blit(badge, (bx, cy - 1))
            _bar(x + 22, cy + 20, w - 40, val, STAT_COLOR[k], h=9)
            cy += 30
    cy += 6
    pygame.draw.line(screen, (*GOLD_SOFT, 90), (x + 14, cy), (x + w - 14, cy), 1)
    cy += 10
    screen.blit(get_font(14, bold=True).render(
        i18n.ui("frag_hud", n=len(items), t=len(ALL_FRAGMENTS)), True, GOLD), (x + 14, cy))
    dx = x + w - 14 - len(ALL_FRAGMENTS) * 20 + 10
    tnow = pygame.time.get_ticks()
    for i, frag in enumerate(ALL_FRAGMENTS):
        got = frag in items
        dcx, dcy = dx + i * 20, cy + 8
        _diamond(dcx, dcy, 6, GOLD if got else (78, 72, 62), filled=got)
        if got:                                   # 획득한 조각은 은은하게 반짝인다
            tw = 0.5 + 0.5 * math.sin(tnow * 0.004 + i * 1.3)
            _sparkle_star(dcx, dcy, 3.5 + 3 * tw, (255, 238, 180), int(50 + 150 * tw))


def draw_toasts():
    now = pygame.time.get_ticks()
    toasts[:] = [t for t in toasts if t[2] > now]
    f = get_font(20, bold=True)
    for i, (text, col, exp) in enumerate(toasts[-4:]):
        remain = exp - now
        alpha = min(255, int(255 * remain / 600)) if remain < 600 else 235
        surf = f.render(text, True, col)
        bg = pygame.Surface((surf.get_width() + 30, surf.get_height() + 12), pygame.SRCALPHA)
        bg.fill((10, 9, 8, min(200, alpha)))
        pygame.draw.rect(bg, (*col, min(180, alpha)), bg.get_rect(), 1, border_radius=14)
        bg.blit(surf, (15, 6))
        bg.set_alpha(alpha)
        screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, 128 + i * 40))


# ── 상단 언어 선택기 (국기) ──────────────────────────
_FLAG_W, _FLAG_H, _FLAG_GAP = 30, 20, 8


def _lang_rects():
    n = len(i18n.LANGS)
    total = n * _FLAG_W + (n - 1) * _FLAG_GAP
    x0 = WIDTH // 2 - total // 2
    y = 14
    return [(pygame.Rect(x0 + i * (_FLAG_W + _FLAG_GAP), y, _FLAG_W, _FLAG_H), code)
            for i, code in enumerate(i18n.LANGS)]


def _half_disc(surf, color, cx, cy, r, top=True):
    pts = []
    steps = 20
    for i in range(steps + 1):
        a = math.pi * i / steps
        x = cx - r * math.cos(a)
        y = cy - r * math.sin(a) if top else cy + r * math.sin(a)
        pts.append((x, y))
    pygame.draw.polygon(surf, color, pts)


def _star(surf, color, cx, cy, r):
    pts = []
    for i in range(10):
        rad = r if i % 2 == 0 else r * 0.42
        ang = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    pygame.draw.polygon(surf, color, pts)


def _flag_surface(code):
    """각 언어의 국기를 간단한 벡터로 그린 Surface 반환 (둥근 모서리, 캐시)."""
    ck = ("flag", code, _FLAG_W, _FLAG_H)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    w, h = 40, 26                          # 기준 크기에서 그린 뒤 축소
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2
    if code == "KR":                       # 태극기(간략)
        s.fill((255, 255, 255))
        r = 7
        _half_disc(s, (200, 60, 60), cx, cy, r, top=True)
        _half_disc(s, (60, 90, 170), cx, cy, r, top=False)
    elif code == "EN":                     # 유니언잭(간략)
        s.fill((40, 60, 140))
        pygame.draw.line(s, (255, 255, 255), (0, 0), (w, h), 5)
        pygame.draw.line(s, (255, 255, 255), (w, 0), (0, h), 5)
        pygame.draw.line(s, (200, 50, 50), (0, 0), (w, h), 2)
        pygame.draw.line(s, (200, 50, 50), (w, 0), (0, h), 2)
        pygame.draw.rect(s, (255, 255, 255), (cx - 5, 0, 10, h))
        pygame.draw.rect(s, (255, 255, 255), (0, cy - 4, w, 8))
        pygame.draw.rect(s, (200, 50, 50), (cx - 3, 0, 6, h))
        pygame.draw.rect(s, (200, 50, 50), (0, cy - 2, w, 4))
    elif code == "CH":                     # 오성홍기(간략: 큰 별 1개)
        s.fill((222, 41, 42))
        _star(s, (255, 222, 0), 12, 9, 6)
    elif code == "JP":                     # 일장기
        s.fill((255, 255, 255))
        pygame.draw.circle(s, (200, 40, 55), (cx, cy), 8)
    s = pygame.transform.smoothscale(s, (_FLAG_W, _FLAG_H)).convert_alpha()
    mask = pygame.Surface((_FLAG_W, _FLAG_H), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=4)
    s.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    _IMG_CACHE[ck] = s
    return s


def draw_lang_selector():
    rects = _lang_rects()
    if rects:                              # 국기들을 감싸는 은은한 컨테이너
        pad = 8
        x0 = rects[0][0].x - pad
        x1 = rects[-1][0].right + pad
        top = rects[0][0].y - 6
        cont = pygame.Surface((x1 - x0, _FLAG_H + 12), pygame.SRCALPHA)
        cont.fill((16, 15, 13, 150))
        pygame.draw.rect(cont, (*GOLD_SOFT, 70), cont.get_rect(), 1, border_radius=13)
        screen.blit(cont, (x0, top))
    for rect, code in rects:
        active = (code == i18n.current)
        flag = _flag_surface(code)
        if not active:
            flag = flag.copy()
            flag.set_alpha(110)
        if active:                         # 선택된 국기: 살짝 위로 떠오르고 금색 글로우
            glow = rect.inflate(8, 8)
            pygame.draw.rect(screen, (*GOLD, 60), glow, border_radius=6)
        screen.blit(flag, rect.topleft)
        pygame.draw.rect(screen, GOLD if active else (86, 82, 74),
                         rect, 2 if active else 1, border_radius=4)


def _on_lang(pos):
    return any(rect.collidepoint(pos) for rect, _ in _lang_rects())


def draw_overlays():
    draw_conflict_scale()
    if hud_visible:
        draw_gauges()
    draw_lang_selector()
    draw_toasts()


# ── 대사창 (몰입형 하단 그라데이션) ─────────────────────
def draw_dialog_box(name, text, name_color, text_color, serif=True, done=True):
    art = load_ui("talk", (WIDTH, 300))
    if art is not None:
        screen.blit(art, (0, HEIGHT - 300))
    else:
        _vgrad(screen, (0, HEIGHT - 300, WIDTH, 300), 0, 232)
        pygame.draw.line(screen, (*GOLD, 90), (0, HEIGHT - 300), (WIDTH, HEIGHT - 300), 1)

    mx = 120
    text_top = HEIGHT - 168
    if name:
        nf = name_font(name, 24, bold=True, serif=True)
        ns = nf.render(name, True, name_color)
        screen.blit(ns, (mx, HEIGHT - 236))
        # 이름 밑줄 : 이름 글자 아래로 충분히 내려, 본문/이름과 겹치지 않게
        underline_y = HEIGHT - 236 + ns.get_height() + 6
        pygame.draw.line(screen, (*name_color, 150),
                         (mx, underline_y), (mx + max(90, ns.get_width()), underline_y), 2)

    f = get_font(29, serif=serif)
    for i, line in enumerate(wrap_text(text, f, WIDTH - mx * 2)[:4]):
        _text_shadow(f, line, text_color, mx, text_top + i * 42)

    if done:
        _draw_advance_hint()


def _draw_advance_hint():
    """하단 우측 진행 힌트 :  Click / Space bar  > >> >>>  (쉐브론 순차 점등)."""
    t = pygame.time.get_ticks()
    cy = HEIGHT - 50
    lbl = get_font(15).render(i18n.ui("hint_advance"), True, GRAY)
    lbl.set_alpha(210)
    chev_f = get_font(20, bold=True)
    chev_w = chev_f.size(">")[0]
    spacing = 4
    right = WIDTH - 46
    chev_x0 = right - (3 * chev_w + 2 * spacing)
    screen.blit(lbl, (chev_x0 - 16 - lbl.get_width(), cy - lbl.get_height() // 2))
    lit = (t // 220) % 4          # 0→1→2→3 : > , >> , >>> 순차 점등 후 리셋
    for i in range(3):
        on = i < lit
        ch = chev_f.render(">", True, GOLD if on else (108, 102, 90))
        ch.set_alpha(240 if on else 90)
        screen.blit(ch, (chev_x0 + i * (chev_w + spacing), cy - ch.get_height() // 2))


# ── 이벤트 ───────────────────────────────────────────
def handle_common(event):
    global hud_visible
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            if in_game:
                open_pause_menu()          # 일시정지 메뉴(볼륨/저장/로드/타이틀/종료)
            else:
                pygame.quit()
                sys.exit(0)
        elif event.key == pygame.K_TAB:
            hud_visible = not hud_visible
        elif event.key in (pygame.K_l,) and in_game:
            open_backlog()                 # L 키로도 로그 열기
    if event.type == pygame.MOUSEWHEEL and event.y > 0 and in_game:
        open_backlog()                     # 마우스 휠 위로 = 백로그
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, code in _lang_rects():
            if rect.collidepoint(event.pos):
                if code != i18n.current:
                    i18n.set_lang(code)
                    save_settings()
                play_sfx("click")
                return


def is_advance(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        return not _on_lang(event.pos)      # 국기 클릭은 진행이 아니라 언어 전환
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
        return True
    return False


# ── 대사 (타이핑 연출 + 문장부호 미세 정지) ─────────────
_PAUSE_CHARS = set("…,.!?—·")


def _log_line(speaker, src, mono):
    """백로그에는 '원문(한국어)'을 저장 → 표시할 때 현재 언어로 번역."""
    dialog_log.append((speaker, src, mono))
    if len(dialog_log) > _MAX_LOG:
        del dialog_log[:len(dialog_log) - _MAX_LOG]


def show_text(src, speaker=None, mono=False, narr_color=PARCH, serif=True):
    """대사 출력. 원문(src)을 매 프레임 현재 언어로 번역하므로,
    재생 중 국기를 눌러 언어를 바꾸면 화면의 대사가 '즉시' 바뀐다."""
    global _player_turn, _speaker_portrait
    _player_turn = (speaker == "나")
    _speaker_portrait = resolve_speaker_portrait(speaker, src)
    _log_line(speaker, src, mono)
    lang = None
    full = ""
    revealed, done, pause = 0.0, False, 0.0
    while True:
        dt = clock.tick(FPS)
        if lang != i18n.current:                 # 언어 전환 → 즉시 재번역/재줄바꿈
            lang = i18n.current
            f = get_font(29, serif=serif)
            full = "\n".join(wrap_text(i18n.t(src), f, WIDTH - 240))
            if done or revealed > len(full):
                revealed = len(full)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event):
                if not done:
                    revealed, done = len(full), True
                else:
                    _player_turn = False
                    _speaker_portrait = None
                    return
        if not done:
            if pause > 0:
                pause = max(0, pause - dt)
            else:
                revealed += TYPE_SPEED * dt / 1000.0
                idx = int(revealed)
                if 0 < idx <= len(full) and full[idx - 1] in _PAUSE_CHARS:
                    pause = 120
            if revealed >= len(full):
                revealed, done = len(full), True
        if speaker is not None:
            name, ncol, tcol = i18n.nm(speaker), PARCH, PARCH
        elif mono:
            name, ncol, tcol = i18n.ui("mono_label"), BLUE, BLUE
        else:
            name, ncol, tcol = None, PARCH, narr_color
        draw_scene_base()
        draw_dialog_box(name, full[:int(revealed)].replace("\n", " "),
                        ncol, tcol, serif=serif, done=done)
        draw_overlays()
        pygame.display.flip()


# ── 선택지 (마우스 + 키보드 겸용, 우아한 리스트) ─────────
_CIRCLED = "①②③④⑤⑥⑦⑧⑨"


def _clean_label(s):
    """앞의 원문자(①②③) 제거 → 언어 무관하게 번호를 다시 붙이기 위함."""
    s = s.strip()
    if s and s[0] in _CIRCLED:
        s = s[1:].lstrip()
    return s


def _choice_loop(get_question, get_labels, get_footer=None, dim=150):
    """question/labels/footer 는 '현재 언어 문자열'을 돌려주는 콜러블.
    매 프레임 평가하므로 선택지 화면에서 국기를 눌러도 즉시 번역된다."""
    f = get_font(25, serif=True)
    bh, gap = 62, 16
    lang = None
    labels, question, footer, bw, total, start_y = [], "", None, 560, 0, 0
    sel = 0
    while True:
        clock.tick(FPS)
        if lang != i18n.current:                 # 언어 전환 → 즉시 재번역/재배치
            lang = i18n.current
            question = get_question()
            footer = get_footer() if get_footer else None
            labels = [f"{i + 1}.  {_clean_label(l)}" for i, l in enumerate(get_labels())]
            bw = min(960, max(560, max((f.size(l)[0] for l in labels), default=560) + 120))
            total = len(labels) * bh + (len(labels) - 1) * gap
            start_y = HEIGHT // 2 - total // 2 + 26
        mx, my = pygame.mouse.get_pos()
        rects = [pygame.Rect(WIDTH // 2 - bw // 2, start_y + i * (bh + gap), bw, bh)
                 for i in range(len(labels))]
        for i, r in enumerate(rects):
            if r.collidepoint(mx, my):
                sel = i
        for event in pygame.event.get():
            handle_common(event)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(labels)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(labels)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    play_sfx("click"); return sel
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    k = event.key - pygame.K_1
                    if k < len(labels):
                        play_sfx("click"); return k
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rects[sel].collidepoint(mx, my):
                    play_sfx("click"); return sel

        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, dim))
        screen.blit(veil, (0, 0))
        q = get_font(26, bold=True, serif=True).render(question, True, GOLD)
        screen.blit(q, q.get_rect(center=(WIDTH // 2, start_y - 52)))
        pygame.draw.line(screen, (*GOLD, 90),
                         (WIDTH // 2 - 200, start_y - 26), (WIDTH // 2 + 200, start_y - 26), 1)
        for i, r in enumerate(rects):
            on = (i == sel)
            slide = 14 if on else 0
            panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
            panel.fill((36, 33, 28, 250) if on else (20, 18, 16, 210))
            pygame.draw.rect(panel, (*GOLD, 255) if on else (96, 90, 80, 200),
                             panel.get_rect(), 2, border_radius=8)
            if on:
                pygame.draw.rect(panel, (*GOLD, 255), (0, 0, 5, bh))
            screen.blit(panel, r.topleft)
            txt = f.render(labels[i], True, GOLD if on else PARCH)
            screen.blit(txt, txt.get_rect(midleft=(r.x + 30 + slide, r.centery)))
        if footer:
            fs = get_font(20).render(footer, True, GRAY)
            screen.blit(fs, fs.get_rect(center=(WIDTH // 2, start_y + total + 42)))
        draw_overlays()
        pygame.display.flip()


def show_choice(options):
    return _choice_loop(lambda: i18n.ui("choice_q"),
                        lambda: [i18n.t(o[0]) for o in options])


def show_choice_menu(get_question, get_labels, get_footer=None):
    return _choice_loop(get_question, get_labels, get_footer=get_footer)


# ── 타이틀 / 카드 / 전환 ─────────────────────────────
def _fade_letterbox(target, ms=280):
    global letterbox
    start_v = letterbox
    start = pygame.time.get_ticks()
    while True:
        t = pygame.time.get_ticks() - start
        r = min(1, t / ms)
        letterbox = start_v + (target - start_v) * r
        for event in pygame.event.get():
            handle_common(event)
        draw_scene_base()
        pygame.display.flip()
        clock.tick(FPS)
        if r >= 1:
            break


def _render_title(lines, sub, alpha):
    """타이틀 한 프레임 렌더링 (선이 글자를 관통하지 않도록 간격 확보)."""
    screen.fill(INK)
    line_gap = 76
    cy = HEIGHT // 2 - (52 if sub else 0)
    for i, line in enumerate(lines):
        fnt = fit_font(line, 62 if i == 0 else 42, WIDTH - 160, bold=True, serif=True)
        surf = fnt.render(line, True, GOLD if i == 0 else PARCH)
        surf.set_alpha(alpha)
        screen.blit(surf, surf.get_rect(center=(WIDTH // 2, cy + i * line_gap)))
    if sub:
        # 구분선은 제목 블록 아래, 부제는 구분선보다 더 아래 → 선/글자 겹침 방지
        div_y = cy + (len(lines) - 1) * line_gap + 64
        pygame.draw.line(screen, (*GOLD_SOFT, int(alpha * 0.7)),
                         (WIDTH // 2 - 130, div_y), (WIDTH // 2 + 130, div_y), 1)
        sf = get_font(23, serif=True)
        for j, s in enumerate(wrap_text(sub, sf, WIDTH - 300)):
            ss = sf.render(s, True, PARCH_DIM)
            ss.set_alpha(alpha)
            screen.blit(ss, ss.get_rect(center=(WIDTH // 2, div_y + 38 + j * 34)))
    draw_lang_selector()


def show_title(lines, sub=None):
    global letterbox
    letterbox = 1.0
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 450:
                letterbox = 0.0
                return
        t = pygame.time.get_ticks() - start
        alpha = min(255, int(255 * t / 700))
        _render_title(lines, sub, alpha)
        pygame.display.flip()


# ── 기억 조각 획득 : 반짝이는 연출 ───────────────────
_GLOW_CACHE = {}


def _glow_surf(radius, color):
    """중심이 밝은 부드러운 방사형 광채 서피스(캐시)."""
    ck = (radius, color)
    if ck in _GLOW_CACHE:
        return _GLOW_CACHE[ck]
    d = radius * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    for rr in range(radius, 0, -1):
        a = int(110 * (1 - rr / radius) ** 2)
        pygame.draw.circle(s, (*color, a), (radius, radius), rr)
    _GLOW_CACHE[ck] = s
    return s


def _frag_surface(frag, px=96, owned=True):
    """기억 조각 아이콘 서피스 : 이미지가 있으면 사용, 없으면 벡터를 48px로 그려 확대."""
    icon = load_icon(frag, px)
    if icon is not None:
        return icon.copy()
    base = GOLD if owned else (90, 84, 74)
    s = pygame.Surface((48, 48), pygame.SRCALPHA)
    pygame.draw.rect(s, (26, 23, 20), (0, 0, 48, 48), border_radius=9)
    pygame.draw.rect(s, base, (0, 0, 48, 48), 2, border_radius=9)
    key = FRAGMENT_ICON.get(frag)
    if key == "clothes":           # 군복
        pygame.draw.polygon(s, base, [(12, 14), (24, 20), (36, 14), (33, 38), (15, 38)])
    elif key == "ballchain":       # 군번줄
        pygame.draw.circle(s, base, (24, 18), 8, 2)
        pygame.draw.rect(s, base, (18, 26, 12, 12), 2, border_radius=3)
    elif key == "scarf":           # 붉은 손수건
        pygame.draw.polygon(s, (188, 72, 62), [(12, 14), (36, 14), (24, 36)])
    elif key == "empshell":        # 탄피
        pygame.draw.rect(s, base, (18, 12, 12, 24), 2, border_radius=4)
        pygame.draw.circle(s, base, (24, 12), 6, 2)
    elif key == "flag":            # 깃발
        pygame.draw.line(s, base, (16, 12), (16, 38), 2)
        pygame.draw.polygon(s, base, [(16, 12), (36, 16), (16, 24)], 2)
    if px != 48:
        s = pygame.transform.smoothscale(s, (px, px))
    return s


def _sparkle_star(cx, cy, r, color, alpha):
    """네 갈래로 뻗는 반짝임 별 (가산 블렌드)."""
    d = int(r * 2 + 4)
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    c = d // 2
    col = (*color, alpha)
    pygame.draw.polygon(s, col, [(c, c - r), (c + r * 0.26, c), (c, c + r), (c - r * 0.26, c)])
    pygame.draw.polygon(s, col, [(c - r, c), (c, c + r * 0.26), (c + r, c), (c, c - r * 0.26)])
    screen.blit(s, (cx - c, cy - c), special_flags=pygame.BLEND_RGBA_ADD)


def _draw_rays(cx, cy, t, n=12, length=96, color=(255, 220, 130)):
    """아이콘 뒤에서 천천히 도는 빛줄기(스타버스트)."""
    d = length * 2
    s = pygame.Surface((d, d), pygame.SRCALPHA)
    c = length
    rot = t * 0.0006
    for i in range(n):
        a = rot + i * 2 * math.pi / n
        ln = length * (1.0 if i % 2 == 0 else 0.58)
        w = 0.05
        pygame.draw.polygon(s, (*color, 42), [
            (c + math.cos(a - w) * 13, c + math.sin(a - w) * 13),
            (c + math.cos(a + w) * 13, c + math.sin(a + w) * 13),
            (c + math.cos(a) * ln, c + math.sin(a) * ln)])
    screen.blit(s, (cx - c, cy - c), special_flags=pygame.BLEND_RGBA_ADD)


def _frag_get_frame(frag, icon96, parts, body_lines, t):
    """기억 조각 획득 연출의 한 프레임을 그린다(t: 시작 후 경과 ms)."""
    intro = min(1.0, t / 400)
    ease = 1 - (1 - intro) ** 3                # 부드러운 등장
    draw_scene_base()
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 192))
    screen.blit(veil, (0, 0))
    cx = WIDTH // 2
    icy = HEIGHT // 2 - 40

    hdr = get_font(19, bold=True, serif=True).render(i18n.ui("frag_get"), True, GOLD)
    hdr.set_alpha(int(255 * min(1, t / 320)))
    screen.blit(hdr, hdr.get_rect(center=(cx, icy - 118)))

    # 빛줄기(회전) + 부드러운 후광(맥동)
    _draw_rays(cx, icy, t)
    pulse = 0.82 + 0.18 * math.sin(t * 0.005)
    glow = _glow_surf(92, (255, 214, 126))
    gsz = max(1, int(184 * ease * pulse))
    gs = pygame.transform.smoothscale(glow, (gsz, gsz))
    screen.blit(gs, gs.get_rect(center=(cx, icy)), special_flags=pygame.BLEND_RGBA_ADD)

    # 아이콘(스케일 인)
    isz = max(2, int(92 * ease))
    ic = pygame.transform.smoothscale(icon96, (isz, isz))
    screen.blit(ic, ic.get_rect(center=(cx, icy)))

    # 반짝이는 별 파티클
    for ang, dist, size, phase, spd in parts:
        tw = 0.5 + 0.5 * math.sin(t * 0.001 * spd + phase)
        d = dist * ease
        _sparkle_star(cx + math.cos(ang) * d, icy + math.sin(ang) * d,
                      size * (0.5 + 0.7 * tw), (255, 234, 170), int(70 + 170 * tw))

    # 조각 이름(크게) — 후광 아래에 배치해 또렷하게
    name = i18n.t(frag)
    nm = fit_font(name, 34, WIDTH - 260, bold=True, serif=True)
    _text_shadow(nm, name, PARCH, cx - nm.size(name)[0] // 2, icy + 96, sa=200)
    pygame.draw.line(screen, (*GOLD_SOFT, 120), (cx - 150, icy + 138), (cx + 150, icy + 138), 1)
    for i, line in enumerate(body_lines):
        ls = get_font(21, serif=True).render(line, True, PARCH_DIM)
        ls.set_alpha(int(255 * min(1, max(0, (t - 240) / 320))))
        screen.blit(ls, ls.get_rect(center=(cx, icy + 166 + i * 32)))

    if t > 700:
        hint = get_font(15).render(i18n.ui("frag_get_hint"), True, GRAY)
        hint.set_alpha(int(150 + 90 * math.sin(t * 0.005)))
        screen.blit(hint, hint.get_rect(center=(cx, HEIGHT - 40)))
    draw_lang_selector()


def show_fragment_get(frag, title, body):
    """기억 조각 획득 연출 : 반짝이는 아이콘 + 이름 + 설명으로 무엇을 얻었는지 직관적으로 보여준다."""
    import random as _rnd
    play_sfx("item")
    icon96 = _frag_surface(frag, 96)
    parts = [(_rnd.uniform(0, 2 * math.pi), _rnd.uniform(60, 138),
              _rnd.uniform(3, 7), _rnd.uniform(0, 2 * math.pi), _rnd.uniform(2.5, 6.0))
             for _ in range(18)]
    body_lines = []
    for b in body:
        body_lines.extend(wrap_text(b, get_font(21, serif=True), 640) if b else [""])
    start = pygame.time.get_ticks()
    while True:
        t = pygame.time.get_ticks() - start
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and t > 420:
                return
        _frag_get_frame(frag, icon96, parts, body_lines, t)
        pygame.display.flip()
        clock.tick(FPS)


def _card_frame(kind, title, body):
    """카드 한 프레임 렌더링. 본문·제목은 박스 내부 폭을 절대 넘지 않도록 처리."""
    accent = CARD_ACCENT.get(kind, PARCH)
    draw_scene_base()
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 175))
    screen.blit(veil, (0, 0))
    card_w = 720
    pad = 56                                  # 박스 내부 좌우 여백
    inner_w = card_w - pad * 2                # 본문/제목이 넘지 못하는 최대 폭
    body_font = get_font(23, serif=True)
    body_lines = []
    for b in body:
        body_lines.extend(wrap_text(b, body_font, inner_w) if b else [""])
    card_h = 150 + len(body_lines) * 34
    cx, cy = WIDTH // 2 - card_w // 2, HEIGHT // 2 - card_h // 2
    panel = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
    panel.fill((16, 15, 13, 250))
    pygame.draw.rect(panel, (*accent, 255), panel.get_rect(), 2, border_radius=6)
    pygame.draw.rect(panel, (*accent, 255), (0, 0, card_w, 5))
    screen.blit(panel, (cx, cy))
    tt = fit_font(title, 34, inner_w, bold=True, serif=True).render(title, True, accent)
    screen.blit(tt, tt.get_rect(center=(WIDTH // 2, cy + 50)))
    pygame.draw.line(screen, (*accent, 150), (cx + 70, cy + 88), (cx + card_w - 70, cy + 88), 1)
    for i, line in enumerate(body_lines):
        ls = body_font.render(line, True, PARCH)
        screen.blit(ls, ls.get_rect(center=(WIDTH // 2, cy + 118 + i * 34)))
    draw_lang_selector()


def show_card(kind, title, body):
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 260:
                return
        _card_frame(kind, title, body)
        pygame.display.flip()


def show_flash():
    for a in list(range(0, 256, 22)) + list(range(255, -1, -16)):
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 250, 240, a))
        screen.blit(veil, (0, 0))
        pygame.display.flip()


def screen_fade_out(ms=460, color=INK):
    """현재 화면을 지정색으로 부드럽게 페이드아웃."""
    snapshot = screen.copy()
    veil = pygame.Surface((WIDTH, HEIGHT))
    veil.fill(color)
    start = pygame.time.get_ticks()
    while True:
        t = pygame.time.get_ticks() - start
        r = min(1.0, t / ms)
        for event in pygame.event.get():
            handle_common(event)
        screen.blit(snapshot, (0, 0))
        veil.set_alpha(int(255 * r))
        screen.blit(veil, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)
        if r >= 1.0:
            break


def scene_fade_in(ms=520):
    """draw_scene_base 화면을 검은색에서 서서히 드러냄(장면 등장)."""
    veil = pygame.Surface((WIDTH, HEIGHT))
    veil.fill(INK)
    start = pygame.time.get_ticks()
    while True:
        t = pygame.time.get_ticks() - start
        r = min(1.0, t / ms)
        for event in pygame.event.get():
            handle_common(event)
        draw_scene_base()
        veil.set_alpha(int(255 * (1 - r)))
        screen.blit(veil, (0, 0))
        draw_overlays()
        pygame.display.flip()
        clock.tick(FPS)
        if r >= 1.0:
            break


def show_black():
    """장면 전환용 검은 화면 : 이전 화면을 페이드아웃한 뒤 잠시 정지."""
    screen_fade_out(460)
    Scene.bg_key = None
    Scene.char_key = None
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 240:
                return
        screen.fill(INK)
        draw_lang_selector()
        pygame.display.flip()


# ── 대사 로그 (백로그) ───────────────────────────────
def open_backlog():
    pygame.event.clear()
    name_f = get_font(21, bold=True, serif=True)
    body_f = get_font(23, serif=True)
    margin = 150
    maxw = WIDTH - margin * 2
    view_top, view_bot = 118, HEIGHT - 66
    view_h = view_bot - view_top

    line_h = 32

    def build_rows():
        # 저장된 '원문'을 현재 언어로 번역해 라인 구성 (언어 변경 시 재호출)
        rows = []  # (surface, indent)
        for speaker, src, mono in dialog_log:
            if mono:
                name, ncol = i18n.ui("mono_label"), BLUE
            elif speaker:
                name, ncol = i18n.nm(speaker), GOLD
            else:
                name, ncol = None, None
            if name:
                rows.append((name_f.render(name, True, ncol), 0))
            for ln in wrap_text(i18n.t(src), body_f, maxw - 24):
                rows.append((body_f.render(ln, True, PARCH if name else PARCH_DIM), 24 if name else 4))
            rows.append((None, 0))  # 항목 간 간격
        return rows

    lang = i18n.current
    rows = build_rows()
    content_h = len(rows) * line_h
    scroll = max(0, content_h - view_h)      # 최신(맨 아래)부터
    max_scroll = scroll

    while True:
        clock.tick(FPS)
        if lang != i18n.current:              # 언어 변경 시 로그도 다시 번역
            lang = i18n.current
            rows = build_rows()
            content_h = len(rows) * line_h
            max_scroll = max(0, content_h - view_h)
            scroll = min(scroll, max_scroll)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_TAB):
                    return
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    scroll = min(max_scroll, scroll + line_h * 2)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    scroll = max(0, scroll - line_h * 2)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll = min(max_scroll, scroll + view_h)
                elif event.key == pygame.K_PAGEUP:
                    scroll = max(0, scroll - view_h)
            if event.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(max_scroll, scroll - event.y * line_h * 2))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not _on_lang(event.pos):
                    return
                for rect, code in _lang_rects():
                    if rect.collidepoint(event.pos) and code != i18n.current:
                        i18n.set_lang(code); save_settings()

        screen.fill(INK)
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((6, 5, 4, 235))
        screen.blit(veil, (0, 0))
        title = get_font(26, bold=True, serif=True).render(i18n.ui("backlog_title"), True, GOLD)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 78)))
        pygame.draw.line(screen, (*GOLD_SOFT, 120), (margin, 100), (WIDTH - margin, 100), 1)

        if not dialog_log:
            em = get_font(22, serif=True).render(i18n.ui("backlog_empty"), True, GRAY)
            screen.blit(em, em.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        else:
            screen.set_clip(pygame.Rect(0, view_top, WIDTH, view_h))
            y = view_top - scroll
            for surf, indent in rows:
                if surf is not None and -line_h < (y - view_top) < view_h + line_h:
                    screen.blit(surf, (margin + indent, y))
                y += line_h
            screen.set_clip(None)
            # 스크롤 인디케이터
            if max_scroll > 0:
                track_h = view_h
                kh = max(30, int(track_h * view_h / content_h))
                ky = view_top + int((track_h - kh) * (scroll / max_scroll))
                pygame.draw.rect(screen, (90, 84, 74), (WIDTH - margin + 40, view_top, 4, track_h))
                pygame.draw.rect(screen, GOLD, (WIDTH - margin + 40, ky, 4, kh))

        hint = get_font(16).render(i18n.ui("backlog_hint"), True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 34)))
        draw_lang_selector()
        pygame.display.flip()


# ── 일시정지 / 설정 메뉴 ─────────────────────────────
def open_pause_menu():
    pygame.event.clear()
    snapshot = screen.copy()
    rows = ["resume", "save", "load", "bgm", "sfx", "to_title", "quit"]
    sel = 0
    msg, msg_at = "", 0
    bw, bh, gap = 420, 52, 10
    total = len(rows) * bh + (len(rows) - 1) * gap
    top = HEIGHT // 2 - total // 2 + 20

    def row_rect(i):
        return pygame.Rect(WIDTH // 2 - bw // 2, top + i * (bh + gap), bw, bh)

    def adjust(key, d):
        settings[key] = max(0.0, min(1.0, round(settings[key] + d, 2)))
        if key == "bgm":
            apply_music_volume()
        else:
            apply_ambience_volume()
            play_sfx("click")
        save_settings()

    def activate(key):
        nonlocal msg, msg_at
        if key == "resume":
            return "close"
        if key == "save":
            save_game(); msg, msg_at = i18n.ui("saved_msg"), pygame.time.get_ticks(); play_sfx("item")
        elif key == "load":
            if load_game():
                raise ReloadStory
            msg, msg_at = i18n.ui("no_save"), pygame.time.get_ticks()
        elif key == "to_title":
            raise ReturnToTitle
        elif key == "quit":
            save_settings(); pygame.quit(); sys.exit(0)
        return None

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        for i in range(len(rows)):
            if row_rect(i).collidepoint(mx, my):
                sel = i
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(rows); play_sfx("click")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(rows); play_sfx("click")
                elif event.key in (pygame.K_LEFT, pygame.K_a) and rows[sel] in ("bgm", "sfx"):
                    adjust(rows[sel], -0.05)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and rows[sel] in ("bgm", "sfx"):
                    adjust(rows[sel], +0.05)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if activate(rows[sel]) == "close":
                        return
            if event.type == pygame.MOUSEWHEEL and rows[sel] in ("bgm", "sfx"):
                adjust(rows[sel], 0.05 * event.y)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handled = False
                for rect, code in _lang_rects():
                    if rect.collidepoint(event.pos):
                        if code != i18n.current:
                            i18n.set_lang(code); save_settings()
                        handled = True
                if handled:
                    continue
                r = row_rect(sel)
                if r.collidepoint(mx, my):
                    if rows[sel] in ("bgm", "sfx"):
                        # 슬라이더 트랙 위 클릭 위치로 값 설정
                        tx, tw = r.x + 150, bw - 200
                        val = max(0.0, min(1.0, (mx - tx) / tw))
                        settings[rows[sel]] = round(val, 2)
                        apply_music_volume() if rows[sel] == "bgm" else apply_ambience_volume()
                        save_settings()
                    elif activate(rows[sel]) == "close":
                        return

        screen.blit(snapshot, (0, 0))
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((6, 5, 4, 205))
        screen.blit(veil, (0, 0))
        ttl = get_font(34, bold=True, serif=True).render(i18n.ui("pause_title"), True, GOLD)
        screen.blit(ttl, ttl.get_rect(center=(WIDTH // 2, top - 54)))
        for i, key in enumerate(rows):
            r = row_rect(i)
            on = (i == sel)
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            surf.fill((38, 34, 28, 250) if on else (18, 16, 14, 220))
            pygame.draw.rect(surf, (*GOLD, 255) if on else (96, 90, 80, 200), surf.get_rect(), 2, border_radius=8)
            if on:
                pygame.draw.rect(surf, (*GOLD, 255), (0, 0, 5, bh))
            screen.blit(surf, r.topleft)
            if key in ("bgm", "sfx"):
                lbl = get_font(22, serif=True).render(i18n.ui(f"{key}_vol"), True, GOLD if on else PARCH)
                screen.blit(lbl, (r.x + 24, r.y + bh // 2 - lbl.get_height() // 2))
                tx, ty, tw = r.x + 150, r.centery, bw - 200
                pygame.draw.rect(screen, (60, 56, 50), (tx, ty - 3, tw, 6), border_radius=3)
                fw = int(tw * settings[key])
                pygame.draw.rect(screen, GOLD if on else GOLD_SOFT, (tx, ty - 3, fw, 6), border_radius=3)
                pygame.draw.circle(screen, GOLD if on else PARCH, (tx + fw, ty), 8)
                pct = get_font(17).render(f"{int(settings[key] * 100)}", True, GRAY)
                screen.blit(pct, (r.right - 44, r.centery - pct.get_height() // 2))
            else:
                lbl = get_font(23, bold=(key in ("resume",)), serif=True).render(
                    i18n.ui(key), True, GOLD if on else PARCH)
                screen.blit(lbl, lbl.get_rect(center=r.center))
        if msg and pygame.time.get_ticks() - msg_at < 1600:
            ms = get_font(20, serif=True).render(msg, True, GREEN)
            screen.blit(ms, ms.get_rect(center=(WIDTH // 2, top + total + 22)))
        hint = get_font(16).render(i18n.ui("pause_hint"), True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 30)))
        draw_lang_selector()
        pygame.display.flip()


def transition_to_bg(newkey, ms=280):
    """배경 교체 시 크로스페이드."""
    if Scene.bg_key == newkey:
        update_bgm_for_bg(newkey)
        return
    old = screen.copy()
    Scene.bg_key = newkey
    update_bgm_for_bg(newkey)
    start = pygame.time.get_ticks()
    while True:
        t = pygame.time.get_ticks() - start
        for event in pygame.event.get():
            handle_common(event)
        draw_scene_base()
        a = max(0, 1 - t / ms)
        if a > 0:
            old.set_alpha(int(255 * a))
            screen.blit(old, (0, 0))
        draw_overlays()
        pygame.display.flip()
        clock.tick(FPS)
        if t >= ms:
            break


# ── 자유 탐색 ────────────────────────────────────────
def run_explore(locations):
    visited = set()
    saved_bg, saved_char, saved_pos = Scene.bg_key, Scene.char_key, Scene.char_pos
    while len(visited) < len(locations):
        remaining = [(name, nodes) for name, nodes in locations if name not in visited]
        Scene.bg_key, Scene.char_key = saved_bg, None
        idx = show_choice_menu(
            lambda: i18n.ui("explore_q"),
            lambda rem=remaining: [i18n.t(name) for name, _ in rem],
            get_footer=lambda v=len(visited): i18n.ui("explore_footer", done=v, total=len(locations)),
        )
        name, nodes = remaining[idx]
        run_nodes(nodes)
        stop_ambience(600)                 # 장소를 떠나면 그 장소의 환경음도 잦아듦
        visited.add(name)
    Scene.bg_key, Scene.char_key, Scene.char_pos = saved_bg, saved_char, saved_pos


# ── 엔딩 판정 ────────────────────────────────────────
ENDING_TITLE = {
    "TRUE": "TRUE END 「진정한 용기」",
    "GOOD": "GOOD END 「앞으로 나아간 사람」",
    "NORMAL": "NORMAL END 「정답 없는 질문」",
    "BAD": "BAD END 「붉은 무공훈장」",
    "HIDDEN": "HIDDEN END 「인간이라는 이름」",
}


def determine_ending():
    E = stats.get("공감", 0)
    T = stats.get("신뢰", 0)
    G = stats.get("죄책감", 0)
    C = stats.get("용기", 0)
    if len(items) >= len(ALL_FRAGMENTS) and E >= 90:
        return "HIDDEN"
    if E >= 80 and T >= 80 and G <= 40 and C >= 80:
        return "TRUE"
    if T <= 30 or G >= 80:
        return "BAD"
    if E >= 60 and C >= 60:
        return "GOOD"
    return "NORMAL"


def _cmp(left, op, right):
    return {">=": left >= right, "<=": left <= right, ">": left > right,
            "<": left < right, "==": left == right}[op]


def eval_cond(cond):
    key, op, val = cond
    if key == "조각수":
        left = len(items)
    elif key in ("인간", "군인"):
        left = conflict.get(key, 0)
    else:
        left = stats.get(key, 0)
    return _cmp(left, op, val)


def _draw_fragment_icon(x, y, frag, owned, px=48):
    """기억 조각 아이콘 : 파일 없으면 조각별 벡터 심볼을 그린다."""
    icon = load_icon(frag, px)
    if icon is not None:
        surf = icon.copy()
        if not owned:
            surf.set_alpha(55)
        screen.blit(surf, (x, y))
        if owned:
            pygame.draw.rect(screen, GOLD, (x, y, px, px), 1, border_radius=6)
        return
    base = GOLD if owned else (78, 74, 66)
    pygame.draw.rect(screen, (24, 22, 20), (x, y, px, px), border_radius=8)
    pygame.draw.rect(screen, base, (x, y, px, px), 2, border_radius=8)
    cx, cy = x + px // 2, y + px // 2
    key = FRAGMENT_ICON.get(frag)
    if key == "clothes":           # 군복
        pygame.draw.polygon(screen, base, [(cx - 12, y + 14), (cx, y + 20), (cx + 12, y + 14),
                                           (cx + 9, y + px - 10), (cx - 9, y + px - 10)])
    elif key == "ballchain":       # 군번줄
        pygame.draw.circle(screen, base, (cx, cy - 6), 8, 2)
        pygame.draw.rect(screen, base, (cx - 6, cy + 2, 12, 12), 2, border_radius=3)
    elif key == "scarf":           # 붉은 손수건
        col = (176, 66, 58) if owned else base
        pygame.draw.polygon(screen, col, [(x + 12, y + 14), (x + px - 12, y + 14), (cx, y + px - 12)])
    elif key == "empshell":        # 탄피
        pygame.draw.rect(screen, base, (cx - 6, cy - 12, 12, 24), 2, border_radius=4)
        pygame.draw.circle(screen, base, (cx, cy - 12), 6, 2)
    elif key == "flag":            # 깃발
        pygame.draw.line(screen, base, (cx - 8, y + 12), (cx - 8, y + px - 10), 2)
        pygame.draw.polygon(screen, base, [(cx - 8, y + 12), (cx + 12, y + 16), (cx - 8, y + 24)], 2)


def _stat_scale_panel(oy=250):
    ox = 180
    screen.blit(get_font(19, bold=True, serif=True).render(i18n.ui("stat_word"), True, GRAY), (ox, oy - 34))
    for i, k in enumerate(["신뢰", "공감", "인간본능", "사회적역할", "죄책감", "용기"]):
        y = oy + i * 40
        screen.blit(get_font(20, serif=True).render(i18n.stat(k), True, PARCH), (ox, y - 2))
        _bar(ox + 150, y + 6, 200, stats.get(k, 0), STAT_COLOR[k])
        screen.blit(get_font(17).render(str(stats.get(k, 0)), True, STAT_COLOR[k]), (ox + 360, y - 2))
    rx, ry = WIDTH - 470, oy
    m = max(100, conflict["인간"], conflict["군인"])
    screen.blit(get_font(19, bold=True, serif=True).render(i18n.ui("conflict_title"), True, GRAY), (rx, ry - 34))
    screen.blit(get_font(18, serif=True).render(f"{i18n.ui('conflict_human')}  {conflict['인간']}", True, GREEN), (rx, ry))
    _bar(rx, ry + 28, 300, conflict["인간"], GREEN, m)
    screen.blit(get_font(18, serif=True).render(f"{i18n.ui('conflict_soldier')}  {conflict['군인']}", True, STAT_COLOR["사회적역할"]), (rx, ry + 52))
    _bar(rx, ry + 80, 300, conflict["군인"], STAT_COLOR["사회적역할"], m)
    screen.blit(get_font(18, serif=True).render(i18n.ui("frag_result", n=len(items), t=len(ALL_FRAGMENTS)), True, GOLD), (rx, ry + 112))
    for i, frag in enumerate(ALL_FRAGMENTS):
        _draw_fragment_icon(rx + i * 58, ry + 138, frag, frag in items, 48)


def show_result(title):
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 450:
                return
        screen.fill(INK)
        _vgrad(screen, (0, 0, WIDTH, 160), 40, 0, color=(40, 34, 26))
        tt = fit_font(title, 38, WIDTH - 200, bold=True, serif=True).render(title, True, GOLD)
        screen.blit(tt, tt.get_rect(center=(WIDTH // 2, 86)))
        pygame.draw.line(screen, (*GOLD_SOFT, 120), (WIDTH // 2 - 240, 128), (WIDTH // 2 + 240, 128), 1)
        _stat_scale_panel(oy=224)
        note = get_font(20).render(i18n.ui("result_continue"), True, GRAY)
        screen.blit(note, note.get_rect(center=(WIDTH // 2, HEIGHT - 56)))
        draw_lang_selector()
        pygame.display.flip()


def show_final_question():
    opt_keys = ["fq1", "fq2", "fq3", "fq4"]
    f = get_font(24, serif=True)
    bw, bh, gap = 720, 60, 16
    total = len(opt_keys) * bh + (len(opt_keys) - 1) * gap
    start_y = HEIGHT // 2 - total // 2 + 30
    picked, picked_at, sel = None, 0, 0
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        opts = [f"{i + 1}.  {i18n.ui(k)}" for i, k in enumerate(opt_keys)]
        rects = [pygame.Rect(WIDTH // 2 - bw // 2, start_y + i * (bh + gap), bw, bh)
                 for i in range(len(opts))]
        for i, r in enumerate(rects):
            if r.collidepoint(mx, my):
                sel = i
        for event in pygame.event.get():
            handle_common(event)
            if picked is None:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_DOWN, pygame.K_UP):
                    sel = (sel + (1 if event.key == pygame.K_DOWN else -1)) % len(opts)
                if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                        and rects[sel].collidepoint(mx, my) and not _on_lang(event.pos)) \
                   or (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE)):
                    picked = sel; picked_at = pygame.time.get_ticks(); play_sfx("click")
            elif is_advance(event) and pygame.time.get_ticks() - picked_at > 450:
                return
        screen.fill(INK)
        q = fit_font(i18n.ui("fq_title"), 30, WIDTH - 200, bold=True, serif=True).render(i18n.ui("fq_title"), True, GOLD)
        screen.blit(q, q.get_rect(center=(WIDTH // 2, start_y - 72)))
        for i, r in enumerate(rects):
            on = (i == sel) or (i == picked)
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            surf.fill((36, 33, 28, 250) if on else (20, 18, 16, 210))
            pygame.draw.rect(surf, (*GOLD, 255) if (i == picked) else (96, 90, 80, 200),
                             surf.get_rect(), 2, border_radius=8)
            screen.blit(surf, r.topleft)
            of = fit_font(opts[i], 24, bw - 44, serif=True)   # 박스를 넘지 않도록 자동 축소
            txt = of.render(opts[i], True, GOLD if on else PARCH)
            screen.blit(txt, txt.get_rect(center=r.center))
        if picked is not None:
            th = get_font(20).render(i18n.ui("fq_note_end"), True, GRAY)
            screen.blit(th, th.get_rect(center=(WIDTH // 2, HEIGHT - 58)))
        else:
            th = get_font(18).render(i18n.ui("fq_note"), True, GRAY)
            screen.blit(th, th.get_rect(center=(WIDTH // 2, start_y + total + 40)))
        draw_lang_selector()
        pygame.display.flip()


def _analysis_data():
    """사전 설문 답과 게임 결과(엔딩·저울·스탯)를 대조한 데이터."""
    code = determine_ending()
    h, s = conflict["인간"], conflict["군인"]
    C = stats.get("용기", 0); G = stats.get("죄책감", 0)
    I = stats.get("인간본능", 0); E = stats.get("공감", 0)
    sv = profile.get("survey", {})
    rows = []                        # (dim_key, pre_key, meas_key, meas_kw, match)
    a1 = sv.get("q1")
    if a1 in ("A", "B"):
        lean = "an_lean_s" if s >= h else "an_lean_h"
        rows.append(("an_q1dim", "an_q1A" if a1 == "A" else "an_q1B", "an_q1meas",
                     {"s": s, "h": h, "lean_key": lean},
                     (a1 == "A" and s >= h) or (a1 == "B" and h >= s)))
    a2 = sv.get("q2")
    if a2 in ("A", "B"):
        cover = (code == "BAD") or (G >= 60) or (C < 60)
        rows.append(("an_q2dim", "an_q2A" if a2 == "A" else "an_q2B", "an_q2meas",
                     {"c": C, "g": G, "end_code": code},
                     (a2 == "A" and not cover) or (a2 == "B" and cover)))
    a3 = sv.get("q3")
    if a3 in ("A", "B"):
        lean = "an_lean_i" if I >= E else "an_lean_e"
        rows.append(("an_q3dim", "an_q3A" if a3 == "A" else "an_q3B", "an_q3meas",
                     {"i": I, "e": E, "lean_key": lean},
                     (a3 == "A" and I >= E) or (a3 == "B" and E >= I)))
    matches = sum(1 for *_, m in rows if m)
    return code, h, s, rows, (matches >= 2 if rows else True)


def _fmt_meas(meas_key, kw):
    """분석 계측 문장을 현재 언어로 즉석 조립 (라이브 재번역)."""
    k = dict(kw)
    if "lean_key" in k:
        k["lean"] = i18n.ui(k.pop("lean_key"))
    if "end_code" in k:
        k["end"] = i18n.ui("end_" + k.pop("end_code")).split(" ")[0]
    return i18n.ui(meas_key, **k)


def log_result(code, h, s, matches):
    """플레이 결과를 results.csv 에 누적 기록 (학술 분석/발표용)."""
    header = ["time", "name", "gender", "grade", "major", "mbti", "q1", "q2", "q3",
              "ending", "human", "soldier", "trust", "empathy", "instinct",
              "duty", "guilt", "courage", "fragments", "matches"]
    sv = profile.get("survey", {})
    row = [time.strftime("%Y-%m-%d %H:%M:%S"), profile.get("name", ""),
           profile.get("gender", ""), profile.get("grade", ""), profile.get("major", ""),
           profile.get("mbti", ""), sv.get("q1", ""), sv.get("q2", ""), sv.get("q3", ""),
           code, h, s, stats.get("신뢰", 0), stats.get("공감", 0), stats.get("인간본능", 0),
           stats.get("사회적역할", 0), stats.get("죄책감", 0), stats.get("용기", 0),
           len(items), matches]
    try:
        new = not os.path.exists(RESULT_PATH)
        with open(RESULT_PATH, "a", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(header)
            w.writerow(row)
    except Exception as e:
        print(f"[경고] 결과 기록 실패: {e}")


def show_analysis(code, h, s, rows, consistent):
    matches = sum(1 for *_, m in rows if m)
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 500:
                return
        screen.fill(INK)
        _vgrad(screen, (0, 0, WIDTH, 170), 44, 0, color=(40, 34, 26))
        ttl = i18n.ui("an_title")
        ts = fit_font(ttl, 33, WIDTH - 460, bold=True, serif=True).render(ttl, True, GOLD)
        screen.blit(ts, ts.get_rect(midtop=(WIDTH // 2, 52)))
        # 프로필 + 엔딩 + 저울  (이름은 문자에 맞는 글꼴로 별도 렌더)
        nm_str = (profile.get("name", "-") or "-") + "   "
        rest = i18n.ui("an_profile_rest",
                       gender=i18n.ui(profile.get("gender", "g_x")),
                       age=i18n.ui(profile.get("grade", "grade_1")),
                       major=i18n.ui(profile.get("major", "maj_ec")),
                       mbti=profile.get("mbti", "-"))
        nsurf = name_font(nm_str, 20, bold=True, serif=True).render(nm_str, True, GOLD_SOFT)
        rsurf = fit_font(rest, 20, WIDTH - 260 - nsurf.get_width(), serif=True).render(rest, True, PARCH)
        tot = nsurf.get_width() + rsurf.get_width()
        px = WIDTH // 2 - tot // 2
        screen.blit(nsurf, (px, 96))
        screen.blit(rsurf, (px + nsurf.get_width(), 96 + (nsurf.get_height() - rsurf.get_height()) // 2))
        end_lbl = f"{i18n.ui('an_ending')} : {i18n.ui(f'end_{code}')}"
        es = fit_font(end_lbl, 20, WIDTH - 200, bold=True, serif=True).render(end_lbl, True, GOLD_SOFT)
        screen.blit(es, es.get_rect(midtop=(WIDTH // 2, 124)))
        scl = f"{i18n.ui('an_scale')} :  {i18n.ui('conflict_human')} {h}   /   {i18n.ui('conflict_soldier')} {s}"
        ss = fit_font(scl, 18, WIDTH - 200, serif=True).render(scl, True, PARCH_DIM)
        screen.blit(ss, ss.get_rect(midtop=(WIDTH // 2, 150)))
        pygame.draw.line(screen, (*GOLD_SOFT, 120), (120, 180), (WIDTH - 120, 180), 1)

        # 문항별 대조
        y = 192
        for dim, pre, meas_key, meas_kw, match in rows:
            meas = _fmt_meas(meas_key, meas_kw)
            box = pygame.Rect(120, y, WIDTH - 240, 90)
            surf = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
            surf.fill((26, 24, 21, 220))
            pygame.draw.rect(surf, (GREEN if match else GOLD) + (200,), surf.get_rect(), 2, border_radius=10)
            pygame.draw.rect(surf, (*(GREEN if match else GOLD), 30), (0, 0, 6, box.h))
            screen.blit(surf, box.topleft)
            screen.blit(get_font(19, bold=True, serif=True).render(i18n.ui(dim), True, GOLD), (box.x + 18, box.y + 12))
            verdict = i18n.ui("an_match" if match else "an_diff")
            vsurf = get_font(17, bold=True).render(verdict, True, GREEN if match else GOLD)
            screen.blit(vsurf, (box.right - 18 - vsurf.get_width(), box.y + 13))
            line1 = f"· {i18n.ui('an_pre')}: {i18n.ui(pre)}"
            line2 = f"· {i18n.ui('an_ingame')}: {meas}"
            screen.blit(fit_font(line1, 17, box.w - 40, serif=True).render(line1, True, PARCH), (box.x + 18, box.y + 40))
            screen.blit(fit_font(line2, 17, box.w - 40, serif=True).render(line2, True, PARCH_DIM), (box.x + 18, box.y + 63))
            y += 98

        # 종합 리포트
        rep = pygame.Rect(120, y, WIDTH - 240, 88)
        rsurf = pygame.Surface((rep.w, rep.h), pygame.SRCALPHA); rsurf.fill((34, 30, 24, 235))
        pygame.draw.rect(rsurf, (*GOLD, 220), rsurf.get_rect(), 2, border_radius=10)
        screen.blit(rsurf, rep.topleft)
        screen.blit(get_font(18, bold=True, serif=True).render(
            f"{i18n.ui('an_summary_title')}  ({matches}/{len(rows)})", True, GOLD), (rep.x + 18, rep.y + 10))
        summ = i18n.ui("an_sum_consistent" if consistent else "an_sum_mixed")
        yy = rep.y + 40
        for ln in wrap_text(summ, get_font(17, serif=True), rep.w - 40):
            screen.blit(get_font(17, serif=True).render(ln, True, PARCH), (rep.x + 18, yy))
            yy += 24

        foot = get_font(16).render(i18n.ui("an_footer"), True, GRAY)
        screen.blit(foot, foot.get_rect(center=(WIDTH // 2, HEIGHT - 26)))
        draw_lang_selector()
        pygame.display.flip()


def run_ending():
    import story
    code = determine_ending()
    run_nodes(story.ENDINGS.get(code, []))
    show_result(i18n.ui(f"end_{code}"))
    show_final_question()
    code, h, s, rows, consistent = _analysis_data()
    log_result(code, h, s, sum(1 for *_, m in rows if m))
    try:                              # 결과 누적 후 학술 비교 리포트 자동 갱신
        import analyze
        analyze.build_report()
    except Exception as e:
        print(f"[경고] 분석 리포트 갱신 실패: {e}")
    show_analysis(code, h, s, rows, consistent)


# ────────────────────────────────────────────────────────────────
def run_nodes(nodes):
    global _chapter_label
    for node in nodes:
        kind = node[0]
        if kind == "bg":
            transition_to_bg(node[1])
        elif kind == "sfx":
            play_sfx(node[1])
        elif kind == "amb":
            if node[1] == "stop":
                stop_ambience()
            else:
                play_ambience(node[1])
        elif kind == "bgm":
            if node[1] == "start":
                start_base_bgm()
            elif node[1] == "stop":
                if AUDIO_OK:
                    pygame.mixer.music.stop()
                _music["base_on"] = False
                _music["cur"] = None
            else:
                start_base_bgm(node[1])
        elif kind == "char":
            Scene.char_key = node[1]
            Scene.char_pos = node[2] if node[2] else "center"
        elif kind == "say":
            show_text(node[2], speaker=node[1])
        elif kind == "mono":
            show_text(node[1], mono=True)
        elif kind == "narr":
            show_text(node[1], narr_color=(224, 214, 188))
        elif kind == "act":
            show_text(node[1], narr_color=GRAY)
        elif kind == "title":
            sub = node[2] if len(node) > 2 else None
            _chapter_label = node[1][0] if node[1] else _chapter_label
            show_title([i18n.t(x) for x in node[1]], i18n.t(sub) if sub else None)
        elif kind == "card":
            frag = None
            if node[1] == "item":
                frag = next((f for f in ALL_FRAGMENTS if f in node[2]), None)
            if frag:
                show_fragment_get(frag, i18n.t(node[2]), [i18n.t(b) for b in node[3]])
            else:
                show_card(node[1], i18n.t(node[2]), [i18n.t(b) for b in node[3]])
        elif kind == "stat":
            apply_effects(node[1])
        elif kind == "item":
            grant_item(node[1])
        elif kind == "flash":
            show_flash()
        elif kind == "clear":
            show_black()
        elif kind == "choice":
            options = node[1]
            idx = show_choice(options)
            _, effects, branch = options[idx]
            if effects:
                apply_effects(effects)
            run_nodes(branch)
        elif kind == "explore":
            run_explore(node[1])
        elif kind == "result":
            show_result(i18n.t(node[1]))
        elif kind == "cond":
            then_nodes = node[2] if len(node) > 2 else []
            else_nodes = node[3] if len(node) > 3 else []
            run_nodes(then_nodes if eval_cond(node[1]) else else_nodes)
        elif kind == "ending":
            run_ending()
            delete_save()                 # 게임 완료 → 세이브 정리(이어하기 방지)
            raise ReturnToTitle           # 엔딩 후 메인 화면으로 복귀


# ── 세이브 / 로드 ────────────────────────────────────
def has_save():
    return os.path.exists(SAVE_PATH)


def delete_save():
    try:
        if os.path.exists(SAVE_PATH):
            os.remove(SAVE_PATH)
    except OSError:
        pass


def _capture_checkpoint(index):
    """'노드 시작 시점'의 상태를 스냅샷. 세이브는 항상 이 지점을 기록하므로
    로드 후 해당 노드를 처음부터 재실행해도 효과가 중복 적용되지 않는다."""
    _checkpoint.update({
        "version": 2,
        "index": index,
        "stats": dict(stats),
        "conflict": dict(conflict),
        "items": list(items),
        "scene": {"bg": Scene.bg_key, "char": Scene.char_key, "pos": Scene.char_pos},
        "music": _music.get("cur"),
        "amb": _ambience.get("cur"),
        "lang": i18n.current,
        "label": _chapter_label,
        "profile": json.loads(json.dumps(profile)),   # 딥카피
    })


def read_save_meta():
    """이어하기 캡션용 : 저장된 챕터 라벨과 저장 시각."""
    if not os.path.exists(SAVE_PATH):
        return None
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"label": data.get("label", ""), "saved_at": data.get("saved_at", 0)}
    except Exception:
        return None


def save_game():
    if not _checkpoint:                       # 아직 체크포인트가 없으면 현재 상태로
        _capture_checkpoint(progress["index"])
    data = dict(_checkpoint)
    data["saved_at"] = time.time()
    data["lang"] = i18n.current               # 언어는 항상 최신 반영
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"[경고] 저장 실패: {e}")
        return False


def load_game():
    global _pending_fadein, _chapter_label
    if not os.path.exists(SAVE_PATH):
        return False
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        stats.clear(); stats.update(data.get("stats", {}))
        conflict.clear(); conflict.update(data.get("conflict", {"인간": 0, "군인": 0}))
        items[:] = data.get("items", [])
        progress["index"] = int(data.get("index", 0))
        if data.get("profile"):
            profile.clear(); profile.update(data["profile"])
            apply_profile_name()
        sc = data.get("scene", {})
        Scene.bg_key = sc.get("bg")
        Scene.char_key = sc.get("char")
        Scene.char_pos = sc.get("pos", "center")
        _chapter_label = data.get("label", "")
        if data.get("lang") in i18n.LANGS:
            i18n.set_lang(data["lang"])
        _checkpoint.clear(); _checkpoint.update(data)   # 이후 저장 일관성 유지
        stop_ambience(200)
        m = data.get("music")
        if m:
            start_base_bgm(m)
        amb = data.get("amb")
        if amb:
            play_ambience(amb)
        _pending_fadein = True                # 재개 시 부드럽게 페이드인
        return True
    except Exception as e:
        print(f"[경고] 불러오기 실패: {e}")
        return False


def reset_state():
    global _chapter_label
    import story
    stats.clear()
    stats.update(dict(story.INITIAL_STATS))
    conflict.clear(); conflict.update({"인간": 0, "군인": 0})
    items.clear()
    dialog_log.clear()
    progress["index"] = 0
    _checkpoint.clear()
    _chapter_label = ""
    Scene.bg_key = None
    Scene.char_key = None
    Scene.char_pos = "center"
    stop_ambience(200)


def run_story_from(start_index=0):
    global in_game, _pending_fadein
    import story
    nodes = story.STORY
    in_game = True
    if _pending_fadein:                       # 로드 직후 장면을 검은색에서 등장
        _pending_fadein = False
        if Scene.bg_key:
            scene_fade_in(560)
    try:
        i = max(0, start_index)
        while i < len(nodes):
            progress["index"] = i
            _capture_checkpoint(i)            # 노드 시작 상태 스냅샷(중복적용 방지)
            run_nodes([nodes[i]])
            if nodes[i][0] in ("result", "clear"):   # 챕터 경계에서 자동 저장
                progress["index"] = i + 1
                _capture_checkpoint(i + 1)
                save_game()
            i += 1
    finally:
        in_game = False


# ── 캐릭터 만들기 / 성향 설문 ─────────────────────────
def _cc_common(event):
    """생성 화면 공통 이벤트 : 종료 / 취소(ESC) / 언어 전환."""
    if event.type == pygame.QUIT:
        pygame.quit(); sys.exit(0)
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return "title"
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for rect, code in _lang_rects():
            if rect.collidepoint(event.pos):
                if code != i18n.current:
                    i18n.set_lang(code); save_settings()
                play_sfx("click")
                return "lang"
    return None


def _cc_button(rect, label, on, hover, serif=False, fs=20):
    surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    surf.fill((46, 42, 34, 252) if on else (34, 34, 40, 235) if hover else (20, 19, 17, 220))
    pygame.draw.rect(surf, GOLD if on else (104, 98, 86) if hover else (78, 74, 66),
                     surf.get_rect(), 2, border_radius=9)
    screen.blit(surf, rect.topleft)
    f = fit_font(label, fs, rect.w - 14, serif=serif)
    ts = f.render(label, True, GOLD if on else PARCH)
    screen.blit(ts, ts.get_rect(center=rect.center))


def _cc_options(x, y, keys, cur, cw, ch, gap, cols, mx, my, translate=True):
    hits = []
    for i, k in enumerate(keys):
        r = pygame.Rect(x + (i % cols) * (cw + gap), y + (i // cols) * (ch + gap), cw, ch)
        _cc_button(r, i18n.ui(k) if translate else k, k == cur, r.collidepoint(mx, my))
        hits.append((r, k))
    return hits


def _cc_section(label, x, y):
    screen.blit(get_font(19, bold=True, serif=True).render(label, True, GOLD), (x, y))


def _draw_swatches(x, y, cur_idx, mx, my):
    hits = []
    for i, col in enumerate(HAIR_COLORS):
        r = pygame.Rect(x + i * 46, y, 36, 36)
        pygame.draw.rect(screen, col, r, border_radius=8)
        sel = (i == cur_idx)
        pygame.draw.rect(screen, GOLD if sel else (90, 84, 74),
                         r.inflate(6, 6), 3 if sel else 1, border_radius=10)
        hits.append((r, i))
    return hits


def _cc_page_info():
    """1페이지 : 이름·성별·나이·전공·MBTI + 외형 미리보기. 반환 'next'/'title'."""
    name_active = False
    caret_on = True; caret_t = pygame.time.get_ticks()
    Scene.bg_key = "bg1"; Scene.char_key = None
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        nmax = NAME_MAX.get(i18n.current, 6)
        hot = {}                                  # (kind, value) → rect

        # ── 렌더 ──
        draw_scene_base(vignette=False)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((10, 9, 8, 205))
        screen.blit(ov, (0, 0))
        title = i18n.ui("cc_title")
        ts = fit_font(title, 38, WIDTH - 460, bold=True, serif=True).render(title, True, GOLD)
        screen.blit(ts, ts.get_rect(midtop=(WIDTH // 2, 54)))
        sub = get_font(17, serif=True).render(i18n.ui("cc_subtitle"), True, PARCH_DIM)
        screen.blit(sub, sub.get_rect(midtop=(WIDTH // 2, 98)))

        # 왼쪽 : 유화풍 초상 선택 (큰 미리보기 + 썸네일 격자)
        panel = pygame.Rect(64, 120, 372, 540)
        _panel(panel.x, panel.y, panel.w, panel.h, alpha=200)
        prev = portrait_cameo(profile["portrait"], 190, 244, radius=14)
        screen.blit(prev, prev.get_rect(midtop=(panel.centerx, panel.y + 12)))
        _cc_section(i18n.ui("cc_portrait"), panel.x + 24, panel.y + 272)
        cols, gap = 4, 8
        tw = (panel.w - 48 - (cols - 1) * gap) // cols
        th = int(tw * 1.02)
        gx = panel.x + 24; gy = panel.y + 300
        for i in range(PORTRAIT_COUNT):
            r = pygame.Rect(gx + (i % cols) * (tw + gap), gy + (i // cols) * (th + gap), tw, th)
            screen.blit(portrait_cameo(i, tw, th, radius=7), r.topleft)
            sel = (i == profile["portrait"])
            if sel or r.collidepoint(mx, my):
                pygame.draw.rect(screen, GOLD if sel else PARCH_DIM, r, 3, border_radius=7)
            hot[("portrait", i)] = r

        # 오른쪽 : 이름 / 성별 / 학년 / 전공 / MBTI
        rx = 470; ry = 132
        _cc_section(i18n.ui("cc_name"), rx, ry)
        nbox = pygame.Rect(rx, ry + 26, 740, 48)
        pygame.draw.rect(screen, (18, 17, 15), nbox, border_radius=8)
        pygame.draw.rect(screen, GOLD if name_active else (100, 94, 82), nbox, 2, border_radius=8)
        nm_txt = profile["name"] or ""
        if nm_txt:
            nsurf = name_font(nm_txt, 26, serif=True).render(nm_txt, True, PARCH)
        else:
            nsurf = get_font(20, serif=True).render(i18n.ui("cc_name_ph", n=nmax), True, GRAY)
        screen.blit(nsurf, (nbox.x + 14, nbox.centery - nsurf.get_height() // 2))
        if name_active and caret_on:
            cxp = nbox.x + 14 + (nsurf.get_width() if nm_txt else 0) + 2
            pygame.draw.line(screen, PARCH, (cxp, nbox.y + 10), (cxp, nbox.bottom - 10), 2)
        hot[("name", None)] = nbox

        _cc_section(i18n.ui("cc_gender"), rx, ry + 92)
        for r, k in _cc_options(rx, ry + 118, GENDER_KEYS, profile["gender"], 150, 40, 12, 3, mx, my):
            hot[("gender", k)] = r
        _cc_section(i18n.ui("cc_grade"), rx, ry + 178)
        for r, k in _cc_options(rx, ry + 204, GRADE_KEYS, profile["grade"], 150, 40, 12, 3, mx, my):
            hot[("grade", k)] = r
        _cc_section(i18n.ui("cc_major"), rx, ry + 264)
        for r, k in _cc_options(rx, ry + 290, MAJOR_KEYS, profile["major"], 130, 40, 12, 4, mx, my):
            hot[("major", k)] = r
        _cc_section(i18n.ui("cc_mbti"), rx, ry + 352)
        for r, k in _cc_options(rx, ry + 378, MBTI_TYPES, profile["mbti"], 86, 34, 8, 8, mx, my, translate=False):
            hot[("mbti", k)] = r

        # 하단 버튼
        rnd = pygame.Rect(rx, HEIGHT - 66, 150, 46)
        nxt = pygame.Rect(WIDTH - 250, HEIGHT - 66, 180, 46)
        _cc_button(rnd, i18n.ui("cc_random"), False, rnd.collidepoint(mx, my))
        ok_name = bool(profile["name"].strip())
        _cc_button(nxt, i18n.ui("cc_next"), ok_name, nxt.collidepoint(mx, my))
        hint = get_font(15).render(i18n.ui("cc_hint"), True, GRAY)
        screen.blit(hint, (70, HEIGHT - 30))
        draw_lang_selector()
        pygame.display.flip()

        if pygame.time.get_ticks() - caret_t > 480:
            caret_on = not caret_on; caret_t = pygame.time.get_ticks()

        # ── 이벤트 ──
        for event in pygame.event.get():
            r = _cc_common(event)
            if r == "title":
                return "title"
            if r == "lang":
                continue
            if event.type == pygame.TEXTINPUT and name_active:
                if len(profile["name"]) < nmax:
                    profile["name"] += event.text
            elif event.type == pygame.KEYDOWN:
                if name_active and event.key == pygame.K_BACKSPACE:
                    profile["name"] = profile["name"][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if profile["name"].strip():
                        play_sfx("click"); return "next"
                    name_active = True
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if nxt.collidepoint(event.pos) and ok_name:
                    play_sfx("click"); return "next"
                if rnd.collidepoint(event.pos):
                    _randomize_look(); play_sfx("click"); continue
                clicked_field = False
                for (kind, val), rect in hot.items():
                    if rect.collidepoint(event.pos):
                        clicked_field = True
                        if kind == "name":
                            name_active = True
                        else:
                            name_active = False
                            profile[kind] = val          # portrait/gender/grade/major/mbti
                            play_sfx("click")
                        break
                if not clicked_field:
                    name_active = False


def _randomize_look():
    import random as _r
    profile["portrait"] = _r.randrange(PORTRAIT_COUNT)
    profile["gender"] = _r.choice(GENDER_KEYS)
    profile["grade"] = _r.choice(GRADE_KEYS)
    profile["major"] = _r.choice(MAJOR_KEYS)
    profile["mbti"] = _r.choice(MBTI_TYPES)


def _cc_page_survey():
    """2페이지 : 성향 설문 3문항(유형당 변종 랜덤). 반환 'done'/'back'/'title'."""
    keys = list(i18n.SURVEY_DIMS)
    picks = pick_survey_variants()
    qs = [i18n.survey_ui_keys(dim, picks[dim]) for dim in keys]
    idx = 0
    while idx < len(qs):
        qt, qa, qb = qs[idx]
        while True:
            clock.tick(FPS)
            mx, my = pygame.mouse.get_pos()
            draw_scene_base(vignette=False)
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); ov.fill((10, 9, 8, 214))
            screen.blit(ov, (0, 0))
            ttl = i18n.ui("sv_title")
            ts = fit_font(ttl, 36, WIDTH - 460, bold=True, serif=True).render(ttl, True, GOLD)
            screen.blit(ts, ts.get_rect(midtop=(WIDTH // 2, 54)))
            intro = get_font(17, serif=True).render(i18n.ui("sv_intro"), True, PARCH_DIM)
            screen.blit(intro, intro.get_rect(midtop=(WIDTH // 2, 100)))
            prog = get_font(17, bold=True).render(i18n.ui("sv_progress", i=idx + 1, n=len(qs)), True, GOLD_SOFT)
            screen.blit(prog, prog.get_rect(midtop=(WIDTH // 2, 130)))

            qf = get_font(25, serif=True)
            qy = 190
            for line in wrap_text(i18n.ui(qt), qf, WIDTH - 260):
                ls = qf.render(line, True, PARCH)
                screen.blit(ls, ls.get_rect(midtop=(WIDTH // 2, qy)))
                qy += 38
            cur = profile["survey"][keys[idx]]
            aR = pygame.Rect(WIDTH // 2 - 470, 420, 460, 150)
            bR = pygame.Rect(WIDTH // 2 + 10, 420, 460, 150)
            for tag, rect, txt in (("A", aR, i18n.ui(qa)), ("B", bR, i18n.ui(qb))):
                on = (cur == tag); hover = rect.collidepoint(mx, my)
                surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                surf.fill((46, 42, 34, 250) if on else (30, 30, 36, 235) if hover else (20, 19, 17, 220))
                pygame.draw.rect(surf, GOLD if on else (104, 98, 86) if hover else (80, 76, 66),
                                 surf.get_rect(), 2, border_radius=12)
                screen.blit(surf, rect.topleft)
                tagc = get_font(30, bold=True, serif=True).render(tag, True, GOLD if on else GOLD_SOFT)
                screen.blit(tagc, (rect.x + 20, rect.y + 16))
                tf = get_font(20, serif=True)
                tyy = rect.y + 20
                for line in wrap_text(txt, tf, rect.w - 90):
                    screen.blit(tf.render(line, True, PARCH), (rect.x + 66, tyy))
                    tyy += 30
            back = pygame.Rect(70, HEIGHT - 66, 160, 46)
            _cc_button(back, i18n.ui("cc_prev"), False, back.collidepoint(mx, my))
            draw_lang_selector()
            pygame.display.flip()

            advanced = False
            for event in pygame.event.get():
                r = _cc_common(event)
                if r == "title":
                    return "title"
                if r == "lang":
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if aR.collidepoint(event.pos):
                        profile["survey"][keys[idx]] = "A"; play_sfx("click"); idx += 1; advanced = True; break
                    if bR.collidepoint(event.pos):
                        profile["survey"][keys[idx]] = "B"; play_sfx("click"); idx += 1; advanced = True; break
                    if back.collidepoint(event.pos):
                        play_sfx("click")
                        if idx == 0:
                            return "back"
                        idx -= 1; advanced = True; break
            if advanced:
                break
    return "done"

def create_character():
    """캐릭터 생성 전체 흐름. 완료 시 True, 취소 시 False(타이틀로)."""
    global profile, _player_turn
    _player_turn = False
    profile = default_profile()
    if load_profile():                            # 직전 캐릭터를 기본값으로 제안
        profile["survey"] = {"q1": None, "q2": None, "q3": None}
    pygame.key.start_text_input()
    try:
        while True:
            if _cc_page_info() == "title":
                return False
            res = _cc_page_survey()
            if res == "title":
                return False
            if res == "back":
                continue
            break
    finally:
        pygame.key.stop_text_input()
    apply_profile_name()
    save_profile()
    return True


def start_menu():
    global in_game
    in_game = False
    stop_ambience(300)
    Scene.bg_key = "bg1"
    Scene.char_key = None
    save_exists = has_save()
    meta = read_save_meta() if save_exists else None
    btns = []  # (rect, action)
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        # 저장본이 있으면 [이어하기(챕터 표시)][새 이야기], 없으면 [이야기 시작] 하나
        if save_exists:
            btns = [(pygame.Rect(WIDTH // 2 - 145, HEIGHT // 2 + 74, 290, 70), "continue"),
                    (pygame.Rect(WIDTH // 2 - 145, HEIGHT // 2 + 158, 290, 54), "new")]
        else:
            btns = [(pygame.Rect(WIDTH // 2 - 145, HEIGHT // 2 + 96, 290, 60), "new")]
        hovered = next((a for r, a in btns if r.collidepoint(mx, my)), None)
        for event in pygame.event.get():
            handle_common(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovered and not _on_lang(event.pos):
                play_sfx("click"); return hovered
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                play_sfx("click"); return "continue" if save_exists else "new"
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 120))
        screen.blit(veil, (0, 0))
        _vgrad(screen, (0, HEIGHT // 2 - 200, WIDTH, 400), 0, 0)
        cx = WIDTH // 2
        # 세로 리듬 : 제목 → (GAP1) → 부제 → (GAP2) → 구분선 → (GAP2) → 원작
        GAP1, GAP2 = 42, 30
        title_main = i18n.ui("title_main")
        t1 = fit_font(title_main, 74, WIDTH - 220, bold=True, serif=True)
        tw, th = t1.size(title_main)
        t2s = get_font(32, serif=True).render("The Weight of Courage", True, PARCH)
        credit = i18n.ui("menu_credit")
        t3s = fit_font(credit, 19, WIDTH - 160, serif=True).render(credit, True, GRAY)

        top = HEIGHT // 2 - 182
        _text_shadow(t1, title_main, RED, cx - tw // 2, top, sa=200)
        y = top + th + GAP1
        screen.blit(t2s, t2s.get_rect(midtop=(cx, y)))
        y += t2s.get_height() + GAP2
        pygame.draw.line(screen, (*GOLD_SOFT, 120), (cx - 180, y), (cx + 180, y), 1)
        y += GAP2
        screen.blit(t3s, t3s.get_rect(midtop=(cx, y)))
        for r, action in btns:
            hover = (action == hovered)
            surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            surf.fill((40, 36, 30, 250) if hover else (18, 16, 14, 220))
            pygame.draw.rect(surf, GOLD if hover else (110, 104, 92), surf.get_rect(), 2, border_radius=10)
            screen.blit(surf, r.topleft)
            if action == "continue":
                cap = i18n.t(meta["label"]) if (meta and meta.get("label")) else None
                bt = get_font(25, bold=True, serif=True).render(i18n.ui("menu_continue"), True, GOLD)
                if cap:
                    screen.blit(bt, bt.get_rect(center=(r.centerx, r.centery - 11)))
                    cs = fit_font(cap, 15, r.w - 40, serif=True).render(cap, True, PARCH_DIM)
                    screen.blit(cs, cs.get_rect(center=(r.centerx, r.centery + 15)))
                else:
                    screen.blit(bt, bt.get_rect(center=r.center))
            else:
                label = i18n.ui("menu_new") if save_exists else i18n.ui("menu_start")
                bt = get_font(26, bold=True, serif=True).render(label, True, GOLD if hover else PARCH)
                screen.blit(bt, bt.get_rect(center=r.center))
        hint = get_font(17).render(i18n.ui("menu_hint"), True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 38)))
        draw_lang_selector()
        pygame.display.flip()


def main():
    load_settings()
    while True:                                   # 타이틀 ↔ 플레이 루프
        action = start_menu()
        if action == "continue" and has_save():
            if not load_game():
                reset_state()
        else:
            if not create_character():            # 새 이야기 → 캐릭터 생성(취소 시 타이틀로)
                continue
            reset_state()
        while True:                               # 플레이 중 '불러오기' 재개 처리
            try:
                run_story_from(progress["index"])
                break                             # 정상 종료/엔딩 → 타이틀로
            except ReloadStory:
                continue                          # 상태 적용됨 → 새 위치에서 재개
            except ReturnToTitle:
                break                             # 메인 화면으로


if __name__ == "__main__":
    main()
