# 붉은 무공훈장 — 웹 버전 개발·배포 가이드

## 무료로 쓸 수 있는 구성

| 역할 | 서비스 | 무료 한도 | 가입 |
|------|--------|-----------|------|
| **웹 호스팅** | [Vercel](https://vercel.com) | 개인 프로젝트 무료, 자동 HTTPS | GitHub 연동 |
| **데이터베이스** | [Supabase](https://supabase.com) | 500MB DB, 월 5만 API 요청 | 이메일 가입 |
| **소스 저장** | GitHub | 공개/비공개 저장소 무료 | 이미 `ziobiz/JIWOO` 사용 중 |

추가 비용 없이 **학생 접속 URL + 결과 DB + 관리자 분석**까지 가능합니다.

---

## 1. 로컬 개발 환경 (한 번만)

### 필요 프로그램

1. **Node.js 20+** — https://nodejs.org (LTS)
   - 설치 확인: `node --version` / `npm --version`
2. **Git** — https://git-scm.com
3. **(선택) VS Code / Cursor** — 코드 편집

### 프로젝트 설치

```powershell
cd d:\Delopment\JIWOO\web
npm install
```

### 게임 이미지·사운드 복사 (최초 1회)

```powershell
cd d:\Delopment\JIWOO\web
npm run assets
```

### 로컬 서버 실행

```powershell
npm run dev
```

브라우저에서 **http://localhost:3000** 접속

- `/` — 메인 (일반 유저용, 게임 시작만 노출)
- `/game` — 게임 (이식 진행 중)
- `/admin` — **관리자 전용** 분석 대시보드 (별도 URL, 비밀번호 로그인)
  - 홈·게임 화면에는 링크가 노출되지 않습니다. 관리자만 주소를 알고 접속합니다.
  - 로컬 개발에서 `ADMIN_SECRET` 미설정 시에만 비밀번호 없이 열립니다.

---

## 2. Supabase 무료 DB 설정 (15분)

### 2-1. 프로젝트 만들기

1. https://supabase.com 가입
2. **New Project** → 이름 `twc` 등, 리전 **Northeast Asia (Seoul)** 권장
3. DB 비밀번호 저장 (분실 시 복구 어려움)

### 2-2. 테이블 생성

1. 왼쪽 **SQL Editor** → New query
2. `web/supabase/schema.sql` 내용 전체 복사 → **Run**

### 2-3. API 키 복사

**Project Settings → API** 에서:

| 키 | 용도 | 환경 변수 |
|----|------|-----------|
| Project URL | 공개 | `NEXT_PUBLIC_SUPABASE_URL` |
| anon public | 클라이언트·결과 제출 | `NEXT_PUBLIC_SUPABASE_ANON_KEY` |
| service_role | 서버·관리자만 | `SUPABASE_SERVICE_ROLE_KEY` |

### 2-4. 로컬 환경 파일

```powershell
copy .env.local.example .env.local
```

`.env.local` 을 열어 위 키를 붙여넣고, 관리자 비밀번호 설정:

```
ADMIN_SECRET=원하는-강한-비밀번호
```

서버 재시작: `Ctrl+C` 후 `npm run dev`

---

## 3. Vercel 무료 배포

### 3-1. GitHub에 web 폴더 푸시

```powershell
cd d:\Delopment\JIWOO
git add web
git commit -m "Add Next.js web platform"
git push
```

### 3-2. Vercel 연결

1. https://vercel.com 가입 (GitHub 연동)
2. **Add New Project** → `ziobiz/JIWOO` 선택
3. **Root Directory** → `web` 로 지정
4. **Project Name** → `twc` 로 지정하면 주소가 `https://twc.vercel.app` 이 됩니다.
   (이미 사용 중인 이름이면 `twc-xxx` 형태가 되니, Settings → Domains 에서 조정)
5. **Environment Variables** 에 추가:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `ADMIN_SECRET` ← 관리자 로그인 비밀번호 (반드시 강하게 설정)
6. **Deploy**

배포 후 URL:

- 학생용: `https://twc.vercel.app` — 이 링크만 공유합니다.
- 관리자용: `https://twc.vercel.app/admin` — 담당자만 접속, 비밀번호(`ADMIN_SECRET`) 입력.

---

## 4. 데이터 흐름

```
학생 플레이 → POST /api/results → Supabase play_results
관리자 → /admin → GET /api/analyze → 집계 + 기준선 비교 + 출처 표시
```

Supabase 미설정 시 로컬 개발에서는 `붉은무공훈장/results.csv` 를 자동으로 읽습니다.

---

## 5. 자주 쓰는 명령

| 명령 | 설명 |
|------|------|
| `npm run dev` | 로컬 개발 서버 |
| `npm run build` | 배포 전 빌드 검증 |
| `npm run start` | 프로덕션 모드 로컬 실행 |

---

## 6. 개인정보·연구 윤리

- 실명 대신 **닉네임** 권장
- 수집 동의 문구를 게임 시작 전에 표시
- `service_role` 키는 **절대** GitHub·클라이언트에 노출 금지
- 발표 자료에는 개인 식별 정보 제거, `n=` 항상 표기

---

## 7. 다음 개발 단계

- [ ] pygame `story.py` → 웹 스토리 엔진 이식
- [ ] 캐릭터 생성 UI
- [ ] BGM/SFX 웹 오디오
- [ ] 게임 종료 시 자동 `/api/results` 제출

문의·이슈는 프로젝트 README를 참고하세요.
