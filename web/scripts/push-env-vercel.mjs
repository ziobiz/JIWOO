/**
 * web/.env.local 의 Supabase/ADMIN 값을 Vercel(Production+Preview)에 등록합니다.
 *
 * 사용:
 *   1) web/.env.local 에 실제 값 4개를 넣는다 (.env.local.example 참고)
 *   2) cd web && node scripts/push-env-vercel.mjs
 *   3) npx vercel --prod --yes   (재배포 필수 — NEXT_PUBLIC_* 는 빌드에 포함)
 */
import { execFileSync } from "node:child_process";
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = resolve(__dirname, "..");
const envPath = resolve(root, ".env.local");

const KEYS = [
  "NEXT_PUBLIC_SUPABASE_URL",
  "NEXT_PUBLIC_SUPABASE_ANON_KEY",
  "SUPABASE_SERVICE_ROLE_KEY",
  "ADMIN_SECRET",
];

function loadEnv(file) {
  const map = {};
  if (!existsSync(file)) return map;
  for (const line of readFileSync(file, "utf8").split(/\r?\n/)) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const i = t.indexOf("=");
    if (i < 0) continue;
    let k = t.slice(0, i).trim();
    let v = t.slice(i + 1).trim();
    if (
      (v.startsWith('"') && v.endsWith('"')) ||
      (v.startsWith("'") && v.endsWith("'"))
    ) {
      v = v.slice(1, -1);
    }
    map[k] = v;
  }
  return map;
}

function run(args, input) {
  return execFileSync("npx", ["vercel", ...args], {
    cwd: resolve(root, ".."),
    input,
    encoding: "utf8",
    stdio: ["pipe", "pipe", "pipe"],
    shell: true,
  });
}

function main() {
  const env = loadEnv(envPath);
  const missing = KEYS.filter((k) => !env[k]?.trim());
  if (missing.length) {
    console.error(
      `[fail] ${envPath} 에 다음 값이 없습니다:\n  - ${missing.join("\n  - ")}`,
    );
    console.error(
      "Supabase → Project Settings → API 에서 URL/anon/service_role 을 복사하고,",
    );
    console.error("ADMIN_SECRET 은 관리자 비밀번호로 직접 정하세요.");
    process.exit(1);
  }

  const url = env.NEXT_PUBLIC_SUPABASE_URL.trim();
  if (!/^https?:\/\//i.test(url) || !url.includes("supabase.co")) {
    console.error(
      `[fail] NEXT_PUBLIC_SUPABASE_URL 형식 확인: https://xxxx.supabase.co (현재: ${url.slice(0, 40)}…)`,
    );
    process.exit(1);
  }

  for (const key of KEYS) {
    const value = env[key].trim();
    for (const target of ["production", "preview"]) {
      try {
        run(["env", "rm", key, target, "--yes"]);
        console.log(`[rm] ${key} (${target})`);
      } catch {
        /* 없어도 무시 */
      }
      try {
        run(["env", "add", key, target, "--yes"], `${value}\n`);
        console.log(`[add] ${key} (${target}) len=${value.length}`);
      } catch (e) {
        console.error(`[fail] add ${key} ${target}:`, e.stderr || e.message);
        process.exit(1);
      }
    }
  }

  console.log("\n[ok] Vercel 환경변수 등록 완료.");
  console.log("반드시 재배포하세요:  npx vercel --prod --yes");
  console.log(
    "그 다음 https://ttwc.vercel.app/api/results POST 가 503이 아니어야 합니다.",
  );
}

main();
