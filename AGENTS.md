# AGENTS.md — 에이전트 운영 계약

> 사람이 프롬프트를 붙여넣는 안내서가 아니다. **자율 에이전트가 따르는 계약**이다.
> 무엇을 읽고, 무엇을 갱신하고, 어떤 검증을 통과해야 다음 단계로 가는지를 기계적으로 닫는다.
> Claude Code / opencode 어디서 돌든 동일 적용.

## 1. 단일 원천 규칙 (가장 중요)

- **`spec/*.yaml|json`이 canonical**(실행 가능한 사실). 에이전트는 여기를 읽고, 여기만 고친다.
- **`docs/`·`STATUS.md`는 생성물/설명.** 사람도 STATUS를 편집하지 않는다 — spec/state를 고친다.
- 같은 사실을 두 곳에 쓰지 않는다(드리프트 원인). 지표=metrics, 이벤트=events, 토큰=tokens, 화면=screens.

## 2. 에이전트–문서 소유권 (read/write)

| 산출물 | 주 담당 | write | read |
|---|---|---|---|
| `spec/evidence.yaml` | product | 기획 에이전트 | 전원 |
| `spec/product.yaml`, `screens.yaml` | product | 기획/UX 에이전트 | 전원 |
| `spec/tokens.json` | design | 디자인 에이전트 | 구현 |
| `spec/architecture.yaml` | eng | 설계 에이전트 | 구현 |
| `spec/events.yaml`, `metrics.yaml` | product+eng | 분석 에이전트 | 전원 |
| `spec/monetization.yaml`, `compliance.yaml` | product | 수익/규제 에이전트 | 전원 |
| `state/tasks.yaml` | eng | 구현/검증 에이전트 | 전원 |
| `state/decisions.yaml` | — | **아무 에이전트나 올리되 결정은 사람만** | 전원 |
| 코드 | eng | 구현 에이전트 | — |

## 3. 실행 루프 (화면 1개 단위)

```
계획 → 구현 → 자가검증 → (게이트) → 다음
```

1. **계획**: `screens.yaml`의 대상 화면 + `tokens.json` + `product.yaml`을 읽는다.
2. **구현**: 6상태(또는 명시적 na) 전부. 토큰 하드코딩 없이 — `tokens.json`에서 생성된 값만.
3. **자가검증**: `python3 scripts/validate.py` **PASS** 필수. 해당 화면 E2E/위젯 테스트까지.
   - `state/tasks.yaml`의 화면 status를 `built` → 검증 통과 시 `verified`로 갱신.
4. **대시보드**: `python3 scripts/status.py`로 STATUS.md 갱신.
5. **게이트**: GATES.md의 게이트가 걸리면 `state/decisions.yaml`에 올리고 **멈춘다**(§4).

## 4. 에이전트가 혼자 결정하면 안 되는 것 (→ decisions.yaml 큐)

아래는 자동 진행하지 않는다. `state/decisions.yaml`에 `pending`으로 올리고 사람 승인을 기다린다.
큐 항목은 짧게: `decision / recommendation / alternatives / risk / impacts / reversible`.

- 💰 돈: 가격·구독·IAP·광고 도입, 유료 마케팅 시작, 외부 유료 API 도입(비용 발생)
- ⚖️ 법: 개인정보 수집 범위 변경, 미성년/COPPA, 권한 추가, 약관/방침 변경
- 🎨 브랜드: 시각 방향·톤·민감한 카피·스토어 첫인상
- 🚀 되돌리기 어려움: 실제 배포, 스토어 제출, 푸시 발송, production 데이터 변경, 계정/OAuth
- 🧭 방향: 이 앱을 만들지(Evidence), MVP 범위(Scope)

그 밖(화면 구현·리팩터·테스트·문서 생성·spec 값 초안)은 **자율 진행**.

## 5. 검증 계약 (자가 게이트)

- `validate.py` PASS = spec 무결성(자리표시자·6상태·대비·이벤트 정합·수익 필드·블로커).
- 게이트별 강제: `--gate evidence`(증거 2종·필수 필드) · `--gate scope`(p0≤5·out_of_scope) · `--gate brand_ux`(대비 쌍) · `--gate launch`(블로커 0 + 미성년 규제 + launch 승인).
- 코드 게이트(매 화면): `architecture.yaml`의 `commands`(analyze·format·test)를 돌린다.
  예: Flutter면 `flutter analyze` 무경고 · `dart format` · 위젯/E2E. React Native면 lint·typecheck·test.
- **PASS 아니면 다음 화면으로 넘어가지 않는다.** 그럴듯한 미완성 코드로 진행하지 않는다.

## 6. 코드 출력 기준 (spec 준수 체크)

- `tokens.json` 값만 사용(색·간격·타이포 하드코딩 없이) · 6상태 구현 · 접근성 label · 입력 검증
- 비밀값 하드코딩 없이 · 에러 삼키지 않기(로깅+사용자 안내) · presentation→domain→data 의존 방향
