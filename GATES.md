# GATES — 사람이 판단하는 5곳

> AI는 대부분을 알아서 합니다. 하지만 **돈·법·브랜드·되돌리기 어려운 일** 딱 5곳에서는 멈춰 사람에게 물어봅니다.
> 나머지는 전부 자율. 이 5곳이 "AI가 혼자 결정하면 안 되는 경계"입니다.

승인은 어렵지 않습니다. 서명식도, 회의도 없습니다. 대기 항목이 `state/decisions.yaml`에 한 줄로 올라오고, 사람이 `status`를 `approved` 또는 `rejected`로 바꾸면 끝입니다. 결과는 `STATUS.md` 대시보드에 뜹니다.

---

## 한눈에 보기

| # | 게이트 | 언제 | 무엇을 판단하나 | 기계 검사 |
|---|---|---|---|---|
| 1 | **Evidence** | 코딩 시작 전 | 이 앱을 만들 근거가 있나 | `--gate evidence` |
| 2 | **Scope** | 구현 시작 전 | MVP 범위 · 수익 가설이 맞나 | `--gate scope` |
| 3 | **Brand/UX** | 핵심 화면 완성 후 | 시각 방향 · 톤 · 첫인상이 괜찮나 | `--gate brand_ux` |
| 4 | **Risk** | 위험이 생길 때마다 | 돈·법·되돌리기 어려운 작업이 안전한가 | 전용 검사 없음 |
| 5 | **Launch** | 배포 직전 | 진짜 내보내도 되나 | `--gate launch` |

게이트 1·2·3·5는 사람이 보기 전에 기계 검사가 먼저 돕니다: `python3 scripts/validate.py --gate <이름>`.
Risk는 전용 기계 검사가 없는 사람 판단입니다(`--gate risk` 이름은 받아주지만 전역 spec 검증만 돕니다).

---

## GATE 1 — Evidence (가장 중요)

**AI 자율 파이프라인의 가장 큰 위험은 "그럴듯하지만 아무도 원하지 않는 앱"을 찍어내는 것입니다.** 그래서 코딩 전에 접을 건 접습니다.

준비물: `spec/evidence.yaml` 작성 + `validate.py --gate evidence` PASS.

사람이 확인할 것:
- 타깃 사용자 1명 · 핵심 pain 1개 · 유입 채널 1개 · 지불/재방문 가설 1개 — 다 채웠나?
- **실제 증거가 2종 이상**인가? (경쟁앱 리뷰 · 검색 키워드 · 랜딩 반응 · 실제 인터뷰 — 상상 속 페르소나는 인정 안 함)
- 접는 기준(kill criteria)에 걸리는 게 없나?

`--gate evidence`가 증거 2종 미만 · 필수 필드 공백 · 접는 기준 누락을 FAIL로 잡습니다.
→ PASS 후 `product`·`screens` 작성으로.

---

## GATE 2 — Scope

준비물: `spec/product.yaml` · `screens.yaml` · `metrics.yaml` + `validate.py --gate scope` PASS.

사람이 확인할 것:
- MVP 범위 · 핵심 흐름 · 뺄 것을 합의했나? (`--gate scope`가 p0 기능이 비었거나 5개 초과 · 뺄 범위 공백을 FAIL로 잡음)
- 수익 가설(`monetization.yaml`)이 범위와 맞나? (유료 모델이면 가격 · 유료 기능이 필수 — validate가 검사)
- 1~2인 팀이 무리 없는 기간에 만들 수 있나?

→ PASS 후 `tokens`·`architecture` 확정, 구현 시작.

---

## GATE 3 — Brand / UX

준비물: `spec/tokens.json` 확정 + `validate.py --gate brand_ux` PASS + 핵심 화면 3개의 스크린샷/클릭스루.

사람이 확인할 것:
- 시각 방향 · 톤 · 민감한 문구가 브랜드에 맞나?
- 디자인 시스템이 뭉개지지 않고 일관되게 적용됐나?
- 색 대비(WCAG AA)를 통과하나? 터치 타겟 · 접근성은?

여기서는 사람이 실제 화면을 눈으로 보고 "사람이 쓸 만한가"를 판단합니다.
→ PASS 후 나머지 화면은 AI가 자율로 구현.

---

## GATE 4 — Risk

`manifest.risk_class`가 medium/high이거나, 아래 항목이 생길 때마다 발동합니다(`decisions.yaml`에 올라옴).

- 💰 **돈** — 결제/IAP · 광고 · 구독 · 유료 마케팅 · 비용 드는 외부 API
- ⚖️ **법** — 미성년/COPPA · 개인정보 수집 · 권한 추가 · OAuth
- 🚀 **되돌리기 어려움** — production 데이터 변경 등

사람이 "스토어 계정이 날아가거나 법·비용 사고가 날 여지는 없나"를 판단합니다. 승인 전에는 자동 실행하지 않습니다.

---

## GATE 5 — Launch

준비물: `validate.py --gate launch` PASS. 이 검사는 아래를 전부 요구합니다.

- 출시 블로커 0개 (`compliance.yaml`의 미해소 블로커 없음)
- 미성년 대상이면 COPPA 등 규제 충족
- **모든 화면이 검증 완료(verified)** — 검증 기록(`verify_evidence`: `validate`·`code_gates` 둘 다 PASS · 담당자 · 날짜) 포함
  - 출시 범위에서 뺀 화면은 `launch_scope: false` + 사유 명시 (단, p0 핵심 화면은 뺄 수 없음)
  - 출시 범위에 검증된 화면이 최소 1개는 있어야 함
- 대기 중(pending)인 결정이 0개
- 출시 승인 결정(`gate: launch` · `approved`)이 실제로 기록돼 있음

사람이 최종 확인할 것:
- crash-free > 99.5% · 심각 버그(P0) 0건 · 중간 버그(P1) 2건 이하(수정 계획 포함)
- 성능 지표 충족 (모바일=cold_start 등 · 웹=LCP 등 Core Web Vitals)
- 실기기/실브라우저에서 10분 탐색 QA — 크래시·치명 오류 없음
- 배포 준비물 완성 (`manifest.deploy_target` 기준)
  - `app_store`: 스토어 자료 · 심사 대응 · 정산 세팅
  - `web_host`: 도메인 · 호스팅 · SEO 기본(메타/robots/sitemap) · 과금 설정
  - `both`: 둘 다

사람이 최종 GO/NO-GO를 냅니다. GO는 `decisions.yaml`에 launch 결정이 `approved`로 기록돼야 배포로 이어집니다.

---

## 출시가 끝이 아니다 — 지표 폐루프

게이트는 아니지만 핵심입니다. AI의 목표는 "동작하는 코드"가 아니라 **`metrics.yaml` 지표 개선**입니다.

실측값은 `metrics.yaml`의 `actual`에 기입합니다 — `STATUS.md` 지표 표에 목표와 나란히 뜹니다.
지표가 목표에 못 미치면 AI가 로그로 실패 가설을 세우고, spec을 고쳐 개선안을 제안합니다(배포 자체는 다시 GATE 5로 사람 승인). 이것이 "좀비 앱"을 막는 가장 큰 레버리지입니다.

---

> 이 5개 게이트는 codex · agy 교차검증에서 합의된 최소 집합입니다. 무엇을 자동화하고 무엇을 사람이 붙잡을지의 경계입니다.
> 운영 규칙 전체는 `AGENTS.md`, 전체 흐름은 `README.md`를 보세요.
