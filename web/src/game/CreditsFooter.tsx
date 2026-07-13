/** 제작진 크레딧 — 타이틀·캐릭터 생성·설문·결과 화면에 공통 노출 */
export function CreditsFooter({ className = "" }: { className?: string }) {
  return (
    <footer
      className={`px-6 py-5 text-center border-t border-stone-900 ${className}`}
    >
      <p className="text-[11px] text-stone-500 leading-relaxed">
        제공: 근현대 미국 문학 탐구 연구회
        <span className="mx-1.5 text-stone-700">ㅣ</span>
        연구회원: 3학년 1반 박지수 이지우
        <span className="mx-1.5 text-stone-700">ㅣ</span>
        그림: 석경원
        <span className="mx-1.5 text-stone-700">ㅣ</span>
        소속: 동두천외국어고등학교
      </p>
    </footer>
  );
}
