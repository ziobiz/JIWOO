/** 게임 에셋 → web/public/assets (한글 경로 호환) */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const repoRoot = path.join(webRoot, "..");
const dst = path.join(webRoot, "public", "assets");

function countFiles(dir) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir).filter((n) => {
    try {
      return fs.statSync(path.join(dir, n)).isFile();
    } catch {
      return false;
    }
  }).length;
}

function findSrc() {
  const candidates = [
    path.join(repoRoot, "붉은무공훈장", "assets"),
    path.join(repoRoot, "붉은무공훈장", "assets"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  // 한글 폴더명 인코딩 이슈 대비: repo 루트에서 assets 포함 디렉터리 탐색
  try {
    for (const name of fs.readdirSync(repoRoot)) {
      const assets = path.join(repoRoot, name, "assets");
      if (fs.existsSync(assets) && countFiles(assets) > 10) return assets;
    }
  } catch {
    /* ignore */
  }
  return null;
}

const src = findSrc();
const existing = countFiles(dst);

if (!src) {
  if (existing > 0) {
    console.log(`[ok] source missing — using existing public/assets (${existing} files)`);
    process.exit(0);
  }
  console.error("[error] source not found and public/assets is empty");
  process.exit(1);
}

fs.mkdirSync(dst, { recursive: true });
let count = 0;
for (const name of fs.readdirSync(src)) {
  const from = path.join(src, name);
  if (!fs.statSync(from).isFile()) continue;
  fs.copyFileSync(from, path.join(dst, name));
  count++;
}
console.log(`[ok] ${count} files -> public/assets`);
