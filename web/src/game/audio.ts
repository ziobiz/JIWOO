/** 웹 오디오 — BGM 크로스페이드, 앰비언스 루프, 효과음 */

const BGM_FILES: Record<string, string> = {
  prologue: "prologue",
  start: "prologue",
  bgm: "bgm",
  campfirebgm: "campfirebgm",
  tension: "tension",
  battle: "battle",
  sorrow: "sorrow",
  hope: "hope",
};

const AMB_FILES: Record<string, string> = {
  warfield: "warfield",
  campfire: "campfire",
  wagon: "wagon",
  river: "river",
};

const BGM_BASE: Record<string, number> = {
  prologue: 0.38,
  start: 0.38,
  bgm: 0.4,
  campfirebgm: 0.42,
  tension: 0.4,
  battle: 0.45,
  sorrow: 0.38,
  hope: 0.42,
};

const SFX_BASE: Record<string, number> = {
  gun: 0.85,
  volley: 0.9,
  cannon: 0.8,
  bomb: 0.75,
  scream: 0.7,
  shout: 0.65,
  cough: 0.6,
  page: 0.5,
  wind: 0.45,
  shifting: 0.5,
  rustle: 0.45,
  splash: 0.55,
  bugle: 0.6,
  drum: 0.55,
  foot: 0.4,
  impact: 0.7,
  heartbeat: 0.5,
  click: 0.4,
  item: 0.55,
};

const AMB_BASE: Record<string, number> = {
  warfield: 0.62,
  campfire: 0.5,
  wagon: 0.45,
  river: 0.4,
};

const SFX_MASTER = 0.55;

function src(name: string) {
  return `/assets/${name}.wav`;
}

export class AudioManager {
  bgmVol = 0.8;
  sfxVol = 0.8;
  private unlocked = false;
  private currentBgm: string | null = null;
  private currentAmb: string | null = null;
  private bgmA: HTMLAudioElement | null = null;
  private bgmB: HTMLAudioElement | null = null;
  private bgmActive: "a" | "b" = "a";
  private ambEl: HTMLAudioElement | null = null;
  private fadeTimer: ReturnType<typeof setInterval> | null = null;

  /** 브라우저 자동재생 정책 — 첫 클릭 시 호출 */
  unlock() {
    if (this.unlocked) return;
    this.unlocked = true;
  }

  private makeBgm(file: string): HTMLAudioElement {
    const el = new Audio(src(file));
    el.loop = true;
    el.preload = "auto";
    return el;
  }

  playBgm(key: string) {
    if (!this.unlocked) return;
    const file = BGM_FILES[key];
    if (!file || this.currentBgm === key) return;
    this.currentBgm = key;
    const base = (BGM_BASE[key] ?? 0.4) * this.bgmVol;
    const next = this.makeBgm(file);
    next.volume = 0;
    const old = this.bgmActive === "a" ? this.bgmA : this.bgmB;
    this.bgmActive = this.bgmActive === "a" ? "b" : "a";
    if (this.bgmActive === "a") this.bgmA = next;
    else this.bgmB = next;
    next.play().catch(() => {});
    if (this.fadeTimer) clearInterval(this.fadeTimer);
    let step = 0;
    const steps = 20;
    this.fadeTimer = setInterval(() => {
      step++;
      const t = step / steps;
      next.volume = base * t;
      if (old) old.volume = base * (1 - t);
      if (step >= steps) {
        if (this.fadeTimer) clearInterval(this.fadeTimer);
        this.fadeTimer = null;
        old?.pause();
      }
    }, 40);
  }

  playAmb(key: string) {
    if (!this.unlocked) return;
    if (key === "stop") {
      this.stopAmb();
      return;
    }
    const file = AMB_FILES[key];
    if (!file || this.currentAmb === key) return;
    this.currentAmb = key;
    this.ambEl?.pause();
    const el = new Audio(src(file));
    el.loop = true;
    el.volume = (AMB_BASE[key] ?? 0.5) * SFX_MASTER * this.sfxVol;
    el.play().catch(() => {});
    this.ambEl = el;
  }

  stopAmb() {
    this.currentAmb = null;
    if (this.ambEl) {
      const el = this.ambEl;
      let v = el.volume;
      const fade = setInterval(() => {
        v -= 0.05;
        if (v <= 0) {
          el.pause();
          clearInterval(fade);
        } else el.volume = v;
      }, 50);
      this.ambEl = null;
    }
  }

  playSfx(key: string) {
    if (!this.unlocked) return;
    const vol = (SFX_BASE[key] ?? 0.55) * SFX_MASTER * this.sfxVol;
    const el = new Audio(src(key));
    el.volume = vol;
    el.play().catch(() => {});
  }

  setBgmVol(v: number) {
    this.bgmVol = v;
    const active = this.bgmActive === "a" ? this.bgmA : this.bgmB;
    if (active && this.currentBgm) {
      active.volume = (BGM_BASE[this.currentBgm] ?? 0.4) * v;
    }
  }

  setSfxVol(v: number) {
    this.sfxVol = v;
    if (this.ambEl && this.currentAmb) {
      this.ambEl.volume =
        (AMB_BASE[this.currentAmb] ?? 0.5) * SFX_MASTER * v;
    }
  }

  stopAll() {
    this.bgmA?.pause();
    this.bgmB?.pause();
    this.ambEl?.pause();
    this.currentBgm = null;
    this.currentAmb = null;
  }

  getCurrentBgm() {
    return this.currentBgm;
  }
  getCurrentAmb() {
    return this.currentAmb;
  }
}

let _audio: AudioManager | null = null;
export function getAudio(): AudioManager {
  if (!_audio) _audio = new AudioManager();
  return _audio;
}
