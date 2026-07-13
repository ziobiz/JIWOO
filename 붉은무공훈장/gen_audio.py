# -*- coding: utf-8 -*-
"""
붉은 무공훈장 : 효과음 · 배경음악 합성 생성기  (v2 · 감정선 사운드트랙)
────────────────────────────────────────────────────────────────
외부 음원 없이 numpy 로 파형을 직접 '샘플링(합성)'하여 assets/ 에 WAV 로 저장.
game.py 가 .wav 를 자동 인식한다.

■ 효과음 (극의 맥락과 1:1 매칭)
   page      책장 넘김        wind      바람 소리
   bugle     나팔 소리(집합)   heartbeat 심장 박동(긴장)
   shifting  책이 빛나는 전환   gun       총성
   bomb      포탄             foot      돌격 발소리
   item      기억 조각 획득     click     선택/버튼
   splash    물에 던지는 소리(강가 돌·동전)

■ 앰비언스 (장소 분위기 · 루프)
   warfield  전장 아비규환     campfire  모닥불 타닥타닥
   wagon     보급마차(바퀴·말발굽)  river 강가 물소리

■ 배경음악 (희로애락 · 고조 · 클라이맥스로 나눔, 모두 루프)
   prologue    도서관 프롤로그 (고요·신비)
   bgm         전장 기본 테마 (쓸쓸·성찰)
   campfirebgm 야영지 (따뜻·정겨움)
   tension     전투 직전 (불안·고조)
   battle      전투 (질주·클라이맥스)
   sorrow      죽음·상실 (애도)
   hope        회복·엔딩 (따뜻한 희망)

실행:  python gen_audio.py
"""
import os
import wave
import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "assets")
os.makedirs(OUT_DIR, exist_ok=True)
rng = np.random.default_rng(1863)

# 음이름 → 주파수
def N(name):
    names = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
             "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
    p = name[:-1]; octv = int(name[-1])
    midi = 12 * (octv + 1) + names[p]
    return 440.0 * 2 ** ((midi - 69) / 12)


# ── 기본 유틸 ────────────────────────────────────────
def t_arr(dur):
    return np.arange(int(SR * dur)) / SR


def fade(sig, fin=0.01, fout=0.05):
    n = len(sig); ni, no = int(SR * fin), int(SR * fout)
    if ni > 0:
        sig[:ni] *= np.linspace(0, 1, ni)
    if no > 0:
        sig[-no:] *= np.linspace(1, 0, no)
    return sig


def norm(sig, peak=0.9):
    m = np.max(np.abs(sig)) or 1.0
    return sig / m * peak


def lowpass(sig, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    L = int(np.log(1e-4) / np.log(a)) + 1 if 0 < a < 1 else 1
    L = max(2, min(L, len(sig)))
    kernel = (1 - a) * (a ** np.arange(L))
    return np.convolve(sig, kernel, mode="full")[:len(sig)]


def bandpass(sig, lo, hi):
    """차분형 대역통과(간이). lo~hi 대역만 남긴다."""
    return lowpass(sig, hi) - lowpass(sig, lo)


# 모음 'ㅏ' 포먼트 (비명·함성 등 사람 목소리 근사)
AH_FORMANTS = [(720, 130, 1.0), (1150, 140, 0.75), (2600, 190, 0.4), (3600, 220, 0.2)]


def scream_voice(f0, dur, rough=0.5, formants=AH_FORMANTS):
    """사람의 비명 — '노이즈 지배' 방식.
    맑은 유성음(하모닉 톤)이 지배하면 '삐~/삐용' 비프처럼 들리므로,
    모음 포먼트로 성형한 '거친 쉰 목소리 노이즈'가 소리의 대부분을 차지하고,
    피치(유성음)는 아주 약하게만 섞어 '사람이 지르는 아우성'으로만 들리게 한다."""
    n = int(SR * dur); t = np.arange(n) / SR
    # 1) 지배 성분 : 모음 'ㅏ' 포먼트로 성형한 광대역 난류 노이즈(쉰 목소리)
    base = rng.standard_normal(n)
    hoarse = np.zeros(n)
    for fc, bw, g in formants:
        hoarse += g * bandpass(base, max(fc - bw * 2.2, 90), fc + bw * 2.2)
    # 2) 아주 약한 유성음(피치) : 사람 목소리 기미만. 톤이 튀지 않게 낮게.
    jit = lowpass(rng.standard_normal(n), 11); jit /= (np.max(np.abs(jit)) or 1.0)
    f = f0 * (1 + 0.05 * jit)
    ph = 2 * np.pi * np.cumsum(f) / SR
    voiced = np.zeros(n)
    for k in range(1, 8):
        fk = f * k
        amp = np.zeros(n)
        for fc, bw, g in formants:
            amp += g * np.exp(-0.5 * ((fk - fc) / bw) ** 2)
        voiced += (0.2 + amp) * np.sin(ph * k) / k
    # 3) 거친 진폭변조(그르렁/절규의 요동) — 불규칙 + 저역 AM
    gr = lowpass(rng.standard_normal(n), 45); gr /= (np.max(np.abs(gr)) or 1.0)
    am = 1 + rough * (0.5 * np.sin(2 * np.pi * rng.uniform(55, 90) * t) + 0.45 * gr)
    sig = (hoarse * 0.9 + voiced * 0.28) * am              # 노이즈가 지배 → 톤 안 튐
    env = adsr(n, 0.02, 0.13, 0.85, 0.42)
    return np.tanh(sig * env * 1.2)


def voice(f0_start, f0_end, dur, formants=AH_FORMANTS, vib=0.02, vibf=6.0,
          kmax=34, breath=0.06):
    """포먼트 합성 사람 목소리 근사. 피치 글라이드 + 비브라토 + 숨소리."""
    n = int(SR * dur); t = np.arange(n) / SR
    contour = np.linspace(f0_start, f0_end, n) * (1 + 0.14 * np.sin(np.linspace(0, np.pi, n)))
    f0 = contour * (1 + vib * np.sin(2 * np.pi * vibf * t))
    phase = 2 * np.pi * np.cumsum(f0) / SR
    sig = np.zeros(n)
    for k in range(1, kmax + 1):
        fk = f0 * k
        amp = np.zeros(n)
        for fc, bw, g in formants:
            amp += g * np.exp(-0.5 * ((fk - fc) / bw) ** 2)
        sig += (amp / k ** 0.5) * np.sin(phase * k)
    sig += bandpass(rng.standard_normal(n), 1000, 4000) * breath
    return sig * adsr(n, 0.05, 0.1, 0.8, 0.3)


def adsr(n, a, d, s, rel):
    env = np.full(n, float(s))
    ai, di, ri = int(SR * a), int(SR * d), int(SR * rel)
    ai = min(ai, n)
    if ai > 0:
        env[:ai] = np.linspace(0, 1, ai)
    if di > 0 and ai + di <= n:
        env[ai:ai + di] = np.linspace(1, s, di)
    if ri > 0 and ri < n:
        env[-ri:] *= np.linspace(1, 0, ri)
    return env


def tone(freq, dur, partials=((1, 1.0),), a=0.01, d=0.08, s=0.75, rel=0.15,
         vib=0.0, vibf=5.0):
    n = int(SR * dur); t = np.arange(n) / SR
    fmod = freq * (1.0 + vib * np.sin(2 * np.pi * vibf * t)) if vib else np.full(n, freq)
    phase = 2 * np.pi * np.cumsum(fmod) / SR
    sig = np.zeros(n)
    for mult, amp in partials:
        sig += amp * np.sin(phase * mult)
    return sig * adsr(n, a, d, s, rel)


STRINGS = [(1, 1.0), (2, 0.5), (3, 0.28), (4, 0.16), (5, 0.09)]
SOFT = [(1, 1.0), (2, 0.28), (3, 0.1)]
BRASS = [(1, 1.0), (2, 0.7), (3, 0.5), (4, 0.34), (5, 0.22), (6, 0.12)]
BELL = [(1, 1.0), (2.76, 0.4), (5.4, 0.18)]


def pluck(freq, dur, bright=0.5):
    n = int(SR * dur); t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * freq * t)
           + bright * 0.5 * np.sin(2 * np.pi * 2 * freq * t)
           + bright * 0.28 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.exp(-t * (3.4 / dur))
    ai = int(SR * 0.004)
    env[:ai] *= np.linspace(0, 1, ai)
    return sig * env


def timp(dur=0.4, f0=130, f1=62, amp=1.0):
    n = int(SR * dur); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 12)
    phase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(phase) * np.exp(-t * 4.2) * amp


def snare(dur=0.18, amp=1.0):
    n = int(SR * dur)
    nz = rng.standard_normal(n) * np.exp(-np.linspace(0, 17, n))
    body = np.sin(2 * np.pi * 190 * np.arange(n) / SR) * np.exp(-np.linspace(0, 22, n)) * 0.4
    return (lowpass(nz, 5200) * 0.8 + body) * amp


def reverb(x, amount=0.25):
    out = x.copy()
    for dl, g in [(0.023, 0.5), (0.041, 0.4), (0.067, 0.3), (0.093, 0.22), (0.131, 0.16)]:
        d = int(dl * SR)
        if d < len(x):
            tail = np.zeros(len(x)); tail[d:] = x[:-d] * g
            out += tail * amount
    return out


def canvas(dur):
    return np.zeros(int(SR * dur))


def place(buf, sig, at, gain=1.0):
    s = int(at * SR)
    if s >= len(buf):
        return
    e = min(len(buf), s + len(sig))
    buf[s:e] += sig[:e - s] * gain


def loopify(sig, xf=0.6):
    x = int(SR * xf)
    if x * 2 >= len(sig):
        return sig
    head = sig[:x].copy(); tail = sig[-x:].copy()
    mix = head * np.linspace(0, 1, x) + tail * np.linspace(1, 0, x)
    out = sig[:-x].copy()
    out[:x] = mix
    return out


def to_stereo(mono, rev=0.28, width=0.011, peak=0.62):
    L = reverb(mono, rev)
    R = reverb(np.roll(mono, int(SR * width)), rev)
    m = max(np.max(np.abs(L)), np.max(np.abs(R))) or 1.0
    return L / m * peak, R / m * peak


def save(name, sig, stereo=None):
    if stereo is not None:
        data = np.stack([stereo[0], stereo[1]], axis=1); ch = 2
    else:
        data = sig.reshape(-1, 1); ch = 1
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(os.path.join(OUT_DIR, name + ".wav"), "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"  [ok] {name}.wav  ({len(data)/SR:.2f}s, {ch}ch)")


def pad(freqs, dur, gain=1.0, parts=SOFT, a=0.6, rel=0.7, vib=0.007, vibf=4.2):
    sig = canvas(dur)
    per = gain / max(1, len(freqs))
    for f in freqs:
        for dt in (0.996, 1.0, 1.004):
            place(sig, tone(f * dt, dur, partials=parts, a=a, d=0.4, s=0.85,
                            rel=rel, vib=vib, vibf=vibf), 0.0, per / 3)
    return sig


# ════════════════════════════════════════════════════
#  효과음
# ════════════════════════════════════════════════════
def make_page():
    out = canvas(0.85)
    for start, dur, amp in [(0.0, 0.20, 1.0), (0.30, 0.24, 0.75)]:
        n = int(SR * dur)
        noise = lowpass(rng.standard_normal(n), 2800)
        env = np.exp(-np.linspace(0, 6, n)) * np.sin(np.linspace(0, np.pi, n))
        place(out, noise * env * amp, start)
    return norm(fade(out), 0.55)


def make_wind():
    dur = 7.0; n = int(SR * dur); t = t_arr(dur)
    noise = rng.standard_normal(n)
    base = lowpass(noise, 650); gust = lowpass(noise, 200)
    amp = 0.5 + 0.32 * np.sin(2 * np.pi * 0.11 * t) + 0.16 * np.sin(2 * np.pi * 0.33 * t)
    sig = (base * 0.7 + gust * 0.6) * amp
    return norm(loopify(sig, 0.6), 0.5)


def make_bugle():
    """나팔 : 야전 집합 나팔 (브라스 하모닉스 콜)."""
    def call(freq, dur):
        return tone(freq, dur, partials=BRASS, a=0.015, d=0.05, s=0.8,
                    rel=0.08, vib=0.006, vibf=5.5)
    out = canvas(2.1)
    G4, C5, E5, G5 = N("G4"), N("C5"), N("E5"), N("G5")
    seq = [(0.00, G4, 0.20), (0.20, C5, 0.20), (0.40, E5, 0.42),
           (0.90, C5, 0.18), (1.08, E5, 0.18), (1.28, G5, 0.62)]
    for at, f, d in seq:
        place(out, call(f, d), at, 0.9)
        # 나팔 특유의 숨소리 어택
        na = int(SR * 0.02)
        place(out, lowpass(rng.standard_normal(na), 3000) * np.exp(-np.linspace(0, 10, na)) * 0.15, at)
    out = reverb(out, 0.3)
    return norm(fade(out, 0.005, 0.25), 0.72)


def make_shifting():
    dur = 2.0; t = t_arr(dur); sig = np.zeros_like(t)
    base = N("A3")
    for i, mult in enumerate([1, 1.5, 2, 3, 4, 5, 6]):
        f = base * mult * (1 + 0.22 * t / dur)
        env = np.exp(-np.linspace(0, 2.5 + i, len(t)))
        sig += np.sin(2 * np.pi * f * t) * env / (i + 1)
    swell = np.sin(np.linspace(0, np.pi, len(t))) * (1 + 0.05 * np.sin(2 * np.pi * 7 * t))
    return norm(fade(reverb(sig * swell, 0.35), 0.02, 0.4), 0.62)


def make_heartbeat():
    dur = 1.7; out = canvas(dur)
    def thump(start, freq, amp, length=0.19):
        n = int(SR * length); tt = t_arr(length)
        place(out, np.sin(2 * np.pi * freq * tt) * np.exp(-np.linspace(0, 9, n)) * amp, start)
    for beat in (0.0, 0.9):
        thump(beat, 55, 1.0); thump(beat + 0.17, 44, 0.65)
    return norm(fade(out), 0.7)


def make_gun():
    dur = 0.5; n = int(SR * dur); tt = t_arr(dur)
    crack = rng.standard_normal(n) * np.exp(-np.linspace(0, 42, n))
    body = lowpass(rng.standard_normal(n), 1100) * np.exp(-np.linspace(0, 17, n))
    punch = np.sin(2 * np.pi * 85 * tt) * np.exp(-np.linspace(0, 28, n)) * 0.6
    tail = lowpass(rng.standard_normal(n), 800) * np.exp(-np.linspace(0, 7, n)) * 0.25  # 먼 메아리
    sig = crack + body * 0.7 + punch + tail
    return norm(fade(sig, 0.0004, 0.06), 0.97)


def make_volley():
    """일제 사격(총성) : 여러 소총이 연달아 터지는 사격음. 전부 노이즈 파열 → '핑옹/피용' 없음."""
    dur = 1.9; out = canvas(dur)
    k = 0.02
    while k < dur - 0.28:
        L = int(rng.uniform(0.16, 0.32) * SR); tt = np.arange(L) / SR
        far = rng.uniform(0.3, 1.0)                          # 원근감(가까울수록 크고 밝게)
        crack = rng.standard_normal(L) * np.exp(-np.linspace(0, rng.uniform(30, 48), L))
        body = lowpass(rng.standard_normal(L), rng.uniform(900, 1300)) * np.exp(-np.linspace(0, 16, L))
        punch = np.sin(2 * np.pi * rng.uniform(70, 100) * tt) * np.exp(-np.linspace(0, 26, L)) * 0.5
        shot = lowpass(crack + body * 0.7 + punch, 1000 + 3800 * far)
        place(out, shot, k, 0.32 + 0.55 * far)
        k += rng.uniform(0.05, 0.2)                          # 불규칙 연사 간격
    return norm(fade(reverb(out, 0.2), 0.001, 0.16), 0.98)


def make_bomb():
    dur = 2.0; n = int(SR * dur); tt = t_arr(dur)
    rumble = np.sin(2 * np.pi * (40 - 20 * tt / dur) * tt) * np.exp(-np.linspace(0, 4.5, n))
    boom = lowpass(rng.standard_normal(n), 420) * np.exp(-np.linspace(0, 3.5, n))
    crack = rng.standard_normal(n) * np.exp(-np.linspace(0, 55, n)) * 0.5
    sig = rumble + boom * 0.9 + crack
    return norm(fade(sig, 0.0004, 0.35), 0.9)


def make_foot():
    dur = 2.2; out = canvas(dur); step = 0.0
    while step < dur - 0.2:
        length = 0.14; n = int(SR * length); tt = t_arr(length)
        thud = np.sin(2 * np.pi * 68 * tt) * np.exp(-np.linspace(0, 15, n))
        dirt = lowpass(rng.standard_normal(n), 1700) * np.exp(-np.linspace(0, 20, n)) * 0.4
        place(out, (thud + dirt) * rng.uniform(0.7, 1.0), step)
        step += rng.uniform(0.27, 0.33)
    return norm(fade(out, 0.002, 0.12), 0.62)


def make_item():
    out = canvas(1.0)
    for i, note in enumerate(["C5", "E5", "G5", "C6"]):
        place(out, tone(N(note), 0.9 - i * 0.09, partials=BELL, a=0.004, d=0.2,
                        s=0.4, rel=0.4), i * 0.085, 0.7)
    return norm(fade(reverb(out, 0.25), 0.002, 0.25), 0.55)


def make_click():
    dur = 0.08; tt = t_arr(dur); n = len(tt)
    tone_ = np.sin(2 * np.pi * 760 * tt) * np.exp(-np.linspace(0, 24, n))
    tick = rng.standard_normal(n) * np.exp(-np.linspace(0, 85, n)) * 0.3
    return norm(fade(tone_ + tick, 0.001, 0.02), 0.4)


def make_scream():
    """비명 : 전장에서 겹쳐 터지는 절규 (사람 목소리로, 크고 전면에 부각)."""
    out = canvas(2.0)
    #        시작   피치   길이  음량
    voices = [(0.00, 860, 0.7, 1.0), (0.26, 620, 0.6, 0.9),
              (0.58, 960, 0.55, 0.78), (0.92, 700, 0.7, 0.9),
              (1.28, 800, 0.55, 0.72), (1.56, 580, 0.6, 0.66)]
    for at, f, ln, g in voices:
        place(out, scream_voice(f, ln, rough=rng.uniform(0.42, 0.62)), at, g)
    return norm(fade(reverb(out, 0.18), 0.004, 0.26), 0.97)   # 크게


def make_shout():
    """함성 : 돌격하는 병사들의 포효 (거친 군중 + 저역 로어, 크레셴도)."""
    out = canvas(2.2); n = int(SR * 2.2)
    for _ in range(9):
        at = rng.uniform(0.0, 0.5); dur = rng.uniform(1.2, 1.8); f = rng.uniform(150, 300)
        place(out, scream_voice(f, dur, rough=rng.uniform(0.4, 0.65)), at, 0.3)
    roar = bandpass(rng.standard_normal(n), 200, 1300) * (0.3 + 0.3 * np.linspace(0, 1, n))
    out[:n] += roar * 0.22
    swell = np.clip(np.linspace(0.2, 1.25, len(out)), 0, 1)
    return norm(fade(reverb(out * swell, 0.34), 0.05, 0.38), 0.62)


def make_rustle():
    """부스럭 : 수풀·나뭇잎을 헤치는 소리 (거친 알갱이 노이즈)."""
    out = canvas(1.0); k = 0.0
    while k < 0.95:
        L = int(rng.uniform(0.01, 0.04) * SR)
        grain = bandpass(rng.standard_normal(L), 700, 4500)
        grain *= np.exp(-np.linspace(0, rng.uniform(6, 14), L))
        place(out, grain, k, rng.uniform(0.4, 1.0))
        k += rng.uniform(0.02, 0.08)
    return norm(fade(out, 0.005, 0.1), 0.5)


def make_drum():
    """북소리 : 멀리서 다가오는 전쟁 북 (행진 리듬, 크레셴도)."""
    out = canvas(2.7)
    def hit(at, amp):
        L = int(SR * 0.3); tt = t_arr(0.3)
        body = np.sin(2 * np.pi * 92 * tt) * np.exp(-np.linspace(0, 9, L))
        attack = lowpass(rng.standard_normal(L), 2000) * np.exp(-np.linspace(0, 30, L)) * 0.3
        place(out, body + attack, at, amp)
    for at in [0.0, 0.5, 1.0, 1.25, 1.5, 2.0, 2.25, 2.5]:
        hit(at, 0.45 + 0.55 * (at / 2.7))
    out = lowpass(out, 1600)                        # 멀리서 들리도록
    return norm(fade(reverb(out, 0.25), 0.005, 0.2), 0.55)


def make_impact():
    """타격(쿵) : 개머리판에 맞는 둔탁한 충격."""
    dur = 0.4; n = int(SR * dur); tt = t_arr(dur)
    thump = np.sin(2 * np.pi * 72 * tt) * np.exp(-np.linspace(0, 20, n))
    crack = lowpass(rng.standard_normal(n), 2400) * np.exp(-np.linspace(0, 46, n)) * 0.7
    tick = rng.standard_normal(n) * np.exp(-np.linspace(0, 120, n)) * 0.3
    return norm(fade(thump + crack + tick, 0.0004, 0.06), 0.8)


def make_cough():
    """콜록 : 먼지·화약 속 기침 3회 (쉰 성대음 + 파열 노이즈)."""
    out = canvas(1.7)

    def one(at, f0, g):
        d = 0.26; n = int(SR * d)
        buzz = voice(f0, f0 * 0.65, d, vib=0.05, vibf=9, kmax=16, breath=0.18)
        burst = bandpass(rng.standard_normal(n), 280, 2600) * np.exp(-np.linspace(0, 24, n))
        env = np.exp(-np.linspace(0, 8, n))
        place(out, (buzz[:n] * 0.7 + burst * 0.8) * env, at, g)

    one(0.0, 155, 0.95); one(0.42, 138, 0.85); one(0.92, 120, 0.62)
    out = lowpass(out, 3600)
    return norm(fade(reverb(out, 0.2), 0.003, 0.2), 0.6)


def make_cannon():
    """포성 : 멀리서 울리는 대포 (초저역 붐 + 공기 파열 + 긴 메아리)."""
    dur = 2.6; n = int(SR * dur); tt = t_arr(dur)
    boom = np.sin(2 * np.pi * (58 - 30 * tt / dur) * tt) * np.exp(-np.linspace(0, 3.2, n))
    sub = np.sin(2 * np.pi * (34 - 14 * tt / dur) * tt) * np.exp(-np.linspace(0, 2.4, n)) * 0.8
    crack = rng.standard_normal(n) * np.exp(-np.linspace(0, 60, n)) * 0.4
    body = lowpass(rng.standard_normal(n), 360) * np.exp(-np.linspace(0, 2.8, n))
    echo = np.zeros(n); d1 = int(0.52 * SR)
    echo[d1:] = boom[:-d1] * 0.32
    sig = boom + sub + crack + body * 0.7 + echo
    return norm(fade(sig, 0.0004, 0.5), 0.92)


def make_splash():
    """물에 던지는 소리(퐁당) : 하강 피치 '플렁크' + 물튐 파열 + 잔물결 방울."""
    dur = 1.2; out = canvas(dur)
    # 1) 돌/동전이 물에 박히는 하강 피치 '플렁크'
    d1 = 0.2; n1 = int(SR * d1); t1 = t_arr(d1)
    f = 120 + 820 * np.exp(-t1 * 16)                # ~940Hz → ~120Hz 급강하
    plunk = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-np.linspace(0, 8, n1))
    place(out, plunk, 0.0, 0.9)
    # 2) 물이 튀는 파열(짧은 대역 노이즈)
    nb = int(SR * 0.28)
    burst = bandpass(rng.standard_normal(nb), 500, 5200) * np.exp(-np.linspace(0, 15, nb))
    place(out, burst, 0.0, 0.45)
    # 3) 잔물결이 번지는 방울들
    for at in [0.18, 0.32, 0.5, 0.72]:
        d = 0.1; nn = int(SR * d); tt = t_arr(d)
        f2 = rng.uniform(300, 620) * (1 + 1.6 * tt / d)   # 위로 튀는 방울음
        place(out, np.sin(2 * np.pi * f2 * tt) * np.exp(-np.linspace(0, 11, nn)),
              at, rng.uniform(0.12, 0.22))
    return norm(fade(reverb(out, 0.28), 0.001, 0.25), 0.62)


def make_fire():
    """모닥불 : 타닥타닥 장작 크래클 + 낮게 깔리는 불길 소리 (루프)."""
    dur = 9.0; n = int(SR * dur); t = t_arr(dur); out = canvas(dur)
    # 1) 불길의 낮은 웅웅거림(로어)
    roar = lowpass(rng.standard_normal(n), 480)
    amp = 0.42 + 0.2 * np.sin(2 * np.pi * 0.3 * t) + 0.1 * np.sin(2 * np.pi * 0.8 * t)
    out += roar * amp * 0.34
    # 2) 산발적인 장작 튀는 소리(크래클 팝)
    k = 0.0
    while k < dur - 0.05:
        L = int(rng.uniform(0.003, 0.02) * SR)
        pop = rng.standard_normal(L) * np.exp(-np.linspace(0, rng.uniform(8, 22), L))
        place(out, lowpass(pop, 4200), k, rng.uniform(0.2, 0.7))
        k += rng.uniform(0.03, 0.26)
    # 3) 이따금 크게 '탁' 하고 튀는 큰 불똥
    for at in rng.uniform(0.3, dur - 0.3, 6):
        L = int(0.05 * SR); tt = t_arr(0.05)
        snap = (np.sin(2 * np.pi * rng.uniform(600, 1100) * tt)
                + rng.standard_normal(L) * 0.6) * np.exp(-np.linspace(0, 26, L))
        place(out, snap, at, rng.uniform(0.4, 0.7))
    return None, to_stereo(loopify(out, 1.0), rev=0.2, peak=0.5)


def make_wagon():
    """보급마차 : 흙길 바퀴 구르는 소리 + 삐걱대는 나무 + 말발굽 (루프)."""
    dur = 9.0; n = int(SR * dur); t = t_arr(dur); out = canvas(dur)
    # 1) 바퀴가 흙길을 구르는 저역 럼블
    rumble = lowpass(rng.standard_normal(n), 300) * (0.4 + 0.15 * np.sin(2 * np.pi * 0.5 * t))
    out += rumble * 0.32
    # 2) 주기적인 나무 바퀴 삐걱(피치 흔들리는 스퀴크)
    ck = rng.uniform(0.2, 0.6)
    while ck < dur - 0.7:
        d = rng.uniform(0.4, 0.75); nn = int(SR * d); tt = t_arr(d)
        base = rng.uniform(300, 520)
        f = base * (1 + 0.28 * np.sin(2 * np.pi * rng.uniform(2.5, 4.0) * tt))
        creak = np.sin(2 * np.pi * f * tt) * np.exp(-np.linspace(0, 3.0, nn))
        place(out, bandpass(creak, 200, 1300), ck, rng.uniform(0.5, 0.85))
        ck += rng.uniform(0.9, 1.7)
    # 3) 느긋한 말발굽 클롭
    hk = 0.0
    while hk < dur - 0.2:
        L = int(0.09 * SR); tt = t_arr(0.09)
        clop = (np.sin(2 * np.pi * 90 * tt) * np.exp(-np.linspace(0, 30, L))
                + lowpass(rng.standard_normal(L), 1600) * np.exp(-np.linspace(0, 42, L)) * 0.4)
        place(out, clop, hk, rng.uniform(0.28, 0.5))
        hk += rng.uniform(0.36, 0.52)
    return None, to_stereo(loopify(out, 1.0), rev=0.26, peak=0.5)


def make_river():
    """강가 : 흐르는 물소리 + 낮은 물결 + 이따금 보글대는 물방울 (루프)."""
    dur = 9.0; n = int(SR * dur); t = t_arr(dur); out = canvas(dur)
    # 1) 물이 흐르는 쉬익 소리(대역 노이즈, 느린 출렁임)
    water = bandpass(rng.standard_normal(n), 420, 6200)
    amp = 0.6 + 0.15 * np.sin(2 * np.pi * 0.2 * t) + 0.1 * np.sin(2 * np.pi * 0.53 * t)
    out += water * amp * 0.46
    # 2) 낮게 깔리는 물결
    out += lowpass(rng.standard_normal(n), 340) * 0.18
    # 3) 이따금 보글대는 물방울
    k = 0.0
    while k < dur - 0.1:
        d = rng.uniform(0.04, 0.12); nn = int(SR * d); tt = t_arr(d)
        f = rng.uniform(400, 900) * (1 + 2.0 * tt / d)   # 위로 튀는 물방울
        place(out, np.sin(2 * np.pi * f * tt) * np.exp(-np.linspace(0, 10, nn)),
              k, rng.uniform(0.08, 0.16))
        k += rng.uniform(0.22, 0.6)
    return None, to_stereo(loopify(out, 1.4), rev=0.3, peak=0.5)


def make_warfield():
    """아비규환 : 전장 앰비언스 루프 — 낮은 굉음 + 산발 총성 + 먼 포성 + 아득한 비명·함성."""
    dur = 12.0; n = int(SR * dur); t = t_arr(dur); out = canvas(dur)
    # 1) 지속되는 저역 전장 굉음(드론)
    base = lowpass(rng.standard_normal(n), 220)
    amp = 0.5 + 0.3 * np.sin(2 * np.pi * 0.13 * t) + 0.15 * np.sin(2 * np.pi * 0.37 * t)
    out += base * amp * 0.5
    # 2) 산발적 총성 (멀리)
    k = 0.0
    while k < dur - 0.3:
        L = int(0.28 * SR)
        crack = rng.standard_normal(L) * np.exp(-np.linspace(0, 40, L))
        place(out, lowpass(crack, 1400) * 0.6, k, rng.uniform(0.12, 0.34))
        k += rng.uniform(0.12, 0.5)
    # 3) 이따금 먼 포성
    for at in [0.8, 3.4, 6.1, 9.3, 11.2]:
        d = 1.6; nn = int(SR * d); ttt = t_arr(d)
        boom = np.sin(2 * np.pi * (50 - 24 * ttt / d) * ttt) * np.exp(-np.linspace(0, 3.5, nn))
        rum = lowpass(rng.standard_normal(nn), 380) * np.exp(-np.linspace(0, 3.0, nn))
        place(out, boom + rum * 0.7, at, rng.uniform(0.3, 0.5))
    # 4) 아득한 군중 로어(톤 없는 노이즈 기반) — 웅성거림/아우성 (피치 스윕 없음)
    roar = bandpass(rng.standard_normal(n), 280, 1800)
    roar_amp = 0.26 + 0.16 * np.sin(2 * np.pi * 0.21 * t) + 0.1 * np.sin(2 * np.pi * 0.5 * t)
    out += roar * roar_amp * 0.36
    out = lowpass(out, 5200)                       # 전체적으로 '멀리서' 필터
    return None, to_stereo(loopify(out, 1.5), rev=0.4, width=0.02, peak=0.5)


# ════════════════════════════════════════════════════
#  배경음악 (감정선)
# ════════════════════════════════════════════════════
def make_prologue():
    """고요한 도서관 · 신비. 느린 마이너9 패드 + 드문 벨."""
    dur = 15.0; out = canvas(dur)
    chords = [["A3", "C4", "E4", "B4"], ["F3", "A3", "C4", "E4"]]
    for i, ch in enumerate(chords):
        place(out, pad([N(x) for x in ch], dur / 2, gain=0.9, a=1.4, rel=1.6), i * dur / 2)
    place(out, tone(N("A2"), dur, partials=[(1, 1.0), (2, 0.2)], a=2.0, s=0.7, rel=2.0), 0, 0.5)
    for at, note in [(2.5, "E5"), (6.0, "A5"), (9.5, "C5"), (12.5, "E5")]:
        place(out, tone(N(note), 2.2, partials=BELL, a=0.01, d=0.6, s=0.3, rel=1.0), at, 0.28)
    return None, to_stereo(loopify(out, 1.2), rev=0.4, peak=0.6)


def make_bgm():
    """전장 기본 · 무겁고 쓸쓸한 성찰. 깊은 저음 진행 + 따뜻한 첼로 선율(비브라토 최소)."""
    bar = 4.0; dur = bar * 4; out = canvas(dur)
    WARM = [(1, 1.0), (2, 0.4), (3, 0.14)]                 # 얇은 고배음 없이 따뜻하게
    prog = [["A2", "E3", "A3"], ["F2", "C3", "F3"], ["C3", "G3", "C4"], ["G2", "D3", "G3"]]
    for i, ch in enumerate(prog):
        place(out, pad([N(x) for x in ch], bar, gain=0.82, parts=WARM, a=1.1, rel=1.3, vib=0.0), i * bar)
    # 깊은 드론(콘트라베이스)
    place(out, tone(N("A1"), dur, partials=[(1, 1.0), (2, 0.28)], a=1.6, s=0.72, rel=2.0), 0, 0.5)
    # 낮고 느린 첼로 선율 — 비브라토 최소, 매끄러운 어택
    mel = [("A3", 0.4, 2.6), ("C4", 3.4, 2.0), ("E3", 6.2, 2.8),
           ("D3", 9.4, 2.2), ("A3", 12.2, 3.2)]
    for note, at, ln in mel:
        place(out, tone(N(note), ln, partials=WARM, a=0.25, d=0.4, s=0.7,
                        rel=0.9, vib=0.005, vibf=3.8), at, 0.26)
    return None, to_stereo(loopify(out, 1.0), rev=0.34, peak=0.6)


def make_campfire():
    """야영지 · 따뜻하고 정겨움. 장조 패드 + 하프 아르페지오 + 모닥불 크래클."""
    bar = 4.0; dur = bar * 4; out = canvas(dur)
    prog = [["C3", "E3", "G3"], ["G2", "B2", "D3"], ["A2", "C3", "E3"], ["F2", "A2", "C3"]]
    for i, ch in enumerate(prog):
        place(out, pad([N(x) for x in ch], bar, gain=0.8, a=0.6, rel=0.7, vib=0.005), i * bar)
    arp_sets = [["C4", "E4", "G4", "E4"], ["D4", "G4", "B4", "G4"],
                ["E4", "A4", "C5", "A4"], ["C4", "F4", "A4", "F4"]]
    for i, arp in enumerate(arp_sets):
        for j, note in enumerate(arp):
            place(out, pluck(N(note), 0.9, bright=0.6), i * bar + j * (bar / 4), 0.16)
    n = len(out); crackle = np.zeros(n); k = 0
    while k < n:
        k += int(rng.uniform(0.05, 0.3) * SR)
        if k >= n:
            break
        L = int(rng.uniform(0.004, 0.018) * SR)
        place(crackle, rng.standard_normal(L) * np.exp(-np.linspace(0, 10, L)), k / SR, rng.uniform(0.15, 0.4))
    out += lowpass(crackle, 3500) * 0.5
    return None, to_stereo(loopify(out, 0.8), rev=0.22, peak=0.6)


def make_tension():
    """전투 직전 · 불안과 고조. 저음 드론 + 맥박 팀파니 + 상승 불협 스웰."""
    dur = 12.0; out = canvas(dur)
    place(out, tone(N("E2"), dur, partials=[(1, 1.0), (2, 0.3), (3, 0.12)], a=1.5, s=0.7, rel=1.5), 0, 0.55)
    beat = 0.6; k = 0
    while k * beat < dur - 0.5:                    # 점점 강해지는 심장 팀파니
        g = 0.3 + 0.6 * (k * beat / dur)
        place(out, timp(0.5, f0=110, f1=55), k * beat, g * 0.5)
        k += 1
    swell = np.sin(np.linspace(0, np.pi, int(SR * dur))) ** 2  # 후반 상승 불협
    diss = (tone(N("E4"), dur, partials=STRINGS, a=2.0, s=0.8, rel=2.0)
            + tone(N("F4"), dur, partials=STRINGS, a=2.0, s=0.8, rel=2.0) * 0.8)
    out += diss * swell * 0.22
    return None, to_stereo(loopify(out, 0.6), rev=0.3, peak=0.6)


def make_battle():
    """전투 · 질주하는 클라이맥스. 8분 오스티나토 + 스네어 + 브라스 스탭 + 팀파니."""
    bpm = 132; beat = 60 / bpm; bar = beat * 4
    bars = 8; dur = bar * bars; out = canvas(dur)
    prog = [["A3", "C4", "E4"], ["A3", "C4", "E4"], ["F3", "A3", "C4"], ["F3", "A3", "C4"],
            ["G3", "B3", "D4"], ["G3", "B3", "D4"], ["A3", "C4", "E4"], ["E3", "G3", "B3"]]
    roots = ["A2", "A2", "F2", "F2", "G2", "G2", "A2", "E2"]
    for b in range(bars):
        t0 = b * bar
        intensity = 0.5 + 0.5 * (b / bars)                 # 점층적 고조
        for e in range(8):                                  # 8분음 저현 오스티나토
            place(out, pluck(N(roots[b]), beat * 0.9, bright=0.35),
                  t0 + e * (beat / 2), 0.28 * intensity)
        place(out, timp(0.45, 120, 58), t0, 0.6)            # 1박 팀파니
        place(out, timp(0.4, 110, 55), t0 + beat * 2, 0.5)  # 3박
        for e in (1, 3):                                    # 스네어 백비트
            place(out, snare(0.16, amp=0.5 * intensity), t0 + e * beat)
        for note in prog[b]:                                # 브라스 스탭
            place(out, tone(N(note) * 2, beat * 1.8, partials=BRASS, a=0.02, d=0.15,
                            s=0.5, rel=0.2), t0, 0.16 * intensity)
        if b >= 4:                                          # 후반 영웅적 상위 선율
            mel = {4: "E5", 5: "D5", 6: "E5", 7: "G5"}[b]
            place(out, tone(N(mel), bar * 0.9, partials=BRASS, a=0.05, d=0.3, s=0.6,
                            rel=0.3, vib=0.012, vibf=5.5), t0, 0.2)
    return None, to_stereo(loopify(out, 0.3), rev=0.22, peak=0.66)


def make_sorrow():
    """죽음·상실 · 애도. 느린 첼로 하강 선율 + 깊은 마이너 패드."""
    bar = 4.5; dur = bar * 4; out = canvas(dur)
    prog = [["A2", "E3", "A3", "C4"], ["F2", "C3", "F3", "A3"],
            ["D3", "A3", "D4", "F4"], ["E3", "B3", "E4", "G4"]]
    for i, ch in enumerate(prog):
        place(out, pad([N(x) for x in ch], bar, gain=0.85, a=1.2, rel=1.4, vib=0.01), i * bar)
    mel = [("E4", 0.5, 2.2), ("D4", 3.0, 1.6), ("C4", 5.0, 2.5), ("B3", 8.0, 1.8),
           ("A3", 10.2, 2.6), ("C4", 13.5, 1.4), ("A3", 15.0, 2.5)]
    for note, at, ln in mel:
        place(out, tone(N(note), ln, partials=STRINGS, a=0.15, d=0.4, s=0.75,
                        rel=0.6, vib=0.014, vibf=4.5), at, 0.24)
    return None, to_stereo(loopify(out, 1.2), rev=0.42, peak=0.58)


def make_hope():
    """회복·엔딩 · 따뜻한 희망. 장조 진행 + 상승 해결 선율 + 부드러운 벨."""
    bar = 4.0; dur = bar * 4; out = canvas(dur)
    prog = [["C3", "E3", "G3"], ["G2", "B2", "D3"], ["A2", "C3", "E3"], ["F2", "A2", "C3"]]
    for i, ch in enumerate(prog):
        place(out, pad([N(x) for x in ch], bar, gain=0.85, a=0.7, rel=0.9, vib=0.006), i * bar)
    mel = [("G4", 0.5, 1.6), ("A4", 2.2, 1.6), ("C5", 4.2, 2.0), ("B4", 6.5, 1.4),
           ("C5", 8.2, 1.6), ("D5", 10.0, 1.6), ("E5", 12.0, 2.4), ("C5", 14.5, 1.6)]
    for note, at, ln in mel:
        place(out, tone(N(note), ln, partials=STRINGS, a=0.1, d=0.3, s=0.72,
                        rel=0.5, vib=0.009, vibf=5), at, 0.22)
    for at, note in [(0.0, "C4"), (8.0, "E4")]:
        place(out, tone(N(note), 3.0, partials=BELL, a=0.01, d=0.8, s=0.3, rel=1.2), at, 0.18)
    return None, to_stereo(loopify(out, 1.0), rev=0.32, peak=0.62)


# ── 실행 ─────────────────────────────────────────────
SFX = {
    "page": make_page, "wind": make_wind, "bugle": make_bugle, "shifting": make_shifting,
    "heartbeat": make_heartbeat, "gun": make_gun, "volley": make_volley, "bomb": make_bomb,
    "foot": make_foot, "item": make_item, "click": make_click,
    "scream": make_scream, "shout": make_shout, "rustle": make_rustle,
    "drum": make_drum, "impact": make_impact,
    "cough": make_cough, "cannon": make_cannon,
    "splash": make_splash,                 # 물에 던지는 소리(퐁당)
}
BGM = {
    "prologue": make_prologue, "bgm": make_bgm, "campfirebgm": make_campfire,
    "tension": make_tension, "battle": make_battle, "sorrow": make_sorrow, "hope": make_hope,
}
# 앰비언스(루프 · 스테레오) — 효과음 채널로 배경음악 위에 겹쳐 재생
AMB = {
    "warfield": make_warfield,
    "campfire": make_fire,    # 모닥불 타닥타닥
    "wagon":    make_wagon,   # 보급마차 삐걱·말발굽
    "river":    make_river,   # 강가 물소리
}


def main(only=None):
    print(f"오디오 생성 → {OUT_DIR}")
    if only is None or "sfx" in only:
        print("[효과음]")
        for name, fn in SFX.items():
            save(name, fn())
    if only is None or "bgm" in only:
        print("[배경음악 · 감정선 · 루프]")
        for name, fn in BGM.items():
            _, st = fn()
            save(name, None, stereo=st)
    if only is None or "amb" in only:
        print("[앰비언스 · 아비규환 루프]")
        for name, fn in AMB.items():
            _, st = fn()
            save(name, None, stereo=st)
    print("완료. game.py 실행 시 자동으로 사용됩니다.")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
