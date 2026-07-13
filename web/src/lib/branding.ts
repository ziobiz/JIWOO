import { getSupabaseAdmin, getSupabasePublic } from "./supabase";

export interface Branding {
  title: string;
  description: string;
  imageUrl: string;
  /** 제공/제작진 크레딧 (푸터) */
  credit: string;
  /** 저작권 문구 (푸터) */
  copyright: string;
  /** 교육·연구 안내 문구 (홈 화면 안내 박스) */
  notice: string;
  /** 홈·타이틀 소개 태그라인 (줄바꿈은 \n) */
  tagline: string;
}

/** 링크 미리보기(오픈그래프) 기본 브랜딩 — Supabase 미설정 시 폴백 */
export const DEFAULT_BRANDING: Branding = {
  title: "붉은 무공훈장 — The Weight of Courage",
  description:
    "1863년, 전쟁터에 선 한 청년의 이야기. 당신의 선택이 헨리의 용기와 두려움을 결정합니다. 교육·연구용 웹 비주얼 노벨.",
  imageUrl: "/assets/title_bg.png",
  credit:
    "제공: 근현대 미국 문학 탐구 연구회ㅣ연구회원: 3학년 1반 박지수 이지우ㅣ그림: 석경원ㅣ소속: 동두천외국어고등학교",
  copyright:
    "© The Weight of Courage · 원작 Stephen Crane, 『The Red Badge of Courage』",
  notice:
    "이 게임은 교육·연구 목적의 성향 분석을 포함합니다. 시작 화면에서 간단한 캐릭터 설정과 설문에 참여하게 되며, 수집된 응답은 익명으로 통계 분석에만 사용됩니다.",
  tagline:
    "1863년, 전쟁터에 선 한 청년의 이야기.\n당신의 선택이 헨리의 용기와 두려움을 결정합니다.",
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
      .select("title, description, image_url, credit, copyright, notice, tagline")
      .eq("id", 1)
      .maybeSingle();
    if (error || !data) return DEFAULT_BRANDING;
    return {
      title: data.title || DEFAULT_BRANDING.title,
      description: data.description || DEFAULT_BRANDING.description,
      imageUrl: data.image_url || DEFAULT_BRANDING.imageUrl,
      credit: data.credit || DEFAULT_BRANDING.credit,
      copyright: data.copyright || DEFAULT_BRANDING.copyright,
      notice: data.notice || DEFAULT_BRANDING.notice,
      tagline: data.tagline || DEFAULT_BRANDING.tagline,
    };
  } catch {
    return DEFAULT_BRANDING;
  }
}
