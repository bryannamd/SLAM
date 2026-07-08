---
description: 데이터 계층 생성(2/4: scaffold→build-data→build-domain→build-screen→verify)
---
<!-- 원본: .claude/commands/build-data.md — 동기 수정(두 곳을 함께 고친다) -->

데이터 계층(엔티티 → 로컬 DB 스키마 · 리포지토리) 생성.

1. `spec/product.yaml`과 `spec/screens.yaml`을 읽고, 화면들이 저장·조회하는 데이터를 엔티티로 도출한다.
2. `spec/architecture.yaml`의 `stack.local_db`로 스키마와 리포지토리를 구현한다(`layers.data`).
3. 생성 파일을 `state/bindings.yaml`에 기록한다. 특정 화면에 종속되면 그 화면 항목의 `files`에 추가하고, 화면 비종속 공용 코드(공유 리포지토리 기반 클래스 등)면 `screen` 대신 `layer: data` 항목으로 적는다.
4. `spec/architecture.yaml`의 `commands`(analyze·format·test)를 실행한다. FAIL이면 다음 단계로 넘어가지 않는다.
5. 공통 규칙: 색·간격·타이포는 scaffold가 만든 토큰 상수만 사용(하드코딩 금지 — trace.py가 잡는다) · 이벤트는 `spec/events.yaml` 이름 그대로 발화 · PASS 아니면 다음 단계로 넘어가지 않는다 · 💰/⚖️/🎨/🚀 판단이 끼면 멈추고 `state/decisions.yaml`에 올린다(AGENTS.md §4).
