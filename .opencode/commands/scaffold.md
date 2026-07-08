---
description: 프로젝트 뼈대 생성(1/4: scaffold→build-data→build-domain→build-screen→verify)
---
<!-- 원본: .claude/commands/scaffold.md — 동기 수정(두 곳을 함께 고친다) -->

프로젝트 초기화.

1. `spec/architecture.yaml`의 `stack`(framework·language·state·local_db)을 읽는다. "TODO"가 남아있으면 먼저 `/spec fill`로 스택을 확정하고 중단한다.
2. 이미 스캐폴드가 있으면(앱 루트 디렉토리·설정 파일 존재) **중단하고 보고한다** — 덮어쓰지 않는다.
3. 프레임워크 표준 구조로 앱 뼈대를 만든다: `spec/architecture.yaml`의 `layers`(presentation→domain→data)를 반영한 디렉토리, DI, 라우팅, 테마 진입점.
4. `spec/tokens.json`에서 토큰 상수 파일을 생성한다(색·타이포·spacing·radius). hex 리터럴이 허용되는 유일한 파일이며, 이후 모든 코드는 이 상수만 참조한다.
5. 생성한 토큰 상수 파일을 `state/bindings.yaml`의 `token_sources`에 기록한다.
6. `spec/architecture.yaml`의 `commands.analyze`·`commands.format`을 실행해 스캐폴드가 clean한지 확인한다. FAIL이면 고치고 재실행.
7. 공통 규칙: 색·간격·타이포는 이 단계가 만든 토큰 상수만 사용(추가 하드코딩 금지 — trace.py가 잡는다) · PASS 아니면 다음 단계로 넘어가지 않는다 · 💰/⚖️/🎨/🚀 판단이 끼면 멈추고 `state/decisions.yaml`에 올린다(AGENTS.md §4).
