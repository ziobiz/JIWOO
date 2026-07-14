"use client";

import { useEffect, useRef, useState } from "react";

/**
 * 캐릭터 버스트 — 초상 PNG의 어두운 사각 배경을 투명 처리해
 * 게임 배경이 그대로 비치도록 한다. (모서리 flood-fill + 소프트 페더)
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
        knockOutDarkBg(ctx, w, h);
        // pygame `_feather_bust` 와 같이 사방 소프트 페더
        featherEdges(ctx, w, h, 0.14, 0.18, 0.2);
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
    // 폴백: 원본 이미지 + CSS 마스크로 사각 티를 줄임
    return (
      <div className={`relative flex h-full w-full items-end justify-center ${className}`}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt}
          className="h-full w-auto max-w-full object-contain object-bottom"
          style={{
            WebkitMaskImage:
              "linear-gradient(to bottom, transparent 0%, black 12%, black 78%, transparent 100%), linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%)",
            maskImage:
              "linear-gradient(to bottom, transparent 0%, black 12%, black 78%, transparent 100%), linear-gradient(to right, transparent 0%, black 10%, black 90%, transparent 100%)",
            WebkitMaskComposite: "source-in",
            maskComposite: "intersect",
          }}
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

function colorDist(r: number, g: number, b: number, br: number, bg: number, bb: number) {
  const dr = r - br;
  const dg = g - bg;
  const db = b - bb;
  return Math.sqrt(dr * dr + dg * dg + db * db);
}

function knockOutDarkBg(ctx: CanvasRenderingContext2D, w: number, h: number) {
  const image = ctx.getImageData(0, 0, w, h);
  const d = image.data;
  const idx = (x: number, y: number) => (y * w + x) * 4;

  // 모서리 샘플로 배경색 추정
  const samples: number[][] = [];
  const pad = Math.max(2, Math.floor(Math.min(w, h) * 0.02));
  for (const [x, y] of [
    [pad, pad],
    [w - 1 - pad, pad],
    [pad, h - 1 - pad],
    [w - 1 - pad, h - 1 - pad],
    [Math.floor(w / 2), pad],
    [pad, Math.floor(h / 2)],
    [w - 1 - pad, Math.floor(h / 2)],
  ] as [number, number][]) {
    const i = idx(x, y);
    samples.push([d[i], d[i + 1], d[i + 2]]);
  }
  const br = samples.reduce((s, v) => s + v[0], 0) / samples.length;
  const bg = samples.reduce((s, v) => s + v[1], 0) / samples.length;
  const bb = samples.reduce((s, v) => s + v[2], 0) / samples.length;
  const luma = 0.299 * br + 0.587 * bg + 0.114 * bb;
  // 밝은 배경이면(거의 없음) chroma-key 생략
  if (luma > 90) {
    ctx.putImageData(image, 0, 0);
    return;
  }

  const thr = 42; // 배경과 색거리 — 머리카락/군복 보존
  const visited = new Uint8Array(w * h);
  const queue: number[] = [];

  const tryPush = (x: number, y: number) => {
    if (x < 0 || y < 0 || x >= w || y >= h) return;
    const p = y * w + x;
    if (visited[p]) return;
    const i = p * 4;
    const dist = colorDist(d[i], d[i + 1], d[i + 2], br, bg, bb);
    const pl = 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    // 가장자리 flood: 배경색과 비슷하고 어두운 픽셀만 통과
    if (dist <= thr && pl < 95) {
      visited[p] = 1;
      queue.push(p);
    } else {
      visited[p] = 2; // 경계(인물)
    }
  };

  for (let x = 0; x < w; x++) {
    tryPush(x, 0);
    tryPush(x, h - 1);
  }
  for (let y = 0; y < h; y++) {
    tryPush(0, y);
    tryPush(w - 1, y);
  }

  while (queue.length) {
    const p = queue.pop()!;
    const x = p % w;
    const y = (p - x) / w;
    const i = p * 4;
    d[i + 3] = 0; // 투명
    tryPush(x + 1, y);
    tryPush(x - 1, y);
    tryPush(x, y + 1);
    tryPush(x, y - 1);
  }

  // 경계 부근 soft alpha (배경에 가까운 인물 가장자리)
  for (let y = 1; y < h - 1; y++) {
    for (let x = 1; x < w - 1; x++) {
      const p = y * w + x;
      if (visited[p] === 1) continue;
      const i = p * 4;
      if (d[i + 3] === 0) continue;
      const dist = colorDist(d[i], d[i + 1], d[i + 2], br, bg, bb);
      if (dist < thr * 1.35) {
        const t = Math.min(1, dist / (thr * 1.35));
        d[i + 3] = Math.min(d[i + 3], Math.floor(255 * t * t));
      }
    }
  }

  ctx.putImageData(image, 0, 0);
}

function featherEdges(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  sidePct: number,
  topPct: number,
  botPct: number,
) {
  const image = ctx.getImageData(0, 0, w, h);
  const d = image.data;
  const fs = Math.max(1, Math.floor(w * sidePct));
  const ft = Math.max(1, Math.floor(h * topPct));
  const fb = Math.max(1, Math.floor(h * botPct));

  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      if (d[i + 3] === 0) continue;
      let m = 1;
      if (x < fs) m = Math.min(m, x / fs);
      if (x > w - 1 - fs) m = Math.min(m, (w - 1 - x) / fs);
      if (y < ft) m = Math.min(m, y / ft);
      if (y > h - 1 - fb) m = Math.min(m, (h - 1 - y) / fb);
      d[i + 3] = Math.floor(d[i + 3] * m);
    }
  }
  ctx.putImageData(image, 0, 0);
}
