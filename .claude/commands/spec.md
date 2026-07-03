---
description: 스펙 점검(읽기 전용) — 부족한 필드·지금 걸린 게이트·다음 할 일을 안내
---

`AGENTS.md`의 단일 원천 규칙을 따른다(spec가 canonical, docs는 생성물).

1. `python3 scripts/validate.py` 를 실행한다.
2. FAIL이면 각 항목을 spec/의 해당 파일에서 고친다(자리표시자·6상태 누락·대비·이벤트 정합 등). PASS까지 반복.
3. PASS면 `state/tasks.yaml`·`state/decisions.yaml`을 읽고, 지금 걸린 게이트(GATES.md)와 다음 할 일을 요약한다.
4. 사람 판단이 필요한 항목은 `state/decisions.yaml`에 pending으로 올린다(혼자 결정 금지 — AGENTS.md §4).
