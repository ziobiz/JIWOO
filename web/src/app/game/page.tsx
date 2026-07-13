import Link from "next/link";

export default function GamePage() {
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col">
      <header className="border-b border-stone-800 px-6 py-4 flex justify-between items-center">
        <div>
          <p className="text-xs text-amber-600 tracking-widest">GAME</p>
          <h1 className="text-xl font-serif text-amber-100">붉은 무공훈장</h1>
        </div>
        <Link href="/" className="text-sm text-stone-400 hover:text-amber-200">
          ← 홈
        </Link>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-16 text-center max-w-lg mx-auto">
        <p className="text-amber-200/80 font-serif text-2xl mb-4">
          The Weight of Courage
        </p>
        <p className="text-stone-400 text-sm leading-relaxed mb-8">
          곧 시작합니다. 캐릭터를 만들고, 사전 설문에 답한 뒤 헨리의 이야기를
          함께 겪게 됩니다. 당신의 선택이 결말을 바꿉니다.
        </p>
        <div className="rounded-lg border border-amber-900/40 bg-stone-900 p-5 text-left text-sm space-y-2 w-full">
          <p className="text-amber-100 font-medium">준비 중인 여정</p>
          <ul className="text-stone-400 list-disc list-inside space-y-1">
            <li>나만의 캐릭터 만들기 (이름 · 성별 · 학년 · 전공 · MBTI)</li>
            <li>나의 성향 테스트 (가치관 밸런스 3문항)</li>
            <li>프롤로그부터 엔딩까지 5개 챕터</li>
            <li>선택에 따라 달라지는 5가지 결말</li>
          </ul>
        </div>
        <Link
          href="/"
          className="mt-8 text-xs text-stone-600 hover:text-stone-400"
        >
          ← 홈으로 돌아가기
        </Link>
      </main>
    </div>
  );
}
