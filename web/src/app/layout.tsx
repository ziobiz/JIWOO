import type { Metadata } from "next";
import { Noto_Serif_KR, Noto_Sans_KR } from "next/font/google";
import "./globals.css";
import { DEFAULT_BRANDING, absoluteImage, siteUrl } from "@/lib/branding";

const sans = Noto_Sans_KR({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

const serif = Noto_Serif_KR({
  variable: "--font-serif",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl()),
  title: DEFAULT_BRANDING.title,
  description: DEFAULT_BRANDING.description,
  openGraph: {
    type: "website",
    url: siteUrl(),
    siteName: "붉은 무공훈장 — The Weight of Courage",
    title: DEFAULT_BRANDING.title,
    description: DEFAULT_BRANDING.description,
    images: [
      {
        url: absoluteImage(DEFAULT_BRANDING.imageUrl),
        width: 1200,
        height: 630,
        alt: DEFAULT_BRANDING.title,
      },
    ],
    locale: "ko_KR",
  },
  twitter: {
    card: "summary_large_image",
    title: DEFAULT_BRANDING.title,
    description: DEFAULT_BRANDING.description,
    images: [absoluteImage(DEFAULT_BRANDING.imageUrl)],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${sans.variable} ${serif.variable} h-full`}>
      <body className="min-h-full font-sans antialiased">{children}</body>
    </html>
  );
}
