import Link from "next/link";
import type { Metadata } from "next";
import { absoluteImage, resolveBranding, siteUrl } from "@/lib/branding";

export const dynamic = "force-dynamic";

export async function generateMetadata(): Promise<Metadata> {
  const b = await resolveBranding();
  const base = siteUrl();
  const img = absoluteImage(b.imageUrl);
  return {
    metadataBase: new URL(base),
    title: b.title,
    description: b.description,
    openGraph: {
      type: "website",
      url: base,
      siteName: "붉은 무공훈장 — The Weight of Courage",
      title: b.title,
      description: b.description,
      images: [{ url: img, width: 1200, height: 630, alt: b.title }],
      locale: "ko_KR",
    },
    twitter: {
      card: "summary_large_image",
      title: b.title,
      description: b.description,
      images: [img],
    },
  };
}

export default async function Home() {
  const b = await resolveBranding();
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col">
      <main className="flex-1 max-w-2xl w-full mx-auto px-6 py-24 flex flex-col items-center text-center gap-12">
        <div className="space-y-4">
          <p className="text-xs tracking-[0.4em] text-amber-600 uppercase">
            A Visual Novel
          </p>
          <h1 className="text-5xl sm:text-6xl font-serif text-amber-50 leading-tight">
            붉은 무공훈장
          </h1>
          <p className="text-lg text-stone-400 font-serif italic">
            The Weight of Courage
          </p>
          <p className="text-sm text-stone-500 max-w-md mx-auto leading-relaxed pt-4 whitespace-pre-line">
            {b.tagline}
          </p>
        </div>

        <Link
          href="/game"
          className="rounded-full bg-amber-700 px-12 py-4 text-base font-medium hover:bg-amber-600 transition-colors shadow-lg shadow-amber-900/30"
        >
          게임 시작
        </Link>

        <div className="w-full rounded-xl border border-stone-800 bg-stone-900/60 p-5 text-left">
          <p className="text-xs text-stone-500 leading-relaxed whitespace-pre-line">
            {b.notice}
          </p>
        </div>
      </main>

      <footer className="px-6 py-6 text-center space-y-2 border-t border-stone-900">
        <p className="text-xs text-stone-500 leading-relaxed whitespace-pre-line">
          {b.credit}
        </p>
        <p className="text-xs text-stone-700">{b.copyright}</p>
      </footer>
    </div>
  );
}
