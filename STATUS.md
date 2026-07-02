# STATUS — SipReminder

> 바쁜 직장인이 물 마시는 습관을 잊지 않도록 부드럽게 알려준다

> ⚙️ 이 파일은 `scripts/status.py`가 생성한다. 직접 편집하지 말 것(spec/·state/를 고친다).

- 플랫폼: ios, android | backend: False | audience: general | risk: low | 수익: freemium
- 검증: ✅ PASS  (`RESULT: PASS`)

## 화면 진행

| 화면 | 우선 | 상태 | 6상태(구현/NA) | blocker |
|---|---|---|---|---|
| onboarding | p0 | ✅ 검증 | 3/3 | — |
| home | p0 | 🔨 진행 | 5/1 | — |
| stats | p1 | ⬜ todo | 4/2 | — |
| settings | p1 | ⛔ 막힘 | 3/3 | 광고 제거 IAP 상품 등록 대기(스토어 콘솔) |

## 인간 승인 대기 (1)

- **[risk] D002 — 광고 제거 IAP(비소비성) 도입**
  - 추천: 도입 — 아동 대상 아님, 광고 대신 1회 구매가 신뢰에 유리
  - 리스크: 중간(스토어 IAP 정책·정산 세팅 필요) | 되돌리기: True | 영향: monetization.yaml, compliance.yaml

