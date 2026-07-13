import {
  GAME,
  type Node,
  type ChoiceOption,
  type ExplorePlace,
  determineEnding,
  evalCond,
  resolveSpeakerPortrait,
} from "./gameData";

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

function clamp(n: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, n));
}

export class Engine {
  state: GameState;
  frame: Frame | null = null;
  done = false;
  endingCode: string | null = null;

  private stack: StackFrame[] = [];
  private pendingChoice: ChoiceOption[] | null = null;
  private currentExplore: ExploreState | null = null;
  private inEnding = false;

  // 외부 훅 (오디오)
  onBgm?: (key: string) => void;
  onAmb?: (key: string) => void;
  onSfx?: (key: string) => void;

  constructor() {
    this.state = {
      stats: { ...GAME.constants.initialStats },
      conflict: { 인간: 0, 군인: 0 },
      items: [],
      bg: null,
      charKey: null,
    };
    this.stack = [{ nodes: GAME.story, i: 0 }];
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
    // 일시정지 프레임을 만들거나 종료할 때까지 노드를 처리
    // 무한 루프 방지용 상한
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
        case "bg":
          this.state.bg = node[1] as string;
          break;
        case "char":
          this.state.charKey = (node[1] as string | null) ?? null;
          break;
        case "bgm":
          this.onBgm?.(node[1] as string);
          break;
        case "amb":
          this.onAmb?.(node[1] as string);
          break;
        case "sfx":
          this.onSfx?.(node[1] as string);
          break;
        case "stat":
          this.applyEffects(node[1] as Record<string, number>);
          break;
        case "item": {
          const name = node[1] as string;
          this.state.items.push(name);
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
        case "say":
          this.frame = {
            type: "text",
            mode: "say",
            speaker: node[1] as string,
            text: node[2] as string,
            portrait: resolveSpeakerPortrait(
              node[1] as string,
              node[2] as string,
            ),
          };
          return;
        case "mono":
          this.frame = { type: "text", mode: "mono", speaker: null, text: node[1] as string, portrait: null };
          return;
        case "narr":
          this.frame = { type: "text", mode: "narr", speaker: null, text: node[1] as string, portrait: null };
          return;
        case "act":
          this.frame = { type: "text", mode: "act", speaker: null, text: node[1] as string, portrait: null };
          return;
        case "title":
          this.frame = {
            type: "title",
            lines: node[1] as string[],
            sub: (node[2] as string | null) ?? null,
          };
          return;
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
          const code = determineEnding(this.state.stats, this.state.items.length);
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

  /** 대사/타이틀/카드/결과/아이템 프레임에서 클릭 진행 */
  advance() {
    if (!this.frame) return;
    if (
      this.frame.type === "text" ||
      this.frame.type === "title" ||
      this.frame.type === "card" ||
      this.frame.type === "result" ||
      this.frame.type === "item"
    ) {
      this.step();
    }
  }

  choose(index: number) {
    if (!this.pendingChoice) return;
    const opt = this.pendingChoice[index];
    this.pendingChoice = null;
    this.applyEffects(opt.effects);
    this.stack.push({ nodes: opt.nodes, i: 0 });
    this.step();
  }

  selectExplore(index: number) {
    const ex = this.currentExplore;
    if (!ex || ex.visited[index]) return;
    this.stack.push({
      nodes: ex.places[index].nodes,
      i: 0,
      exploreOwner: ex,
      exploreIndex: index,
    });
    this.step();
  }
}
