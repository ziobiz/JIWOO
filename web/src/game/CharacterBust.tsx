"use client";

import { useEffect, useRef, useState } from "react";

/**
 * 캐릭터 버스트 — 인물 실루엣(테두리) 바깥의 어두운 사각 배경만 투명화.
 * 인물 안(얼굴·머리·옷)은 완전 불투명으로 유지한다.
 */
export function CharacterBust({
  src,
  alt = "character",
  className = "",
}: {
  src: string;
  alt?: string;
  className?: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setReady(false);
    setFailed(false);

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      if (cancelled) return;
      const canvas = canvasRef.current;
      if (!canvas) return;
      const w = img.naturalWidth || img.width;
      const h = img.naturalHeight || img.height;
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext("2d", { willReadFrequently: true });
      if (!ctx) {
        setFailed(true);
        return;
      }
      ctx.clearRect(0, 0, w, h);
      ctx.drawImage(img, 0, 0);
      try {
        cutBackgroundOutsideSilhouette(ctx, w, h);
        // 하단만 살짝 페더(대사창과 자연스럽게) — 상단/얼굴은 절대 깎지 않음
        featherBottomOnly(ctx, w, h, 0.12);
        setReady(true);
      } catch {
        setFailed(true);
      }
    };
    img.onerror = () => {
      if (!cancelled) setFailed(true);
    };
    img.src = src;

    return () => {
      cancelled = true;
    };
  }, [src]);

  if (failed) {
    return (
      <div className={`relative flex h-full w-full items-end justify-center ${className}`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt}
          className="h-full w-auto max-w-full object-contain object-bottom"
        />
      </div>
    );
  }

  return (
    <div className={`relative flex h-full w-full items-end justify-center ${className}`}>
      <canvas
        ref={canvasRef}
        aria-label={alt}
        className={`h-full w-auto max-w-full transition-opacity duration-300 ${
          ready ? "opacity-100" : "opacity-0"
        }`}
      />
    </div>
  );
}

function luma(r: number, g: number, b: number) {
  return 0.299 * r + 0.587 * g + 0.114 * b;
}

function colorDist(r: number, g: number, b: number, br: number, bg: number, bb: number) {
  const dr = r - br;
  const dg = g - bg;
  const db = b - bb;
  return Math.sqrt(dr * dr + dg * dg + db * db);
}

/**
 * 외곽에서만 flood-fill 해 '배경 영역'을 찾고, 그 바깥만 투명 처리.
 * - 인물 내부 픽셀은 visited 되지 않으면 alpha 를 절대 건드리지 않음
 * - 텍스처(국소 분산)가 있는 픽셀은 배경으로 취급하지 않아 머리카락/그림자가 뚫리지 않음
 */
function cutBackgroundOutsideSilhouette(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
) {
  const image = ctx.getImageData(0, 0, w, h);
  const d = image.data;

  const pad = Math.max(2, Math.floor(Math.min(w, h) * 0.015));
  const samples: [number, number, number][] = [];
  for (const [x, y] of [
    [pad, pad],
    [w - 1 - pad, pad],
    [pad, h - 1 - pad],
    [w - 1 - pad, h - 1 - pad],
    [Math.floor(w / 2), pad],
    [pad, Math.floor(h * 0.3)],
    [w - 1 - pad, Math.floor(h * 0.3)],
  ] as [number, number][]) {
    const i = (y * w + x) * 4;
    samples.push([d[i], d[i + 1], d[i + 2]]);
  }
  const br = samples.reduce((s, v) => s + v[0], 0) / samples.length;
  const bgc = samples.reduce((s, v) => s + v[1], 0) / samples.length;
  const bb = samples.reduce((s, v) => s + v[2], 0) / samples.length;
  const bgLuma = luma(br, bgc, bb);
  // 배경이 어두워야 이 처리가 의미가 있음
  if (bgLuma > 85) {
    ctx.putImageData(image, 0, 0);
    return;
  }

  // 국소 루마 분산 — 평탄한 칠 배경 vs 머리카락/피부 텍스처 구분
  const localStd = (x: number, y: number) => {
    let sum = 0;
    let sum2 = 0;
    let n = 0;
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        const xx = x + dx;
        const yy = y + dy;
        if (xx < 0 || yy < 0 || xx >= w || yy >= h) continue;
        const i = (yy * w + xx) * 4;
        const L = luma(d[i], d[i + 1], d[i + 2]);
        sum += L;
        sum2 += L * L;
        n++;
      }
    }
    const mean = sum / n;
    return Math.sqrt(Math.max(0, sum2 / n - mean * mean));
  };

  /** 외곽 flood 가 통과할 '배경 후보' — 엄격하게 */
  const isBackgroundCandidate = (x: number, y: number) => {
    const i = (y * w + x) * 4;
    const r = d[i];
    const g = d[i + 1];
    const b = d[i + 2];
    const dist = colorDist(r, g, b, br, bgc, bb);
    const L = luma(r, g, b);
    // 색이 배경과 가깝고, 너무 밝지 않으며, 평면(저분산)
    if (dist > 30) return false;
    if (L > 78) return false;
    if (localStd(x, y) > 14) return false;
    return true;
  };

  // 0=미방문, 1=배경(투명화), 2=인물(불투명 유지)
  const mark = new Uint8Array(w * h);
  const queue: number[] = [];

  const seed = (x: number, y: number) => {
    const p = y * w + x;
    if (mark[p]) return;
    if (isBackgroundCandidate(x, y)) {
      mark[p] = 1;
      queue.push(p);
    } else {
      mark[p] = 2;
    }
  };

  for (let x = 0; x < w; x++) {
    seed(x, 0);
    seed(x, h - 1);
  }
  for (let y = 0; y < h; y++) {
    seed(0, y);
    seed(w - 1, y);
  }

  while (queue.length) {
    const p = queue.pop()!;
    const x = p % w;
    const y = (p - x) / w;
    // 4-이웃만 — 테두리로만 전파 (인물 구멍으로 새지 않게)
    for (const [nx, ny] of [
      [x + 1, y],
      [x - 1, y],
      [x, y + 1],
      [x, y - 1],
    ] as [number, number][]) {
      if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
      const np = ny * w + nx;
      if (mark[np]) continue;
      if (isBackgroundCandidate(nx, ny)) {
        mark[np] = 1;
        queue.push(np);
      } else {
        mark[np] = 2; // 실루엣 경계 — 여기서 멈춤
      }
    }
  }

  // 배경만 완전 투명. 인물(2)과 미방문(0, 내부에 고립된 영역)은 불투명 유지
  for (let p = 0; p < w * h; p++) {
    if (mark[p] === 1) {
      d[p * 4 + 3] = 0;
    }
  }

  // 실루엣 경계 1~2px 만 아주 약한 소프트 (테두리 안티앨리어싱)
  // 인물 안쪽으로 넓게 퍼지지 않음
  const soft = new Uint8Array(w * h);
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const p = y * w + x;
      if (mark[p] !== 2) continue;
      let nearBg = false;
      for (const [dx, dy] of [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
        [1, 1],
        [-1, -1],
        [1, -1],
        [-1, 1],
      ] as [number, number][]) {
        if (mark[(y + dy) * w + (x + dx)] === 1) {
          nearBg = true;
          break;
        }
      }
      if (nearBg) soft[p] = 1;
    }
  }
  for (let p = 0; p < w * h; p++) {
    if (!soft[p]) continue;
    const i = p * 4;
    // 경계에서만 살짝 — 얼굴 내부는 soft=0 이므로 영향 없음
    d[i + 3] = Math.min(d[i + 3], 210);
  }

  ctx.putImageData(image, 0, 0);
}

/** 하단 일부만 페더 — 머리/얼굴은 건드리지 않음 */
function featherBottomOnly(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  botPct: number,
) {
  const image = ctx.getImageData(0, 0, w, h);
  const d = image.data;
  const fb = Math.max(1, Math.floor(h * botPct));
  const startY = h - fb;
  for (let y = startY; y < h; y++) {
    const m = (h - 1 - y) / fb; // 1 → 0
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      if (d[i + 3] === 0) continue;
      d[i + 3] = Math.floor(d[i + 3] * m);
    }
  }
  ctx.putImageData(image, 0, 0);
}
