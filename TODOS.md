# TODOS

## Phase 1 MVP (당근마켓 for B2B) — 구현 시 필수 확인

### BUG: MaterialStatus enum 불일치
- **What:** 백엔드 MaterialStatus는 ACTIVE/REVIEWING/SOLD/HIDDEN인데, 프론트엔드에서 RESERVED/reserved/sold 등 존재하지 않는 상태값을 참조
- **Why:** 프론트-백 간 status enum이 어긋나면 자재 상태 표시가 깨짐 (예: 예약중 표시가 안 됨)
- **Context:** Codex eng review에서 발견 (2026-03-25). 파일: `app/models/material.py:17`, `apps/web/src/app/material/[id]/page.tsx:20`, `apps/web/src/app/page.tsx:246`
- **How to fix:** 프론트엔드 재설계 시 백엔드 enum에 맞춰 통일. RESERVED가 필요하면 백엔드에도 추가.
- **Depends on:** Phase 1 프론트엔드 재설계

### CHECK: AI 임베딩 자동 생성 훅
- **What:** Material 생성 시 임베딩이 자동 생성되는 코드가 materials.py endpoint에 존재. AI 서비스(OpenAI/Vertex) 미연결 시 에러 가능
- **Why:** Phase 1에서 AI 검색을 비활성화하더라도 자재 등록 자체가 실패할 수 있음
- **Context:** Codex eng review에서 발견 (2026-03-25). 파일: `app/api/endpoints/materials.py:96`, `app/ai/clients/embeddings.py:195`
- **How to fix:** 임베딩 생성을 try/except로 감싸서 AI 서비스 미연결 시에도 자재 등록이 성공하도록. 또는 Phase 1에서 임베딩 훅을 비활성화.
- **Depends on:** Phase 1 백엔드 작업
