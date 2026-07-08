---
description: 도메인 유스케이스 생성(3/4: scaffold→build-data→build-domain→build-screen→verify)
---
<!-- 원본: .claude/commands/build-domain.md — 동기 수정(두 곳을 함께 고친다) -->

도메인 계층(순수 유스케이스) 생성.

1. `spec/screens.yaml`의 `acceptance`에서 화면별 유스케이스(입력→처리→출력, 순수 로직)를 도출한다.
2. `spec/architecture.yaml`의 `layers.domain`에 유스케이스·엔티티를 구현한다. presentation·data에 의존하지 않는다(의존 방향은 presentation→domain→data, 역방향 금지).
3. 각 유스케이스가 해당 화면의 acceptance를 만족하는지 유닛 테스트로 검증한다. 테스트 없는 유스케이스는 완료로 보지 않는다.
4. 생성 파일을 `state/bindings.yaml`에 기록한다. 특정 화면에 종속되면 그 화면 항목의 `files`에 추가하고, 화면 비종속 공용 코드면 `screen` 대신 `layer: domain` 항목으로 적는다.
5. `spec/architecture.yaml`의 `commands`(analyze·format·test)를 실행한다. FAIL이면 다음 단계로 넘어가지 않는다.
6. 공통 규칙: 색·간격·타이포는 scaffold가 만든 토큰 상수만 사용(하드코딩 금지 — trace.py가 잡는다) · 이벤트는 `spec/events.yaml` 이름 그대로 발화 · PASS 아니면 다음 단계로 넘어가지 않는다 · 💰/⚖️/🎨/🚀 판단이 끼면 멈추고 `state/decisions.yaml`에 올린다(AGENTS.md §4).
