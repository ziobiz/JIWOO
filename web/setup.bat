@echo off
chcp 65001 >nul
echo ========================================
echo  붉은 무공훈장 - 웹 개발 환경 세팅
echo ========================================
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo [오류] Node.js 가 설치되어 있지 않습니다.
  echo        https://nodejs.org 에서 LTS 버전을 설치하세요.
  pause
  exit /b 1
)

echo [1/4] Node.js 버전
node --version
npm --version
echo.

echo [2/4] npm 패키지 설치
call npm install
if errorlevel 1 exit /b 1
echo.

echo [3/4] 게임 에셋 복사
node scripts\copy-assets.mjs
echo.

if not exist .env.local (
  echo [4/4] .env.local 생성
  copy .env.local.example .env.local
  echo.
  echo  .env.local 파일을 열어 Supabase 키를 입력하세요.
  echo  가이드: SETUP.md
) else (
  echo [4/4] .env.local 이미 존재 - 건너뜀
)

echo.
echo ========================================
echo  세팅 완료!  npm run dev 로 시작하세요.
echo  http://localhost:3000
echo ========================================
pause
