import { getSupabaseAdmin, getSupabasePublic } from "./supabase";

export interface Branding {
  title: string;
  description: string;
  imageUrl: string;
}

/** 링크 미리보기(오픈그래프) 기본 브랜딩 — Supabase 미설정 시 폴백 */
export const DEFAULT_BRANDING: Branding = {
  title: "붉은 무공훈장 — The Weight of Courage",
  description:
    "1863년, 전쟁터에 선 한 청년의 이야기. 당신의 선택이 헨리의 용기와 두려움을 결정합니다. 교육·연구용 웹 비주얼 노벨.",
  imageUrl: "/assets/title_bg.png",
};

/** 배포 도메인 (오픈그래프 절대 URL 계산용) */
export function siteUrl(): string {
  return (
    process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") || "https://ttwc.vercel.app"
  );
}

/** 상대 경로 이미지를 절대 URL로 */
export function absoluteImage(imageUrl: string): string {
  if (/^https?:\/\//.test(imageUrl)) return imageUrl;
  return siteUrl() + (imageUrl.startsWith("/") ? "" : "/") + imageUrl;
}

/** 서버 전용 — Supabase에 저장된 브랜딩을 읽어 기본값과 병합 */
export async function resolveBranding(): Promise<Branding> {
  try {
    const sb = getSupabaseAdmin() ?? getSupabasePublic();
    if (!sb) return DEFAULT_BRANDING;
    const { data, error } = await sb
      .from("site_branding")
      .select("title, description, image_url")
      .eq("id", 1)
      .maybeSingle();
    if (error || !data) return DEFAULT_BRANDING;
    return {
      title: data.title || DEFAULT_BRANDING.title,
      description: data.description || DEFAULT_BRANDING.description,
      imageUrl: data.image_url || DEFAULT_BRANDING.imageUrl,
    };
  } catch {
    return DEFAULT_BRANDING;
  }
}
