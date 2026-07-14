"use client";

/**
 * 캐릭터 버스트 — 누끼 처리된 투명 PNG를 그대로 표시.
 * (배경 제거는 assets 단계에서 rembg 로 완료됨)
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
  return (
    <div className={`relative flex h-full w-full items-end justify-center ${className}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={alt}
        draggable={false}
        className="h-full w-auto max-w-full select-none object-contain object-bottom"
        style={{
          // 하단만 살짝 페더 — 인물 본체(얼굴)는 완전 불투명
          WebkitMaskImage:
            "linear-gradient(to bottom, #000 0%, #000 82%, transparent 100%)",
          maskImage:
            "linear-gradient(to bottom, #000 0%, #000 82%, transparent 100%)",
        }}
      />
    </div>
  );
}
