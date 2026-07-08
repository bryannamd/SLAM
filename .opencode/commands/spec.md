---
description: 스펙 점검(읽기 전용) 또는 대화형 인테이크로 채우기 — 인자 없음은 진단, `fill`은 질문하며 값을 대신 기입
argument-hint: [fill]
---
<!-- 원본: .claude/commands/spec.md — 동기 수정(두 곳을 함께 고친다) -->

`AGENTS.md`의 단일 원천 규칙을 따른다(spec가 canonical, docs는 생성물).

## 모드

- `/spec` (인자 없음) — **읽기 전용 진단.** spec 파일을 고치지 않는다.
- `/spec fill` — **대화형 인테이크.** 진단 후 FAIL 목록을 질문으로 바꿔 하나씩 채운다.

## 1. 진단 (두 모드 공통, 항상 먼저 실행)

1. `python3 scripts/validate.py` 를 실행한다.
2. PASS면 `state/tasks.yaml`·`state/decisions.yaml`을 읽고 지금 걸린 게이트(GATES.md)와 다음 할 일을 요약한다. `fill` 모드였다면 "더 채울 것 없음 — validate PASS"를 안내하고 종료.
3. FAIL이면 항목을 게이트 순서로 정렬한다: manifest → evidence → product/screens → tokens → architecture → events/metrics/monetization/compliance.
   - **`/spec`(기본)** 이면 정렬된 FAIL 목록만 안내하고 "`/spec fill`로 대화하며 채울 수 있다"고 제안한 뒤 멈춘다. spec 파일을 고치지 않는다.
   - **`/spec fill`** 이면 아래 "인테이크 루프"로 들어간다.

## 2. 인테이크 루프 (`fill` 전용)

- 한 번에 **AskUserQuestion 1회, 질문 1~2개**만. YAML 필드명이 아니라 사람 언어로 묻는다(예: "features.p0는?"이 아니라 "이 앱이 첫 실행에서 반드시 되는 기능, 5개 이하로 뭐가 있나요?"). 선택지 2~4개 + 직접 입력을 함께 제공.
- 답을 받으면 해당 spec 파일의 TODO를 그 값으로 직접 교체한다. **파일 경로·YAML 문법은 먼저 노출하지 않는다**(물어보면 알려준다).
- 하나 고치면 바로 `python3 scripts/validate.py`를 재실행해 다음 FAIL로 넘어간다. 여러 필드를 한 번에 몰아서 묻지 않는다.
- **evidence(실증거 2종·kill 기준)는 지어내지 않는다.** 사용자가 증거를 못 대면 조사 숙제(예: "경쟁앱 리뷰 3개 링크를 찾아달라")를 제안하거나, 에이전트가 직접 조사한 뒤 결과를 사용자에게 보여주고 확인받아 기입한다.
- **Evidence 게이트** 도달(evidence.yaml 완료) 시 `python3 scripts/validate.py --gate evidence`를 실행한다. PASS면 `state/decisions.yaml`에 decision 항목을 pending으로 올리고 **멈춰서 사람 승인을 기다린다**(GATES.md 계약 — 혼자 다음으로 넘어가지 않는다).
- **Scope 게이트** 도달(product.yaml·screens.yaml·metrics.yaml 완료) 시 동일하게 `--gate scope` PASS → decisions.yaml에 올리고 멈춘다.
- 두 게이트 다 approved 상태가 돼야 tokens/architecture 이후 항목을 계속 채운다. 승인 대기 중 뒤 항목을 미리 채워두는 것은 괜찮지만 게이트 자체는 건너뛰지 않는다.

## 3. 질문 흐름 가이드 (빈 템플릿 → Evidence+Scope PASS)

대략 8~12문항. 실제 흐름은 답변에 따라 달라진다 — 이 표는 길을 잃지 않기 위한 가이드레일이다.

| # | 묻는 것 (사람 언어) | 채우는 파일 |
|---|---|---|
| 1 | 이 앱을 한 줄로 하면? 이름은? 모바일 앱인가요 웹인가요(둘 다?) | `manifest.yaml`(name, one_liner, platform_profile) |
| 2 | 누구의 어떤 문제를 풀어주나요? | `evidence.yaml`(problem, target_user) |
| 3 | 사람들이 이 앱을 어디서 찾게 되나요? | `evidence.yaml`(acquisition_channel) |
| 4 | 그 문제가 실제로 있다는 증거(리뷰·검색량·인터뷰 등) 2가지는? | `evidence.yaml`(evidence) |
| 5 | 언제 이 앱을 접어야 할까요(kill 기준)? | `evidence.yaml`(kill_criteria) |
| ⏸ | **Evidence 게이트** — `--gate evidence` PASS → decisions.yaml → 사람 승인 대기 | — |
| 6 | 첫 버전에 반드시 있어야 할 기능, 5개 이하로는? | `product.yaml`(features.p0) |
| 7 | 이번엔 일부러 안 만드는 건 뭔가요? | `product.yaml`(out_of_scope) |
| 8 | 화면은 몇 개, 각각 뭘 하나요? | `screens.yaml` |
| 9 | 돈은 어떻게 버나요(무료/구독/광고 등)? | `manifest.yaml`(monetization_model), `monetization.yaml` |
| ⏸ | **Scope 게이트** — `--gate scope` PASS → decisions.yaml → 사람 승인 대기 | — |
| 10 | 색·느낌은 어떤 방향으로? (기본 팔레트 유지 가능) | `tokens.json` |
| 11 | 기술 스택은? (모르면 기본 추천값 사용) | `architecture.yaml` |
| 12 | 핵심 지표(리텐션 등)와 이벤트는? | `events.yaml`, `metrics.yaml` |

## 4. 공통 규칙

사람 판단이 필요한 항목(evidence/scope 게이트 포함)은 `state/decisions.yaml`에 pending으로 올린다(혼자 결정 금지 — AGENTS.md §4).
