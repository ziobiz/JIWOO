"use client";

import { useEffect, useState } from "react";

/**
 * 모바일·좁은 화면에서는 가로(landscape)만 허용.
 * 세로일 때는 전체 화면으로 회전 안내를 띄우고, 가능하면 orientation.lock 시도.
 */
export function LandscapeGate({
  children,
  hint = "화면을 가로로 돌려 주세요",
}: {
  children: React.ReactNode;
  hint?: string;
}) {
  const [portrait, setPortrait] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(orientation: portrait) and (max-width: 1024px)");
    const apply = () => setPortrait(mq.matches);
    apply();
    mq.addEventListener?.("change", apply);
    window.addEventListener("resize", apply);
    window.addEventListener("orientationchange", apply);

    const lock = async () => {
      try {
        const o = screen.orientation as ScreenOrientation & {
          lock?: (t: string) => Promise<void>;
        };
        if (o?.lock) await o.lock("landscape");
      } catch {
        /* 브라우저/미지원 무시 — 안내 오버레이로 대체 */
      }
    };
    const onInteract = () => {
      lock();
    };
    window.addEventListener("pointerdown", onInteract, { once: true });
    window.addEventListener("touchstart", onInteract, { once: true });

    return () => {
      mq.removeEventListener?.("change", apply);
      window.removeEventListener("resize", apply);
      window.removeEventListener("orientationchange", apply);
      window.removeEventListener("pointerdown", onInteract);
      window.removeEventListener("touchstart", onInteract);
    };
  }, []);

  return (
    <>
      <div className={`game-root min-h-dvh ${portrait ? "game-root--blocked" : ""}`}>
        {children}
      </div>
      {portrait && (
        <div
          className="rotate-gate"
          role="dialog"
          aria-live="polite"
          aria-label={hint}
        >
          <div className="rotate-gate__phone" aria-hidden />
          <p className="rotate-gate__text">{hint}</p>
        </div>
      )}
    </>
  );
}
