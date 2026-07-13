"use client";

import { useEffect, useState } from "react";
import { DEFAULT_BRANDING, type Branding } from "./branding";

let _cache: Branding | null = null;
let _inflight: Promise<Branding> | null = null;

async function fetchBranding(): Promise<Branding> {
  if (_cache) return _cache;
  if (_inflight) return _inflight;
  _inflight = fetch("/api/branding", { cache: "no-store" })
    .then((r) => r.json())
    .then((j) => {
      _cache = {
        title: j.title ?? DEFAULT_BRANDING.title,
        description: j.description ?? DEFAULT_BRANDING.description,
        imageUrl: j.imageUrl ?? DEFAULT_BRANDING.imageUrl,
        credit: j.credit ?? DEFAULT_BRANDING.credit,
        copyright: j.copyright ?? DEFAULT_BRANDING.copyright,
        notice: j.notice ?? DEFAULT_BRANDING.notice,
        tagline: j.tagline ?? DEFAULT_BRANDING.tagline,
      };
      return _cache;
    })
    .catch(() => DEFAULT_BRANDING)
    .finally(() => {
      _inflight = null;
    });
  return _inflight;
}

/** 클라이언트 — 저장된 브랜딩을 읽고, 로드 전에는 기본값을 반환 */
export function useBranding(): Branding {
  const [branding, setBranding] = useState<Branding>(_cache ?? DEFAULT_BRANDING);
  useEffect(() => {
    let alive = true;
    fetchBranding().then((b) => {
      if (alive) setBranding(b);
    });
    return () => {
      alive = false;
    };
  }, []);
  return branding;
}
