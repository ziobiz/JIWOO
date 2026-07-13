"use client";

import { useCallback, useEffect, useState } from "react";

interface BrandingResponse {
  title: string;
  description: string;
  imageUrl: string;
  siteUrl: string;
  defaults: { title: string; description: string; imageUrl: string };
}

/** 관리자 — 링크 공유 시 노출되는 소개(오픈그래프) 브랜딩 설정 */
export function BrandCard({ secret }: { secret: string }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [siteUrl, setSiteUrl] = useState("");
  const [defaults, setDefaults] =
    useState<BrandingResponse["defaults"] | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "saving" | "saved" | "error">(
    "loading",
  );
  const [msg, setMsg] = useState("");
  const [copied, setCopied] = useState(false);

  const fetchBranding = useCallback(async () => {
    setStatus("loading");
    try {
      const res = await fetch("/api/branding", { cache: "no-store" });
      const j = (await res.json()) as BrandingResponse;
      setTitle(j.title);
      setDescription(j.description);
      setImageUrl(j.imageUrl);
      setSiteUrl(j.siteUrl);
      setDefaults(j.defaults);
      setStatus("idle");
    } catch {
      setStatus("error");
      setMsg("브랜딩 정보를 불러오지 못했습니다.");
    }
  }, []);

  useEffect(() => {
    fetchBranding();
  }, [fetchBranding]);

  const save = useCallback(async () => {
    setStatus("saving");
    setMsg("");
    try {
      const res = await fetch(`/api/branding?secret=${encodeURIComponent(secret)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", "x-admin-secret": secret },
        body: JSON.stringify({ title, description, imageUrl }),
      });
      const j = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(j.error || `HTTP ${res.status}`);
      setStatus("saved");
      setMsg("저장되었습니다. 링크 미리보기는 다음 접속부터 반영됩니다.");
      setTimeout(() => setStatus("idle"), 2500);
    } catch (e) {
      setStatus("error");
      setMsg(e instanceof Error ? e.message : "저장 실패");
    }
  }, [secret, title, description, imageUrl]);

  const resetDefaults = useCallback(() => {
    if (!defaults) return;
    setTitle(defaults.title);
    setDescription(defaults.description);
    setImageUrl(defaults.imageUrl);
  }, [defaults]);

  const copyLink = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(siteUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* 무시 */
    }
  }, [siteUrl]);

  const host = (() => {
    try {
      return new URL(siteUrl).host;
    } catch {
      return siteUrl;
    }
  })();

  const previewImg = /^https?:\/\//.test(imageUrl)
    ? imageUrl
    : siteUrl.replace(/\/$/, "") + (imageUrl.startsWith("/") ? "" : "/") + imageUrl;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm break-inside-avoid">
      <h2 className="font-semibold text-lg text-slate-900">브랜드 (링크 미리보기)</h2>
      <p className="mt-0.5 text-xs text-slate-500">
        카카오톡·문자·SNS에 <span className="font-medium text-slate-700">{host || "사이트 주소"}</span> 링크를
        붙여넣으면 아래 소개 카드가 노출됩니다.
      </p>

      <div className="mt-5 grid gap-6 lg:grid-cols-2 items-start">
        {/* 편집 폼 */}
        <div className="no-print space-y-4">
          <Field label="제목 (Title)">
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={120}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-amber-500"
            />
          </Field>
          <Field label="설명 (Description)">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={400}
              rows={3}
              className="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-amber-500"
            />
            <span className="text-[10px] text-slate-400">{description.length}/400</span>
          </Field>
          <Field label="이미지 URL (권장 1200×630)">
            <input
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="/assets/title_bg.png 또는 https://..."
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-amber-500"
            />
          </Field>

          <div className="flex flex-wrap items-center gap-2 pt-1">
            <button
              type="button"
              onClick={save}
              disabled={status === "saving" || status === "loading"}
              className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-amber-500 disabled:opacity-40"
            >
              {status === "saving" ? "저장 중…" : "저장"}
            </button>
            <button
              type="button"
              onClick={resetDefaults}
              disabled={!defaults}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 disabled:opacity-40"
            >
              기본값 복원
            </button>
            <button
              type="button"
              onClick={copyLink}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
            >
              {copied ? "복사됨" : "링크 복사"}
            </button>
          </div>
          {msg && (
            <p
              className={`text-xs ${
                status === "error" ? "text-rose-500" : "text-emerald-600"
              }`}
            >
              {msg}
            </p>
          )}
          <p className="text-[11px] leading-relaxed text-slate-400">
            ※ 저장은 Supabase에 반영됩니다. 카카오톡 등 일부 메신저는 링크 미리보기를 캐시하므로,
            변경 후에도 이전 카드가 보이면 캐시가 갱신될 때까지 시간이 걸릴 수 있습니다.
          </p>
        </div>

        {/* 공유 미리보기 카드 */}
        <div className="space-y-2">
          <p className="text-xs font-semibold text-slate-700">공유 미리보기</p>
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            {previewImg ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={previewImg}
                alt="공유 이미지 미리보기"
                className="h-44 w-full object-cover"
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).style.display = "none";
                }}
              />
            ) : (
              <div className="flex h-44 w-full items-center justify-center bg-slate-100 text-xs text-slate-400">
                이미지 없음
              </div>
            )}
            <div className="space-y-1 p-4">
              <p className="text-[11px] uppercase tracking-wide text-slate-400">{host}</p>
              <p className="line-clamp-2 text-sm font-semibold text-slate-900">
                {title || "제목을 입력하세요"}
              </p>
              <p className="line-clamp-2 text-xs text-slate-500">
                {description || "설명을 입력하세요"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block space-y-1">
      <span className="text-xs font-semibold text-slate-700">{label}</span>
      {children}
    </label>
  );
}
