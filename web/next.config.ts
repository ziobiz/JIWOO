import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // 정적 게임 에셋(png)이 많아 최적화 파이프라인을 우회한다.
    unoptimized: true,
  },
};

export default nextConfig;
