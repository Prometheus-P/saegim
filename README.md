# 새김 (Saegim)

**배송/화환/행사 현장 사진 인증 + 자동 통지**를 위한 B2B SaaS MVP.

- 업체(화환/배송)가 주문을 등록 → 토큰(=QR) 발급
- 기사/현장 직원이 링크(또는 QR)로 접속 → 사진 업로드(1회)
- 구매자/수령자에게 카톡/문자(현재는 mock 기록)로 사진 인증 링크 전송
- 관리자(업체)용 웹 백오피스 제공

## Quick Start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

### 1) DB 마이그레이션

```bash
docker compose exec api alembic upgrade head
```

### 2) 테스트 데이터 시드

```bash
docker compose exec api python -m scripts.seed_test_data
```

## URLs

- Web (Public + Backoffice): http://localhost:3000
- API Swagger: http://localhost:8000/docs
- Public API base: http://localhost:8000/api/v1/public
- Admin API base: http://localhost:8000/api/v1/admin

## Backoffice (업체용)

- `/app/orders` : 주문 목록
- `/app/orders/new` : 주문 생성
- `/app/orders/{id}` : 토큰 발급/링크 확인/재발송(큐잉)

## Auth (Backoffice)

- 기본: **외부 로그인(Clerk/Auth0 등)** → Web은 세션/보호 라우팅, API는 **Bearer JWT(JWKS 검증)** 방식.
- fallback(개발/비상용): `X-Admin-Key` (서버 `.env`의 `ADMIN_API_KEY`, `ALLOW_ADMIN_API_KEY=true`)

### Clerk 권장 흐름

1) Clerk 대시보드에서 앱 생성  
2) `.env.local`에 `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` 세팅  
3) (선택) JWT Template 생성 후 Web의 `NEXT_PUBLIC_AUTH_TOKEN_TEMPLATE`에 template 이름 지정  
4) Server `.env`에 `AUTH_JWKS_URL`, `AUTH_ISSUER`(필요 시 `AUTH_AUDIENCE`) 세팅

> **중요**: 화면 보호(Next middleware)만 믿지 말고, **API 서버에서 토큰 검증을 반드시 유지**하세요.

## Public Flow

- 업로드 링크(기사/현장): `/proof/{token}`
- 확인 링크(구매자/수령자): `/p/{token}`

## Notes

- 기본 메시징은 `MESSAGING_PROVIDER=mock`로 DB `notifications` 테이블에만 기록됩니다.
- `LOCAL_UPLOAD_DIR=/data/uploads`에 업로드되며, API에서 `/uploads/...`로 서빙합니다.
