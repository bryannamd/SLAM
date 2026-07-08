---
description: screens.yaml의 화면 하나를 6상태로 구현 → 검증 → tasks 갱신(4/4, 화면별 반복. scaffold→build-data→build-domain→build-screen→verify)
argument-hint: <screen-id>
---
<!-- 원본: .claude/commands/build-screen.md — 동기 수정(두 곳을 함께 고친다) -->

대상 화면: `$ARGUMENTS`

1. `spec/screens.yaml`에서 해당 id의 states(6종, na 포함)·acceptance를 읽고, `spec/tokens.json`·`spec/product.yaml`을 참조한다.
2. 6상태를 모두 구현한다. na로 표시된 상태는 만들지 않는다. **토큰 하드코딩 금지** — scaffold가 만든 토큰 상수만 사용.
3. 위젯/E2E 테스트로 acceptance를 만족시킨다. 이벤트는 `spec/events.yaml` 이름 그대로 발화한다.
4. `python3 scripts/validate.py` + 코드 게이트가 PASS인지 확인. 코드 게이트는 `spec/architecture.yaml`의 `commands`(analyze·format·test — 예: Flutter면 `flutter analyze` 무경고·`dart format`). FAIL이면 다음으로 넘어가지 않는다.
5. 구현한 파일을 `state/bindings.yaml`의 해당 화면(`screen: <id>`) 항목의 `files`에 기록한다.
6. (advisory) `python3 scripts/trace.py` 실행 — 스펙↔코드 드리프트 lint. warn은 보고만 하고 블로킹하지 않는다.
7. `state/tasks.yaml`의 해당 화면 status를 `built`로 갱신하고 `python3 scripts/status.py` 실행. **`verified`로는 올리지 않는다** — 별도 verifier 패스가 validate PASS + 코드 게이트 PASS를 확인하고 `verify_evidence`와 함께 전환한다(AGENTS.md §5).
8. 💰/⚖️/🚀/브랜드 판단이 끼면 멈추고 `state/decisions.yaml`에 올린다(AGENTS.md §4).
