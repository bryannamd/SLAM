---
description: spec 무결성 + 코드 게이트를 실행하고 결과를 보고
---

자가 게이트(AGENTS.md §5). PASS가 아니면 완료를 주장하지 않는다.

1. `python3 scripts/validate.py`  (필요 시 `--gate launch`).
2. 코드 게이트: `flutter analyze`(무경고) · `dart format --set-exit-if-changed .` · 관련 위젯/E2E 테스트.
3. 모두 PASS면 `python3 scripts/status.py`로 대시보드 갱신.
4. 하나라도 FAIL이면 원인을 spec/ 또는 코드에서 고치고 재실행. 통과 전까지 반복.
