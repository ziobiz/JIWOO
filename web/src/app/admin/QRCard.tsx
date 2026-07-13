"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

type Preset = { key: string; label: string; path: string };

const PRESETS: Preset[] = [
  { key: "home", label: "홈 화면 (게임 시작)", path: "/" },
  { key: "game", label: "게임 바로 시작", path: "/game" },
];

/** 관리자 — 사이트 접속용 QR 코드 생성·배포 */
export function QRCard() {
  const [origin, setOrigin] = useState("");
  const [preset, setPreset] = useState<Preset>(PRESETS[0]);
  const [custom, setCustom] = useState("");
  const [useCustom, setUseCustom] = useState(false);
  const [copied, setCopied] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    setOrigin(window.location.origin);
  }, []);

  const url = useMemo(() => {
    if (useCustom) return custom.trim();
    if (!origin) return "";
    return origin.replace(/\/$/, "") + preset.path;
  }, [useCustom, custom, origin, preset]);

  const valid = /^https?:\/\/.+/.test(url);

  const render = useCallback(async () => {
    const canvas = canvasRef.current;
    if (!canvas || !valid) return;
    const QR = (await import("qrcode")).default;
    await QR.toCanvas(canvas, url, {
      width: 320,
      margin: 2,
      errorCorrectionLevel: "M",
      color: { dark: "#0f172a", light: "#ffffff" },
    });
  }, [url, valid]);

  useEffect(() => {
    render();
  }, [render]);

  const downloadPng = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const a = document.createElement("a");
    a.href = canvas.toDataURL("image/png");
    a.download = "붉은무공훈장_QR.png";
    a.click();
  }, []);

  const downloadSvg = useCallback(async () => {
    if (!valid) return;
    const QR = (await import("qrcode")).default;
    const svg = await QR.toString(url, {
      type: "svg",
      margin: 2,
      errorCorrectionLevel: "M",
      color: { dark: "#0f172a", light: "#ffffff" },
    });
    const blob = new Blob([svg], { type: "image/svg+xml" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "붉은무공훈장_QR.svg";
    a.click();
    URL.revokeObjectURL(a.href);
  }, [url, valid]);

  const copyUrl = useCallback(async () => {
    if (!valid) return;
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard 미지원 무시 */
    }
  }, [url, valid]);

  const printQr = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !valid) return;
    const dataUrl = canvas.toDataURL("image/png");
    const w = window.open("", "_blank", "width=520,height=680");
    if (!w) return;
    w.document.write(`<!doctype html><html><head><title>붉은 무공훈장 · 접속 QR</title>
      <style>body{font-family:sans-serif;text-align:center;padding:40px;color:#0f172a}
      h1{font-size:20px;margin:0 0 4px}p{color:#475569;font-size:13px;margin:2px 0}
      img{width:340px;height:340px;margin:24px 0}code{font-size:12px;color:#334155}</style>
      </head><body>
      <h1>붉은 무공훈장 · The Weight of Courage</h1>
      <p>카메라로 QR을 촬영하면 게임에 접속됩니다.</p>
      <img src="${dataUrl}" alt="QR"/>
      <p><code>${url}</code></p>
      </body></html>`);
    w.document.close();
    w.focus();
    setTimeout(() => w.print(), 300);
  }, [url, valid]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm break-inside-avoid">
      <h2 className="font-semibold text-lg text-slate-900">QR 배포</h2>
      <p className="mt-0.5 text-xs text-slate-500">
        아래 QR을 카메라로 촬영하면 게임 사이트로 접속됩니다. 인쇄·이미지로 배포하세요.
      </p>

      <div className="mt-5 grid gap-6 md:grid-cols-[auto_1fr] items-start">
        {/* QR 미리보기 */}
        <div className="flex flex-col items-center gap-3">
          <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
            <canvas ref={canvasRef} className="block h-[220px] w-[220px]" />
          </div>
          <div className="no-print flex flex-wrap justify-center gap-2">
            <QrBtn onClick={downloadPng}>PNG 저장</QrBtn>
            <QrBtn onClick={downloadSvg}>SVG 저장</QrBtn>
            <QrBtn onClick={printQr}>인쇄</QrBtn>
          </div>
        </div>

        {/* 대상 주소 설정 */}
        <div className="no-print space-y-4">
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-700">접속 대상</p>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button
                  key={p.key}
                  type="button"
                  onClick={() => {
                    setUseCustom(false);
                    setPreset(p);
                  }}
                  className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                    !useCustom && preset.key === p.key
                      ? "border-amber-500 bg-amber-50 text-amber-700"
                      : "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  {p.label}
                </button>
              ))}
              <button
                type="button"
                onClick={() => setUseCustom(true)}
                className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                  useCustom
                    ? "border-amber-500 bg-amber-50 text-amber-700"
                    : "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                }`}
              >
                직접 입력
              </button>
            </div>
          </div>

          {useCustom && (
            <input
              type="url"
              value={custom}
              onChange={(e) => setCustom(e.target.value)}
              placeholder="https://example.com/game"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-amber-500"
            />
          )}

          <div className="space-y-1">
            <p className="text-xs font-semibold text-slate-700">QR 주소</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 truncate rounded-lg bg-slate-100 px-3 py-2 text-xs text-slate-700">
                {url || "주소를 확인하는 중…"}
              </code>
              <QrBtn onClick={copyUrl} disabled={!valid}>
                {copied ? "복사됨" : "복사"}
              </QrBtn>
            </div>
            {!valid && url !== "" && (
              <p className="text-xs text-rose-500">http(s):// 로 시작하는 올바른 주소를 입력하세요.</p>
            )}
          </div>

          <p className="text-xs leading-relaxed text-slate-500">
            팁 · 대부분의 스마트폰은 기본 카메라 앱으로 QR을 비추면 접속 링크가 자동으로 뜹니다.
            발표·게시용으로는 인쇄가 선명한 SVG 저장을 권장합니다.
          </p>
        </div>
      </div>
    </section>
  );
}

function QrBtn({
  onClick,
  disabled,
  children,
}: {
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100 disabled:opacity-40"
    >
      {children}
    </button>
  );
}
