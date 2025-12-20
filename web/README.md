# Saegim Web

- Public (no-login): 주문/증빙 확인, 업로드
- Backoffice (login): `/app` 이하

## Setup

```bash
cp .env.local.example .env.local
pnpm i
pnpm dev
```

## Backoffice Login

v1은 **Clerk** 기준으로 세팅되어 있습니다.

- Clerk keys: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`
- (선택) JWT template: `NEXT_PUBLIC_AUTH_TOKEN_TEMPLATE`

서버는 JWKS 검증을 하므로, Server `.env`에도 `AUTH_JWKS_URL`, `AUTH_ISSUER`(필요 시 `AUTH_AUDIENCE`)를 맞춰주세요.
