# GATES — 인간 판단 지점 (5개)

> **원칙:** 자율 파이프라인이 안전하려면, AI가 혼자 결정하면 안 되는 딱 5곳에서만 사람이 멈춰 판단한다.
> 그 밖은 전부 자율. 게이트 판단은 `state/decisions.yaml`에 올라오고, 승인/반려 결과가 STATUS.md에 뜬다.
> 서명식·대면 심사 없음 — 결정은 decisions.yaml에 1줄(`decided_by`, `date`, `status`)로 기록.

각 게이트는 codex·agy 교차검증에서 합의된 최소 집합. 무엇을 자동화하고 무엇을 사람이 잡을지의 경계다.
게이트 ①②③⑤는 기계 검사가 먼저 돈다: `python3 scripts/validate.py --gate evidence|scope|brand_ux|launch`.

---

## GATE #1 — Evidence (빌드 전, 가장 중요)
**자율 파이프라인 최대 위험 = "그럴듯하지만 아무도 원하지 않는 앱" 양산.** 코딩 전에 죽일 건 죽인다.

전제: `spec/evidence.yaml` 작성 + `validate.py --gate evidence` PASS.
- 타깃 사용자 1 · 핵심 pain 1 · 유입 채널 1 · 지불/재방문 가설 1 — 채워졌는가?
- **실제 증거** 2종 이상(경쟁앱 리뷰·키워드·랜딩·실인터뷰)인가? (가상 페르소나 인정 안 함)
- kill 기준에 하나라도 해당하지 않는가?

`--gate evidence`가 증거 2종 미만·필수 필드 공백·kill_criteria 부재를 FAIL로 잡는다. → PASS 후 product/screens 작성.

## GATE #2 — Scope
전제: `spec/product.yaml`·`screens.yaml`·`metrics.yaml` + `validate.py --gate scope` PASS.
- MVP 범위·핵심 flow·제외 범위 합의됐는가? (`--gate scope`가 p0 5개 초과·out_of_scope 공백을 FAIL로 잡는다)
- 수익 가설(`monetization.yaml`)이 범위와 맞는가? (유료 모델이면 pricing·paid_features 필수 — validate가 검사)
- 2인팀이 합리적 기간에 만들 수 있는가?

→ PASS 후 tokens/architecture 확정, 구현 시작.

## GATE #3 — Brand / UX
전제: `spec/tokens.json` 확정 + `validate.py --gate brand_ux` PASS + 핵심 화면 3개의 에이전트 생성 스크린샷/클릭스루.
- 시각 방향·톤·민감한 카피가 브랜드에 맞는가?
- 디자인 시스템이 뭉개지지 않고 일관 적용됐는가?
- 대비(WCAG AA) PASS인가? 터치 타겟·접근성은?

사람이 스크린샷을 보고 "사람이 쓸 만한가"를 판단. → PASS 후 나머지 화면 자율 구현.

## GATE #4 — Risk
`manifest.risk_class`가 medium/high이거나 아래 항목이 생길 때마다 발동(decisions.yaml).
- 💰 결제/IAP·광고·구독·유료 마케팅·외부 유료 API(비용)
- ⚖️ 미성년/COPPA·개인정보 수집·권한 추가·OAuth
- 🚀 production 데이터 변경 등 되돌리기 어려운 작업

사람이 "스토어 계정이 날아가거나 법/비용 사고가 없는가"를 판단. 승인 전 자동 실행하지 않는다.

## GATE #5 — Launch
전제: `validate.py --gate launch` PASS — 출시 블로커 0 + 미성년 규제 충족 + **모든 화면 verified(verify_evidence: PASS·by·date 포함) 또는 launch_scope 제외 명시(단 p0 화면은 제외 불가·출시 범위에 verified 화면 1개 이상) + 모든 게이트 pending 결정 0 + launch 승인 결정(gate:launch·approved) 실존**. 스테이징 무결성.
- crash-free > 99.5% · P0 0건 · P1 2건 이하(수정계획)
- `metrics.client` 목표 충족(모바일=cold_start 등 · 웹=lcp 등 Core Web Vitals)
- 실기기/실브라우저 10분 탐색 QA에서 크래시·치명 오류 없음
- 배포 준비물 완성 — `manifest.deploy_target` 기준:
  - `app_store`: 스토어 자료·심사 대응·정산 세팅 완료
  - `web_host`: 도메인·호스팅·SEO 기본(메타/robots/sitemap)·과금 설정 완료
  - `both`: 위 둘 다

사람이 최종 GO/NO-GO. → GO는 decisions.yaml에 launch 결정 approved로 기록돼야 배포된다.

---

### 출시 후 폐루프 (게이트는 아니지만 필수)
출시가 끝이 아니다. 에이전트의 build target은 "동작하는 코드"가 아니라 **`metrics.yaml` 지표 개선**이다.
실측값은 `metrics.yaml`의 `actual`에 기입 — `STATUS.md` 지표 표에 목표와 나란히 뜬다.
지표가 목표 미달이면 에이전트가 로그로 실패 가설을 세우고 spec을 고쳐 개선 패치를 제안한다
(배포 자체는 GATE #5로 다시 사람 승인). 이것이 좀비 앱을 막는 최고 레버리지다.
