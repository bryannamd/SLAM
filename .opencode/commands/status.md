---
description: STATUS.md 대시보드를 갱신하고 현재 상태를 요약
---
<!-- 원본: .claude/commands/status.md — 동기 수정(두 곳을 함께 고친다) -->

1. `python3 scripts/status.py` 를 실행해 `STATUS.md`를 갱신한다(spec/·state/에서 생성).
2. STATUS.md를 읽고 사람에게 요약한다: 검증 PASS/FAIL, 화면별 진행·6상태 커버리지, blocker, 인간 승인 대기 큐.
3. 승인 대기(pending)가 있으면 가장 위에 눈에 띄게 알린다.
