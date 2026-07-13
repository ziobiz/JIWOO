# -*- coding: utf-8 -*-
"""
붉은 무공훈장 : The Weight of Courage
pygame 비주얼 노벨 엔진 (스탯 시스템 v2)

스탯 : 신뢰 · 공감 · 인간본능 · 사회적역할 · 죄책감 · 용기 (+숨김: 전쟁체험도)
상단 : 갈등의 저울 (인간으로 살아남기 ⚖ 군인으로 살아가기)
수집 : 기억 조각 (군복 · 짐의 군번줄 · 붉은 손수건 · 탄피 · 마지막 깃발)
엔딩 : TRUE / GOOD / NORMAL / BAD / HIDDEN

실행:  python game.py       (TAB: 스탯 패널 On/Off, ESC: 종료)
필요:  pip install pygame-ce
"""
import io
import os
import sys

try:
    import pygame
except ImportError:
    print("pygame 이 필요합니다.  터미널에서:  pip install pygame-ce")
    sys.exit(1)

# ────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 60
TYPE_SPEED = 42

# 실행 위치 판별 : PyInstaller 로 빌드된 exe 든, 그냥 .py 든 항상
# '실행 파일(또는 스크립트) 옆의 assets 폴더'를 찾도록 한다.
#   - frozen(exe) : sys.executable 이 있는 폴더  → exe 옆 assets (외부 폴더, 이미지 교체 가능)
#   - 일반 .py    : 이 파일이 있는 폴더           → game.py 옆 assets
if getattr(sys, "frozen", False):          # PyInstaller / cx_Freeze 등으로 빌드된 경우
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(HERE, "assets")

WHITE = (238, 238, 240)
BLACK = (12, 12, 14)
GOLD = (216, 182, 120)
BLUE = (150, 190, 230)
GRAY = (168, 168, 174)
RED = (176, 58, 52)
GREEN = (120, 200, 140)
BOX_BG = (18, 20, 26)

# 스탯별 게이지 색
STAT_COLOR = {
    "신뢰": (210, 150, 90),
    "공감": (150, 190, 230),
    "인간본능": (120, 200, 140),
    "사회적역할": (150, 156, 200),
    "죄책감": (176, 88, 96),
    "용기": (216, 182, 120),
}
# 화면 표시용 라벨
STAT_LABEL = {
    "신뢰": "신뢰도", "공감": "공감",
    "인간본능": "인간 본능", "사회적역할": "사회적 역할",
    "죄책감": "죄책감", "용기": "용기",
}
# HUD 그룹 (헤더, [스탯키...])
HUD_GROUPS = [
    ("Henry", ["신뢰", "공감"]),
    ("플레이어", ["인간본능", "사회적역할"]),
    ("헨리", ["죄책감", "용기"]),
]
# 기억 조각 전체 (히든 엔딩 조건)
ALL_FRAGMENTS = ["군복", "짐의 군번줄", "붉은 손수건", "탄피", "마지막 깃발"]

# 이미지 키 → 파일 '기본 이름'(확장자 제외). 실제 파일은 .png/.jpg 등 무엇이든 매칭됨.
IMG_BASE = {
    "henry": "henry",
    "jim": "jim",
    "wilson": "wilson",      # 윌슨 (3장)
    "player1": "player(1)",
    "player2": "player(2)",
    "talk": "talk",          # 대사창(말풍선) 배경
    # 기억 조각 아이콘
    "clothes": "clothes",    # 군복
    "ballchain": "ballchain",  # 짐의 군번줄
    "scarf": "scarf",        # 붉은 손수건
    "empshell": "empshell",  # 탄피
    "flag": "flag",          # 마지막 깃발
}
for i in range(1, 17):
    IMG_BASE[f"bg{i}"] = f"bg({i})"

# 기억 조각 이름 → 아이콘 키
FRAGMENT_ICON = {
    "군복": "clothes",
    "짐의 군번줄": "ballchain",
    "붉은 손수건": "scarf",
    "탄피": "empshell",
    "마지막 깃발": "flag",
}

# 야영지 계열 배경 (이 배경일 때만 campfirebgm 재생)
CAMP_BGS = {"bg6", "bg7", "bg8", "bg10", "bg11"}

CARD_ACCENT = {
    "time": GRAY, "mission": GOLD, "system": BLUE,
    "quest": GREEN, "item": GOLD, "question": WHITE, "fear": RED,
}

# ────────────────────────────────────────────────────────────────
pygame.init()
pygame.display.set_caption("붉은 무공훈장 : The Weight of Courage")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def _korean_font_path(bold=False):
    cands = (
        [r"C:\Windows\Fonts\malgunbd.ttf", r"C:\Windows\Fonts\malgun.ttf"]
        if bold else
        [r"C:\Windows\Fonts\malgun.ttf", r"C:\Windows\Fonts\malgunbd.ttf"]
    )
    for p in cands:
        if os.path.exists(p):
            return p
    return None


_FONT_CACHE = {}


def get_font(size, bold=False):
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    path = _korean_font_path(bold)
    if path:
        f = pygame.font.Font(path, size)
    else:
        f = pygame.font.SysFont("malgungothic,applegothic,gulim,arial", size, bold=bold)
    _FONT_CACHE[key] = f
    return f


# ── 이미지 ───────────────────────────────────────────
_IMG_CACHE = {}
_ASSET_INDEX = None
_IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")


def _find_asset(key):
    """확장자·대소문자 무관하게 assets 폴더에서 파일을 찾는다. 없으면 None."""
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


def _placeholder(key):
    surf = pygame.Surface((WIDTH, HEIGHT))
    h = (abs(hash(key)) % 360)
    col = pygame.Color(0)
    col.hsva = (h, 35, 26, 100)
    surf.fill(col)
    dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 4):
        a = int(120 * (y / HEIGHT))
        pygame.draw.rect(dark, (0, 0, 0, a), (0, y, WIDTH, 4))
    surf.blit(dark, (0, 0))
    label = get_font(40, bold=True).render(f"[{key}]", True, (235, 235, 235))
    surf.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    hint = get_font(22).render("assets 폴더에 이미지를 넣으면 여기에 표시됩니다", True, (210, 210, 210))
    surf.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 44)))
    return surf


def _safe_load(path):
    """한글 경로에서도 안전하게 로드 (바이트로 읽어 포맷 힌트와 함께 디코드)."""
    with open(path, "rb") as f:
        data = f.read()
    return pygame.image.load(io.BytesIO(data), path)


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


def load_char(key):
    ck = ("char", key)
    if ck in _IMG_CACHE:
        return _IMG_CACHE[ck]
    path = _find_asset(key)
    img = None
    if path:
        try:
            src = _safe_load(path).convert_alpha()
            target_h = int(HEIGHT * 0.74)
            ratio = target_h / src.get_height()
            target_w = int(src.get_width() * ratio)
            if target_w > WIDTH * 0.62:
                target_w = int(WIDTH * 0.62)
                ratio = target_w / src.get_width()
                target_h = int(src.get_height() * ratio)
            img = pygame.transform.smoothscale(src, (target_w, target_h))
        except Exception as e:
            print(f"[경고] 캐릭터 로드 실패 {path}: {e}")
            img = None
    if img is None:
        img = pygame.Surface((360, 520), pygame.SRCALPHA)
        pygame.draw.rect(img, (60, 64, 78, 230), (0, 0, 360, 520), border_radius=24)
        pygame.draw.rect(img, (150, 156, 176, 255), (0, 0, 360, 520), 3, border_radius=24)
        label = get_font(30, bold=True).render(key, True, WHITE)
        img.blit(label, label.get_rect(center=(180, 260)))
    _IMG_CACHE[ck] = img
    return img


def load_ui(key, size):
    """UI 이미지(talk 등)를 주어진 크기로 로드. 없으면 None."""
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
    """기억 조각 아이콘 로드. 없으면 None."""
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


# ── 오디오 ───────────────────────────────────────────
AUDIO_OK = False
try:
    pygame.mixer.init()
    AUDIO_OK = True
except Exception as _e:
    print(f"[알림] 오디오 장치를 열 수 없어 소리 없이 실행합니다: {_e}")

_SFX_CACHE = {}
_AUDIO_EXTS = (".mp3", ".ogg", ".wav")


def _find_audio(name):
    for ext in _AUDIO_EXTS:
        p = os.path.join(ASSET_DIR, name + ext)
        if os.path.exists(p):
            return p
    return None


def play_sfx(name, vol=0.7):
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
            snd.set_volume(vol)
            snd.play()
        except Exception:
            pass


# 배경음: base(책 진입 후 기본 곡)와 야영지(campfirebgm)를 자동 전환
_music = {"cur": None, "base": None, "base_on": False}


def _play_music_file(name, vol=0.45):
    if not AUDIO_OK or _music["cur"] == name:
        return
    p = _find_audio(name)
    if not p:
        return
    try:
        pygame.mixer.music.load(p)
        pygame.mixer.music.set_volume(vol)
        pygame.mixer.music.play(-1)
        _music["cur"] = name
    except Exception:
        pass


def start_base_bgm(name="bgm"):
    """책에 빨려 들어간 이후 기본 BGM 시작."""
    _music["base"] = name
    _music["base_on"] = True
    _play_music_file(name)


def update_bgm_for_bg(bgkey):
    """배경이 바뀔 때 호출: 야영지면 campfirebgm, 아니면 기본 BGM."""
    if not _music["base_on"]:
        return
    _play_music_file("campfirebgm" if bgkey in CAMP_BGS else _music["base"])


# ────────────────────────────────────────────────────────────────
# 전역 상태
class Scene:
    bg_key = None
    char_key = None
    char_pos = "center"


stats = {}                       # 신뢰/공감/인간본능/사회적역할/죄책감/용기/전쟁체험도
conflict = {"인간": 0, "군인": 0}   # 갈등의 저울
items = []                        # 기억 조각
toasts = []                       # [[text, color, expire_ms]]
hud_visible = True


def _toast(text, color):
    toasts.append([text, color, pygame.time.get_ticks() + 1800])


def apply_effects(changes):
    """선택지/이벤트 효과. 키: 스탯명 / '인간' / '군인'."""
    for k, v in changes.items():
        if k in ("인간", "군인"):
            conflict[k] = max(0, conflict[k] + v)
            _toast(f"{'인간으로 살아남기' if k == '인간' else '군인으로 살아가기'} {'+' if v >= 0 else ''}{v}",
                   GREEN if k == "인간" else STAT_COLOR["사회적역할"])
        else:
            stats[k] = max(0, min(100, stats.get(k, 0) + v))
            if k != "전쟁체험도":   # 전쟁체험도는 숨김 스탯
                sign = "+" if v >= 0 else ""
                _toast(f"{STAT_LABEL.get(k, k)} {sign}{v}", GREEN if v >= 0 else RED)


def grant_item(name):
    if name not in items:
        items.append(name)
        _toast(f"기억 조각 획득 : {name}", GOLD)
        play_sfx("item")


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


# ── 그리기 ───────────────────────────────────────────
def draw_scene_base():
    if Scene.bg_key:
        screen.blit(load_bg(Scene.bg_key), (0, 0))
    else:
        screen.fill(BLACK)
    if Scene.char_key:
        img = load_char(Scene.char_key)
        xpos = {"left": 0.30, "center": 0.5, "right": 0.70}.get(Scene.char_pos, 0.5)
        rect = img.get_rect()
        rect.midbottom = (int(WIDTH * xpos), HEIGHT - 175)
        screen.blit(img, rect)


def _bar(x, y, w, val, color, maxv=100):
    """게이지 바 한 줄 그리기 (라벨 없이 트랙+채움)."""
    h = 11
    track = pygame.Surface((w, h), pygame.SRCALPHA)
    track.fill((40, 42, 50, 220))
    pygame.draw.rect(track, (90, 92, 104, 255), track.get_rect(), 1, border_radius=4)
    screen.blit(track, (x, y))
    fw = int(w * max(0, min(1, val / maxv)))
    if fw > 0:
        fill = pygame.Surface((fw, h), pygame.SRCALPHA)
        fill.fill((*color, 235))
        screen.blit(fill, (x, y))


def draw_conflict_scale():
    """상단: 갈등의 저울 (항상 표시)."""
    x, y, w = 18, 14, 430
    panel = pygame.Surface((w, 118), pygame.SRCALPHA)
    panel.fill((10, 12, 18, 195))
    pygame.draw.rect(panel, (100, 106, 126, 255), panel.get_rect(), 1, border_radius=8)
    screen.blit(panel, (x, y))
    ttl = get_font(17, bold=True).render("⚖  갈등의 저울", True, GOLD)
    screen.blit(ttl, (x + 14, y + 10))
    h_val, s_val = conflict["인간"], conflict["군인"]
    scale = max(100, h_val, s_val)
    f = get_font(16)
    screen.blit(f.render(f"인간으로 살아남기  {h_val}", True, GREEN), (x + 14, y + 38))
    _bar(x + 14, y + 58, w - 28, h_val, GREEN, scale)
    screen.blit(f.render(f"군인으로 살아가기  {s_val}", True, STAT_COLOR["사회적역할"]), (x + 14, y + 74))
    _bar(x + 14, y + 94, w - 28, s_val, STAT_COLOR["사회적역할"], scale)


def draw_gauges():
    """우측 상단: 스탯 게이지 패널 (TAB 로 On/Off)."""
    x, w = WIDTH - 262, 246
    y = 14
    rows = sum(len(g[1]) for g in HUD_GROUPS)
    h = 16 + len(HUD_GROUPS) * 24 + rows * 34 + 12
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    panel.fill((10, 12, 18, 195))
    pygame.draw.rect(panel, (100, 106, 126, 255), panel.get_rect(), 1, border_radius=8)
    screen.blit(panel, (x, y))
    cy = y + 12
    lf = get_font(16)
    for header, keys in HUD_GROUPS:
        hs = get_font(15, bold=True).render(f"— {header} —", True, GRAY)
        screen.blit(hs, (x + 14, cy))
        cy += 24
        for k in keys:
            val = stats.get(k, 0)
            screen.blit(lf.render(STAT_LABEL[k], True, WHITE), (x + 16, cy))
            vs = lf.render(str(val), True, STAT_COLOR[k])
            screen.blit(vs, (x + w - 16 - vs.get_width(), cy))
            _bar(x + 16, cy + 20, w - 32, val, STAT_COLOR[k])
            cy += 34
    # 기억 조각 개수
    frag = get_font(15).render(f"기억 조각  {len(items)} / {len(ALL_FRAGMENTS)}", True, GOLD)
    screen.blit(frag, (x + 14, y + h - 26))


def draw_toasts():
    now = pygame.time.get_ticks()
    toasts[:] = [t for t in toasts if t[2] > now]
    f = get_font(23, bold=True)
    for i, (text, col, exp) in enumerate(toasts[-5:]):
        remain = exp - now
        alpha = min(255, int(255 * remain / 700)) if remain < 700 else 255
        surf = f.render(text, True, col)
        bg = pygame.Surface((surf.get_width() + 26, surf.get_height() + 12), pygame.SRCALPHA)
        bg.fill((10, 12, 18, min(210, alpha)))
        pygame.draw.rect(bg, (*col, alpha), bg.get_rect(), 1, border_radius=6)
        bg.blit(surf, (13, 6))
        bg.set_alpha(alpha)
        screen.blit(bg, (WIDTH // 2 - bg.get_width() // 2, HEIGHT - 330 + i * 40))


def draw_overlays():
    draw_conflict_scale()
    if hud_visible:
        draw_gauges()
    draw_toasts()


def draw_dialog_box(name, text, name_color, text_color):
    margin, box_h = 50, 210
    box_y = HEIGHT - box_h - 30
    box_w = WIDTH - margin * 2
    art = load_ui("talk", (box_w, box_h))     # talk.png 있으면 말풍선 이미지 사용
    if art is not None:
        screen.blit(art, (margin, box_y))
    else:
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((*BOX_BG, 224))
        pygame.draw.rect(box, (110, 116, 140, 255), box.get_rect(), 2, border_radius=10)
        screen.blit(box, (margin, box_y))

    inner_x = margin + 34
    text_top = box_y + 34
    if name:
        tab = get_font(26, bold=True).render(name, True, name_color)
        tw = tab.get_width() + 36
        tab_bg = pygame.Surface((tw, 42), pygame.SRCALPHA)
        tab_bg.fill((*BOX_BG, 240))
        pygame.draw.rect(tab_bg, (*name_color, 255), tab_bg.get_rect(), 2, border_radius=8)
        tab_bg.blit(tab, (18, 6))
        screen.blit(tab_bg, (margin + 24, box_y - 24))
        text_top = box_y + 40

    f = get_font(30)
    for i, line in enumerate(wrap_text(text, f, WIDTH - margin * 2 - 68)[:4]):
        screen.blit(f.render(line, True, text_color), (inner_x, text_top + i * 40))


def draw_hint(fully_shown):
    if fully_shown and (pygame.time.get_ticks() // 500) % 2 == 0:
        screen.blit(get_font(20).render("▶  클릭 / Space", True, GRAY), (WIDTH - 220, HEIGHT - 34))


# ── 이벤트 ───────────────────────────────────────────
def handle_common(event):
    global hud_visible
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit(0)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        if event.key == pygame.K_TAB:
            hud_visible = not hud_visible


def is_advance(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        return True
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
        return True
    return False


# ── 대사 ─────────────────────────────────────────────
def show_text(text, name=None, name_color=WHITE, text_color=WHITE):
    f = get_font(30)
    full = "\n".join(wrap_text(text, f, WIDTH - 50 * 2 - 68))
    revealed, done = 0.0, False
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event):
                if not done:
                    revealed, done = len(full), True
                else:
                    return
        if not done:
            revealed += TYPE_SPEED * dt / 1000.0
            if revealed >= len(full):
                revealed, done = len(full), True
        draw_scene_base()
        draw_dialog_box(name, full[:int(revealed)].replace("\n", " "), name_color, text_color)
        draw_overlays()
        draw_hint(done)
        pygame.display.flip()


# ── 선택지 ───────────────────────────────────────────
def show_choice(options):
    labels = [o[0] for o in options]
    f = get_font(26, bold=True)
    bw, bh, gap = 860, 60, 18
    total = len(labels) * bh + (len(labels) - 1) * gap
    start_y = HEIGHT // 2 - total // 2 + 40
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        hover, rects = -1, []
        for i in range(len(labels)):
            r = pygame.Rect(WIDTH // 2 - bw // 2, start_y + i * (bh + gap), bw, bh)
            rects.append(r)
            if r.collidepoint(mx, my):
                hover = i
        for event in pygame.event.get():
            handle_common(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hover >= 0:
                play_sfx("click")
                return hover
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 120))
        screen.blit(veil, (0, 0))
        q = get_font(24).render("당신의 선택은?", True, GOLD)
        screen.blit(q, q.get_rect(center=(WIDTH // 2, start_y - 46)))
        for i, r in enumerate(rects):
            sel = (i == hover)
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            surf.fill((30, 34, 46, 245) if sel else (18, 20, 28, 225))
            pygame.draw.rect(surf, (GOLD if sel else (110, 116, 140)), surf.get_rect(), 2, border_radius=8)
            screen.blit(surf, r.topleft)
            txt = f.render(labels[i], True, GOLD if sel else WHITE)
            screen.blit(txt, txt.get_rect(midleft=(r.x + 28, r.centery)))
        draw_overlays()
        pygame.display.flip()


# ── 타이틀 ───────────────────────────────────────────
def show_title(lines, sub=None):
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 400:
                return
        screen.fill(BLACK)
        pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 70))
        pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 70, WIDTH, 70))
        t = pygame.time.get_ticks() - start
        alpha = min(255, int(255 * t / 600))
        cy = HEIGHT // 2 - (30 if sub else 0)
        for i, line in enumerate(lines):
            fnt = get_font(66 if i == 0 else 44, bold=True)
            surf = fnt.render(line, True, GOLD if i == 0 else WHITE)
            surf.set_alpha(alpha)
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, cy + i * 78)))
        if sub:
            fy = cy + len(lines) * 78 + 30
            for j, s in enumerate(wrap_text(sub, get_font(24), WIDTH - 240)):
                ss = get_font(24).render(s, True, GRAY)
                ss.set_alpha(alpha)
                screen.blit(ss, ss.get_rect(center=(WIDTH // 2, fy + j * 34)))
        pygame.display.flip()


# ── 카드 ─────────────────────────────────────────────
def show_card(kind, title, body):
    accent = CARD_ACCENT.get(kind, WHITE)
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 250:
                return
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 170))
        screen.blit(veil, (0, 0))
        body_lines = []
        for b in body:
            body_lines.extend(wrap_text(b, get_font(24), WIDTH - 320) if b else [""])
        card_w = 760
        card_h = 150 + len(body_lines) * 34
        cx, cy = WIDTH // 2 - card_w // 2, HEIGHT // 2 - card_h // 2
        panel = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        panel.fill((14, 16, 22, 245))
        pygame.draw.rect(panel, (*accent, 255), panel.get_rect(), 2, border_radius=12)
        pygame.draw.rect(panel, (*accent, 255), (0, 0, card_w, 6))
        screen.blit(panel, (cx, cy))
        tt = get_font(36, bold=True).render(title, True, accent)
        screen.blit(tt, tt.get_rect(center=(WIDTH // 2, cy + 52)))
        pygame.draw.line(screen, (*accent, 160), (cx + 60, cy + 92), (cx + card_w - 60, cy + 92), 1)
        for i, line in enumerate(body_lines):
            ls = get_font(24).render(line, True, WHITE)
            screen.blit(ls, ls.get_rect(center=(WIDTH // 2, cy + 122 + i * 34)))
        draw_overlays()
        pygame.display.flip()


def show_flash():
    for a in list(range(0, 256, 24)) + list(range(255, -1, -18)):
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((255, 255, 255, a))
        screen.blit(veil, (0, 0))
        pygame.display.flip()


def show_black():
    Scene.bg_key = None
    Scene.char_key = None
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 300:
                return
        screen.fill(BLACK)
        pygame.display.flip()


# ── 자유 탐색 ────────────────────────────────────────
def run_explore(locations):
    visited = set()
    saved_bg, saved_char, saved_pos = Scene.bg_key, Scene.char_key, Scene.char_pos
    while len(visited) < len(locations):
        remaining = [(name, nodes) for name, nodes in locations if name not in visited]
        Scene.bg_key, Scene.char_key = saved_bg, None
        idx = show_choice_menu(
            "어디를 조사할까?  (모두 조사하면 헨리에게 돌아갈 수 있다)",
            [f"▶ {name}" for name, _ in remaining],
            footer=f"조사 완료 {len(visited)} / {len(locations)}",
        )
        name, nodes = remaining[idx]
        run_nodes(nodes)
        visited.add(name)
    Scene.bg_key, Scene.char_key, Scene.char_pos = saved_bg, saved_char, saved_pos


def show_choice_menu(question, labels, footer=None):
    f = get_font(26, bold=True)
    bw, bh, gap = 720, 58, 16
    total = len(labels) * bh + (len(labels) - 1) * gap
    start_y = HEIGHT // 2 - total // 2 + 30
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        hover, rects = -1, []
        for i in range(len(labels)):
            r = pygame.Rect(WIDTH // 2 - bw // 2, start_y + i * (bh + gap), bw, bh)
            rects.append(r)
            if r.collidepoint(mx, my):
                hover = i
        for event in pygame.event.get():
            handle_common(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hover >= 0:
                play_sfx("click")
                return hover
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        screen.blit(veil, (0, 0))
        q = get_font(26, bold=True).render(question, True, GOLD)
        screen.blit(q, q.get_rect(center=(WIDTH // 2, start_y - 50)))
        for i, r in enumerate(rects):
            sel = (i == hover)
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            surf.fill((30, 34, 46, 245) if sel else (18, 20, 28, 225))
            pygame.draw.rect(surf, (GOLD if sel else (110, 116, 140)), surf.get_rect(), 2, border_radius=8)
            screen.blit(surf, r.topleft)
            txt = f.render(labels[i], True, GOLD if sel else WHITE)
            screen.blit(txt, txt.get_rect(midleft=(r.x + 26, r.centery)))
        if footer:
            fs = get_font(22).render(footer, True, GRAY)
            screen.blit(fs, fs.get_rect(center=(WIDTH // 2, start_y + total + 40)))
        draw_overlays()
        pygame.display.flip()


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
    """cond = (key, op, val). key: 스탯명 / '조각수' / '인간' / '군인'."""
    key, op, val = cond
    if key == "조각수":
        left = len(items)
    elif key in ("인간", "군인"):
        left = conflict.get(key, 0)
    else:
        left = stats.get(key, 0)
    return _cmp(left, op, val)


def _stat_scale_panel(oy=250):
    """스탯 6종 + 갈등의 저울 + 기억 조각을 그린다 (결과/엔딩 공용)."""
    ox = 180
    gs = get_font(20, bold=True).render("스탯", True, GRAY)
    screen.blit(gs, (ox, oy - 34))
    for i, k in enumerate(["신뢰", "공감", "인간본능", "사회적역할", "죄책감", "용기"]):
        y = oy + i * 40
        screen.blit(get_font(20).render(STAT_LABEL[k], True, WHITE), (ox, y - 2))
        _bar(ox + 130, y + 4, 200, stats.get(k, 0), STAT_COLOR[k])
        screen.blit(get_font(18).render(str(stats.get(k, 0)), True, STAT_COLOR[k]), (ox + 340, y - 2))
    rx, ry = WIDTH - 470, oy
    m = max(100, conflict["인간"], conflict["군인"])
    screen.blit(get_font(20, bold=True).render("갈등의 저울", True, GRAY), (rx, ry - 34))
    screen.blit(get_font(20).render(f"인간으로 살아남기  {conflict['인간']}", True, GREEN), (rx, ry))
    _bar(rx, ry + 26, 300, conflict["인간"], GREEN, m)
    screen.blit(get_font(20).render(f"군인으로 살아가기  {conflict['군인']}", True, STAT_COLOR["사회적역할"]), (rx, ry + 50))
    _bar(rx, ry + 76, 300, conflict["군인"], STAT_COLOR["사회적역할"], m)
    # 기억 조각 아이콘 (보유=선명, 미보유=흐림)
    screen.blit(get_font(19).render(f"기억 조각  {len(items)}/{len(ALL_FRAGMENTS)}", True, GOLD), (rx, ry + 112))
    for i, frag in enumerate(ALL_FRAGMENTS):
        ix, iy = rx + i * 58, ry + 138
        icon = load_icon(frag, 48)
        owned = frag in items
        if icon is not None:
            surf = icon.copy()
            if not owned:
                surf.set_alpha(60)
            screen.blit(surf, (ix, iy))
        else:
            pygame.draw.rect(screen, (GOLD if owned else (70, 72, 82)), (ix, iy, 48, 48), 2, border_radius=6)
        if owned:
            pygame.draw.rect(screen, GOLD, (ix, iy, 48, 48), 1, border_radius=6)


def show_result(title):
    """Chapter Result 화면."""
    start = pygame.time.get_ticks()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            handle_common(event)
            if is_advance(event) and pygame.time.get_ticks() - start > 400:
                return
        screen.fill(BLACK)
        tt = get_font(40, bold=True).render(title, True, GOLD)
        screen.blit(tt, tt.get_rect(center=(WIDTH // 2, 90)))
        _stat_scale_panel(oy=230)
        note = get_font(22).render("▶  클릭하여 계속", True, GRAY)
        screen.blit(note, note.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
        pygame.display.flip()


def show_final_question():
    """마지막 화면: 당신에게 용기란 무엇입니까? (저장되지 않음)"""
    opts = ["① 두려움이 없는 것", "② 두려움을 이겨내는 것",
            "③ 두려움을 인정하고도 행동하는 것", "④ 아직 모르겠다"]
    f = get_font(26, bold=True)
    bw, bh, gap = 640, 58, 16
    total = len(opts) * bh + (len(opts) - 1) * gap
    start_y = HEIGHT // 2 - total // 2 + 30
    picked = None
    picked_at = 0
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        hover, rects = -1, []
        for i in range(len(opts)):
            r = pygame.Rect(WIDTH // 2 - bw // 2, start_y + i * (bh + gap), bw, bh)
            rects.append(r)
            if r.collidepoint(mx, my):
                hover = i
        for event in pygame.event.get():
            handle_common(event)
            if picked is None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hover >= 0:
                picked = hover
                picked_at = pygame.time.get_ticks()
                play_sfx("click")
            elif picked is not None and is_advance(event) and pygame.time.get_ticks() - picked_at > 400:
                return
        screen.fill(BLACK)
        q = get_font(30, bold=True).render("당신에게 용기란 무엇입니까?", True, GOLD)
        screen.blit(q, q.get_rect(center=(WIDTH // 2, start_y - 70)))
        for i, r in enumerate(rects):
            sel = (i == hover) or (i == picked)
            surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            surf.fill((30, 34, 46, 245) if sel else (18, 20, 28, 225))
            pygame.draw.rect(surf, (GOLD if (i == picked) else (110, 116, 140)), surf.get_rect(), 2, border_radius=8)
            screen.blit(surf, r.topleft)
            txt = f.render(opts[i], True, GOLD if sel else WHITE)
            screen.blit(txt, txt.get_rect(midleft=(r.x + 26, r.centery)))
        if picked is not None:
            th = get_font(22).render("당신의 대답은 저장되지 않습니다.  ·  클릭하면 종료", True, GRAY)
            screen.blit(th, th.get_rect(center=(WIDTH // 2, HEIGHT - 60)))
        else:
            th = get_font(20).render("(선택은 저장되지 않습니다.)", True, GRAY)
            screen.blit(th, th.get_rect(center=(WIDTH // 2, start_y + total + 40)))
        pygame.display.flip()


def run_ending():
    import story
    code = determine_ending()
    run_nodes(story.ENDINGS.get(code, []))
    show_result(ENDING_TITLE.get(code, code))
    show_final_question()


# ────────────────────────────────────────────────────────────────
def run_nodes(nodes):
    for node in nodes:
        kind = node[0]
        if kind == "bg":
            Scene.bg_key = node[1]
            update_bgm_for_bg(node[1])
        elif kind == "sfx":
            play_sfx(node[1])
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
            show_text(node[2], name=node[1], name_color=WHITE, text_color=WHITE)
        elif kind == "mono":
            show_text(node[1], name="속마음", name_color=BLUE, text_color=BLUE)
        elif kind == "narr":
            show_text(node[1], name=None, text_color=GOLD)
        elif kind == "act":
            show_text(node[1], name=None, text_color=GRAY)
        elif kind == "title":
            show_title(node[1], node[2] if len(node) > 2 else None)
        elif kind == "card":
            show_card(node[1], node[2], node[3])
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
            show_result(node[1])
        elif kind == "cond":
            # ("cond", (key, op, val), then_nodes, else_nodes)
            then_nodes = node[2] if len(node) > 2 else []
            else_nodes = node[3] if len(node) > 3 else []
            run_nodes(then_nodes if eval_cond(node[1]) else else_nodes)
        elif kind == "ending":
            run_ending()
            pygame.quit()
            sys.exit(0)


def start_menu():
    Scene.bg_key = "bg1"
    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        btn = pygame.Rect(WIDTH // 2 - 140, HEIGHT // 2 + 80, 280, 64)
        hover = btn.collidepoint(mx, my)
        for event in pygame.event.get():
            handle_common(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hover:
                play_sfx("click")
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                return
        draw_scene_base()
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        screen.blit(veil, (0, 0))
        t1 = get_font(64, bold=True).render("붉은 무공훈장", True, RED)
        screen.blit(t1, t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90)))
        t2 = get_font(34).render("The Weight of Courage", True, WHITE)
        screen.blit(t2, t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
        t3 = get_font(20).render("원작 : Stephen Crane 『The Red Badge of Courage』", True, GRAY)
        screen.blit(t3, t3.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 16)))
        surf = pygame.Surface((btn.w, btn.h), pygame.SRCALPHA)
        surf.fill((30, 34, 46, 245) if hover else (18, 20, 28, 225))
        pygame.draw.rect(surf, GOLD if hover else (120, 126, 150), surf.get_rect(), 2, border_radius=10)
        screen.blit(surf, btn.topleft)
        bt = get_font(28, bold=True).render("시작하기", True, GOLD if hover else WHITE)
        screen.blit(bt, bt.get_rect(center=btn.center))
        hint = get_font(18).render("TAB : 스탯 패널 On/Off   ·   ESC : 종료", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 40)))
        pygame.display.flip()


def main():
    import story
    stats.clear()
    stats.update(dict(story.INITIAL_STATS))
    conflict.update({"인간": 0, "군인": 0})
    items.clear()
    start_menu()
    run_nodes(story.STORY)
    pygame.quit()


if __name__ == "__main__":
    main()
