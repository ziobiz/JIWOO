"use client";

import { useBranding } from "@/lib/useBranding";

/** 제작진 크레딧 — 타이틀·캐릭터 생성·설문·결과 화면에 공통 노출 */
export function CreditsFooter({ className = "" }: { className?: string }) {
  const b = useBranding();
  return (
    <footer
      className={`px-6 py-5 text-center border-t border-stone-900 ${className}`}
    >
      <p className="text-[11px] text-stone-500 leading-relaxed whitespace-pre-line">
        {b.credit}
      </p>
    </footer>
  );
}
