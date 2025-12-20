# server

FastAPI app placeholder.


## Multi-tenant scoping

- `/api/v1/admin/*`는 JWT의 `org_id`(예: Clerk Organizations)를 테넌트 키로 사용합니다.
- 매핑 컬럼: `organizations.external_org_id`.
- 개발/플랫폼용 `X-Admin-Key` 사용 시:
  - `X-Org-Id: <internal organization id>`를 같이 보내면 특정 테넌트로 고정됩니다.
  - `X-Org-Id` 없이 호출하면 조직 전체 목록 등 플랫폼 스코프(위험)로 동작할 수 있습니다.
