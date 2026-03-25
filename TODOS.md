# TODOS

## Phase 1 MVP (당근마켓 for B2B) — 구현 시 필수 확인

### ~~BUG: MaterialStatus enum 불일치~~ ✅ DONE
- **해결:** 백엔드에 RESERVED 상태 추가 완료 (2026-03-26). 프론트엔드는 재설계 시 통일 예정.

### ~~CHECK: AI 임베딩 자동 생성 훅~~ ✅ NOT AN ISSUE
- **확인 결과:** embedding_hook.py가 이미 try/except로 감싸져 있고 background task로 실행. AI 서비스 미연결 시에도 자재 등록은 성공함.

## Phase 1 — 남은 작업

### TODO: 프론트엔드 당근마켓 UX 재설계
- **What:** 홈 피드(2열 그리드), 자재 상세, 채팅, 프로필 4개 화면 재설계
- **Context:** 디자인 명세 완료 (색상 #2563EB, lazy auth, 빈 상태 등). 디자인 문서: `~/.gstack/projects/goopy-priv-surplus-hub/jeongseongchae-main-design-20260325-161255.md`

### TODO: 카테고리 시드 데이터 업종별 재구성
- **What:** 기존 카테고리를 업종별(조명/문/건자재/전기/설비)로 재구성
