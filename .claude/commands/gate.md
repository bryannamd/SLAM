---
description: 게이트 판단을 사람 승인 큐(decisions.yaml)에 올림 — 결정은 사람이 한다
argument-hint: evidence|scope|brand_ux|risk|launch
---

게이트: `$ARGUMENTS` (GATES.md 참조)

1. 해당 게이트의 전제 spec을 검증한다. launch면 `python3 scripts/validate.py --gate launch`.
2. 게이트 판단 항목을 `state/decisions.yaml`에 **pending**으로 추가한다. 형식은 짧게:
   `id / gate / decision / recommendation / alternatives / risk / impacts / reversible / status: pending`.
3. `python3 scripts/status.py`로 대시보드에 승인 대기로 노출.
4. **결정은 사람이 한다.** 에이전트는 추천안만 제시하고 승인 전까지 해당 작업을 진행하지 않는다.
