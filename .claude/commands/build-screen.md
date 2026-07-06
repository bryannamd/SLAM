---
description: screens.yaml의 화면 하나를 6상태로 구현 → 검증 → tasks 갱신
argument-hint: <screen-id>
---

대상 화면: `$ARGUMENTS`

1. `spec/screens.yaml`에서 해당 id의 states(6종, na 포함)·acceptance를 읽고, `spec/tokens.json`·`spec/product.yaml`을 참조한다.
2. 6상태를 모두 구현한다. na로 표시된 상태는 만들지 않는다. **토큰 하드코딩 금지** — tokens.json에서 생성된 값만 사용.
3. 위젯/E2E 테스트로 acceptance를 만족시킨다.
4. `python3 scripts/validate.py` + 코드 게이트가 PASS인지 확인. 코드 게이트는 `spec/architecture.yaml`의 `commands`(analyze·format·test — 예: Flutter면 `flutter analyze` 무경고·`dart format`). FAIL이면 다음으로 넘어가지 않는다.
5. `state/tasks.yaml`의 해당 화면 status를 `built`→검증 통과 시 `verified`로 갱신하고 `python3 scripts/status.py` 실행.
6. 💰/⚖️/🚀/브랜드 판단이 끼면 멈추고 `state/decisions.yaml`에 올린다(AGENTS.md §4).
