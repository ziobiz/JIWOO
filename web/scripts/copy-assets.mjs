/** 게임 에셋 → web/public/assets (한글 경로 호환) */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.join(__dirname, "..");
const repoRoot = path.join(webRoot, "..");
const src = path.join(repoRoot, "붉은무공훈장", "assets");
const dst = path.join(webRoot, "public", "assets");

if (!fs.existsSync(src)) {
  console.error("[warn] source not found:", src);
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
