---
description: 완료 게이트 — 스펙 무결성 + 코드 검사(analyze/format/test)까지 통과 확인
---
<!-- 원본: .claude/commands/verify.md — 동기 수정(두 곳을 함께 고친다) -->

자가 게이트(AGENTS.md §5). PASS가 아니면 완료를 주장하지 않는다.

1. `python3 scripts/validate.py`  (게이트 단계면 `--gate evidence|scope|brand_ux|launch`).
2. 코드 게이트: `spec/architecture.yaml`의 `commands`(analyze·format·test)를 실행.
   예: Flutter면 `flutter analyze`(무경고) · `dart format --set-exit-if-changed .` · 관련 위젯/E2E 테스트.
3. 모두 PASS면 `python3 scripts/status.py`로 대시보드 갱신.
4. 하나라도 FAIL이면 원인을 spec/ 또는 코드에서 고치고 재실행. 통과 전까지 반복.
5. (advisory) `python3 scripts/trace.py` 실행 — 스펙↔코드 드리프트 lint. warn은 보고만 하고 블로킹하지 않는다(정규식 수준 검출이라 게임 가능 — 참고 신호일 뿐 게이트 아님).
