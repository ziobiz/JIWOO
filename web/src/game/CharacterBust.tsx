"use client";

/**
 * 캐릭터 버스트
 *
 * 픽셀 chroma-key / flood-fill 은 어두운 머리·그림자까지 뚫어 버리므로 사용하지 않음.
 * 원본 인물(얼굴·옷)은 완전 불투명으로 유지하고,
 * CSS 마스크로 사각 PNG의 바깥 모서리(배경)만 부드럽게 잘라 게임 배경과 섞는다.
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
          // 중앙 타원 = 인물 유지 / 바깥 = 사각 배경 페이드
          // 하단은 대사창과 자연스럽게 이어지도록 세로 그라데이션과 합성
          WebkitMaskImage: [
            "radial-gradient(ellipse 62% 68% at 50% 40%, #000 58%, rgba(0,0,0,0.85) 72%, transparent 100%)",
            "linear-gradient(to bottom, #000 0%, #000 78%, transparent 100%)",
          ].join(", "),
          maskImage: [
            "radial-gradient(ellipse 62% 68% at 50% 40%, #000 58%, rgba(0,0,0,0.85) 72%, transparent 100%)",
            "linear-gradient(to bottom, #000 0%, #000 78%, transparent 100%)",
          ].join(", "),
          WebkitMaskComposite: "source-in",
          maskComposite: "intersect",
          WebkitMaskRepeat: "no-repeat",
          maskRepeat: "no-repeat",
          WebkitMaskSize: "100% 100%",
          maskSize: "100% 100%",
        }}
      />
    </div>
  );
}
