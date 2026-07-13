import {
  GAME,
  type Node,
  type ChoiceOption,
  type ExplorePlace,
  determineEnding,
  evalCond,
  resolveSpeakerPortrait,
} from "./gameData";
import type { Profile } from "./profile";

export interface GameState {
  stats: Record<string, number>;
  conflict: Record<string, number>;
  items: string[];
  bg: string | null;
  charKey: string | null;
}

export type Frame =
  | {
      type: "text";
      mode: "say" | "mono" | "narr" | "act";
      speaker: string | null;
      text: string;
      portrait: string | null;
    }
  | { type: "title"; lines: string[]; sub: string | null }
  | { type: "card"; cardKind: string; title: string; body: string[] }
  | { type: "result"; title: string }
  | { type: "item"; name: string; icon: string }
  | { type: "choice"; options: { label: string; index: number }[] }
  | {
      type: "explore";
      places: { name: string; index: number; visited: boolean }[];
    };

export interface BacklogEntry {
  speaker: string | null;
  text: string;
  mode: string;
}

interface ExploreState {
  places: ExplorePlace[];
  visited: boolean[];
}
interface StackFrame {
  nodes: Node[];
  i: number;
  exploreOwner?: ExploreState;
  exploreIndex?: number;
}

export interface EngineSnapshot {
  version: 1;
  state: GameState;
  stack: StackFrame[];
  pendingChoice: ChoiceOption[] | null;
  currentExplore: ExploreState | null;
  inEnding: boolean;
  endingCode: string | null;
  done: boolean;
  frame: Frame | null;
  currentBgm: string | null;
  currentAmb: string | null;
  label: string;
  profile: Profile;
  backlog: BacklogEntry[];
  savedAt: number;
}

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

export class Engine {
  state: GameState;
  frame: Frame | null = null;
  done = false;
  endingCode: string | null = null;
  backlog: BacklogEntry[] = [];
  label = "";
  currentBgm: string | null = null;
  currentAmb: string | null = null;

  private stack: StackFrame[] = [];
  private pendingChoice: ChoiceOption[] | null = null;
  private currentExplore: ExploreState | null = null;
  private inEnding = false;
  private checkpoint: EngineSnapshot | null = null;

  onBgm?: (key: string) => void;
  onAmb?: (key: string) => void;
  onSfx?: (key: string) => void;
  onBgChange?: (key: string | null) => void;

  constructor(snapshot?: EngineSnapshot) {
    if (snapshot) {
      this.state = snapshot.state;
      this.stack = snapshot.stack;
      this.pendingChoice = snapshot.pendingChoice;
      this.currentExplore = snapshot.currentExplore;
      this.inEnding = snapshot.inEnding;
      this.endingCode = snapshot.endingCode;
      this.done = snapshot.done;
      this.frame = snapshot.frame;
      this.currentBgm = snapshot.currentBgm;
      this.currentAmb = snapshot.currentAmb;
      this.label = snapshot.label;
      this.backlog = snapshot.backlog ?? [];
      this.checkpoint = snapshot;
      return;
    }
    this.state = {
      stats: { ...GAME.constants.initialStats },
      conflict: { 인간: 0, 군인: 0 },
      items: [],
      bg: null,
      charKey: null,
    };
    this.stack = [{ nodes: GAME.story, i: 0 }];
    this.captureCheckpoint();
    this.step();
  }

  private applyEffects(effects: Record<string, number>) {
    for (const [key, v] of Object.entries(effects)) {
      if (key === "인간" || key === "군인") {
        this.state.conflict[key] = (this.state.conflict[key] ?? 0) + v;
      } else {
        this.state.stats[key] = clamp((this.state.stats[key] ?? 0) + v, 0, 100);
      }
    }
  }

  private logBacklog(frame: Frame) {
    if (frame.type === "text") {
      this.backlog.push({
        speaker: frame.speaker,
        text: frame.text,
        mode: frame.mode,
      });
    }
  }

  private showExplore(ex: ExploreState) {
    this.currentExplore = ex;
    this.frame = {
      type: "explore",
      places: ex.places.map((p, idx) => ({
        name: p.name,
        index: idx,
        visited: ex.visited[idx],
      })),
    };
  }

  private step() {
    for (let guard = 0; guard < 100000; guard++) {
      const top = this.stack[this.stack.length - 1];
      if (!top) {
        this.frame = null;
        if (this.inEnding) this.done = true;
        return;
      }
      if (top.i >= top.nodes.length) {
        this.stack.pop();
        if (top.exploreOwner) {
          const ex = top.exploreOwner;
          ex.visited[top.exploreIndex!] = true;
          if (ex.visited.every(Boolean)) {
            this.currentExplore = null;
            continue;
          }
          this.showExplore(ex);
          return;
        }
        continue;
      }

      const node = top.nodes[top.i];
      top.i++;
      const kind = node[0] as string;

      switch (kind) {
        case "bg": {
          const bg = node[1] as string;
          this.state.bg = bg;
          this.onBgChange?.(bg);
          break;
        }
        case "char":
          this.state.charKey = (node[1] as string | null) ?? null;
          break;
        case "bgm":
          this.currentBgm = node[1] as string;
          this.onBgm?.(this.currentBgm);
          break;
        case "amb": {
          const amb = node[1] as string;
          this.currentAmb = amb === "stop" ? null : amb;
          this.onAmb?.(amb);
          break;
        }
        case "sfx":
          this.onSfx?.(node[1] as string);
          break;
        case "stat":
          this.applyEffects(node[1] as Record<string, number>);
          break;
        case "item": {
          const name = node[1] as string;
          this.state.items.push(name);
          this.onSfx?.("item");
          this.frame = {
            type: "item",
            name,
            icon: GAME.constants.fragmentIcon[name] ?? "",
          };
          return;
        }
        case "clear":
          this.state.charKey = null;
          break;
        case "flash":
          break;
        case "say": {
          const frame: Frame = {
            type: "text",
            mode: "say",
            speaker: node[1] as string,
            text: node[2] as string,
            portrait: resolveSpeakerPortrait(
              node[1] as string,
              node[2] as string,
            ),
          };
          this.frame = frame;
          this.logBacklog(frame);
          return;
        }
        case "mono": {
          const frame: Frame = {
            type: "text",
            mode: "mono",
            speaker: null,
            text: node[1] as string,
            portrait: null,
          };
          this.frame = frame;
          this.logBacklog(frame);
          return;
        }
        case "narr": {
          const frame: Frame = {
            type: "text",
            mode: "narr",
            speaker: null,
            text: node[1] as string,
            portrait: null,
          };
          this.frame = frame;
          this.logBacklog(frame);
          return;
        }
        case "act": {
          const frame: Frame = {
            type: "text",
            mode: "act",
            speaker: null,
            text: node[1] as string,
            portrait: null,
          };
          this.frame = frame;
          this.logBacklog(frame);
          return;
        }
        case "title": {
          const lines = node[1] as string[];
          const sub = (node[2] as string | null) ?? null;
          if (lines[0]?.startsWith("CHAPTER") || lines[0]?.includes("CHAPTER")) {
            this.label = lines.join(" ");
          }
          this.frame = { type: "title", lines, sub };
          return;
        }
        case "card":
          this.frame = {
            type: "card",
            cardKind: node[1] as string,
            title: node[2] as string,
            body: node[3] as string[],
          };
          return;
        case "result":
          this.frame = { type: "result", title: node[1] as string };
          return;
        case "choice": {
          const opts = node[1] as ChoiceOption[];
          this.pendingChoice = opts;
          this.frame = {
            type: "choice",
            options: opts.map((o, idx) => ({ label: o.label, index: idx })),
          };
          return;
        }
        case "explore": {
          const places = node[1] as ExplorePlace[];
          this.showExplore({ places, visited: places.map(() => false) });
          return;
        }
        case "cond": {
          const cond = node[1] as [string, string, number];
          const thenN = node[2] as Node[];
          const elseN = (node[3] as Node[]) ?? [];
          const branch = evalCond(
            cond,
            this.state.stats,
            this.state.conflict,
            this.state.items.length,
          )
            ? thenN
            : elseN;
          this.stack.push({ nodes: branch, i: 0 });
          break;
        }
        case "ending": {
          const code = determineEnding(
            this.state.stats,
            this.state.items.length,
          );
          this.endingCode = code;
          this.inEnding = true;
          this.stack.push({ nodes: GAME.endings[code] ?? [], i: 0 });
          break;
        }
        default:
          break;
      }
    }
  }

  advance() {
    if (!this.frame) return;
    if (
      this.frame.type === "text" ||
      this.frame.type === "title" ||
      this.frame.type === "card" ||
      this.frame.type === "result" ||
      this.frame.type === "item"
    ) {
      this.captureCheckpoint();
      this.step();
    }
  }

  choose(index: number) {
    if (!this.pendingChoice) return;
    const opt = this.pendingChoice[index];
    this.pendingChoice = null;
    this.applyEffects(opt.effects);
    this.captureCheckpoint();
    this.stack.push({ nodes: opt.nodes, i: 0 });
    this.step();
  }

  selectExplore(index: number) {
    const ex = this.currentExplore;
    if (!ex || ex.visited[index]) return;
    this.captureCheckpoint();
    this.stack.push({
      nodes: ex.places[index].nodes,
      i: 0,
      exploreOwner: ex,
      exploreIndex: index,
    });
    this.step();
  }

  captureCheckpoint() {
    this.checkpoint = this.serialize();
  }

  serialize(profile?: Profile): EngineSnapshot {
    return {
      version: 1,
      state: { ...this.state, stats: { ...this.state.stats }, conflict: { ...this.state.conflict }, items: [...this.state.items] },
      stack: JSON.parse(JSON.stringify(this.stack)),
      pendingChoice: this.pendingChoice
        ? JSON.parse(JSON.stringify(this.pendingChoice))
        : null,
      currentExplore: this.currentExplore
        ? JSON.parse(JSON.stringify(this.currentExplore))
        : null,
      inEnding: this.inEnding,
      endingCode: this.endingCode,
      done: this.done,
      frame: this.frame ? JSON.parse(JSON.stringify(this.frame)) : null,
      currentBgm: this.currentBgm,
      currentAmb: this.currentAmb,
      label: this.label,
      profile: profile ?? this.checkpoint?.profile ?? {
        name: "", gender: "g_x", grade: "grade_1", major: "maj_ec",
        mbti: "ENFP", portrait: 1,
        survey: { q1: null, q2: null, q3: null },
      },
      backlog: [...this.backlog],
      savedAt: Date.now(),
    };
  }

  static fromSnapshot(snap: EngineSnapshot): Engine {
    return new Engine(snap);
  }

  getCheckpoint(profile: Profile): EngineSnapshot {
    const base = this.checkpoint ?? this.serialize(profile);
    return { ...base, profile, savedAt: Date.now() };
  }
}
