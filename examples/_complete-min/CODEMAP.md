<!-- 생성물 — 직접 편집 금지. `python3 scripts/codemap.py --root <경로>` 재실행으로 갱신한다. -->
# CODEMAP — OneLine

스펙·바인딩·진행상태를 한 장으로 요약한 네비게이션 지도. 코드를 grep하지 않고 스펙 기준으로만 만든다(드리프트 검출은 `scripts/trace.py`).

## 화면

| id | 목적 | 우선순위 | status | 바인딩 파일 |
| --- | --- | --- | --- | --- |
| home | 오늘 한 줄 메모를 보고 쓴다 | p0 | verified | `app/lib/home_screen.dart`<br>`app/lib/analytics.dart` |

## 이벤트

발화 화면은 스펙에 직접 매핑이 없어 트리거(발화 시점)로 표기한다(코드 상 실제 발화 여부는 `scripts/trace.py`가 검사).

| 이벤트 | 발화 시점(trigger) | 참조 지표 |
| --- | --- | --- |
| `app_open` | 앱 실행 | `d1_retention` |
| `note_saved` | 오늘 한 줄 메모 저장 | `daily_note_rate` |
| `reminder_permission_result` | 알림 권한 응답 | — |

## 스펙 파일 인덱스

| 파일 | 무엇인가 | 무엇을 바꿀 때 여는가 |
| --- | --- | --- |
| `spec/manifest.yaml` | 앱 정체성의 단일 원천(이름·플랫폼·수익모델·연령·리스크). | 앱 이름·대상 플랫폼·타깃 사용자·수익 모델을 바꿀 때. |
| `spec/evidence.yaml` | 왜 만드는가 — 문제·타깃·실증거·중단(kill) 기준. | 문제 정의나 '언제 접는가' 기준을 세우거나 고칠 때. |
| `spec/product.yaml` | 무엇을 만드는가 — 기능 우선순위(p0/p1)·범위 밖(out_of_scope). | 기능을 넣고 빼거나 MVP 범위를 조일 때. |
| `spec/screens.yaml` | 화면 명세 + 6상태 계약(loading/empty/error/success + 프로파일 상태). | 화면을 추가하거나 상태별 UI·문구를 정할 때. |
| `spec/events.yaml` | 분석 이벤트의 단일 원천(name·trigger·props). | 새 분석 이벤트를 추가하거나 이름·속성을 바꿀 때. |
| `spec/metrics.yaml` | 성공·성장 지표 타깃(product는 이벤트를 uses로 참조, client는 성능). | 성공 지표나 성능 목표를 세우거나 이벤트 연결을 바꿀 때. |
| `spec/monetization.yaml` | 수익화 상세(model·paid_features·pricing·paywall_trigger). | 유료 기능·가격·페이월 트리거를 정할 때(manifest와 일치해야 함). |
| `spec/architecture.yaml` | 기술 스택·계층·코드 게이트 명령(analyze/format/test). | 프레임워크·백엔드·검증 명령을 정하거나 바꿀 때. |
| `spec/compliance.yaml` | 출시 블로커·미성년자(COPPA)·개인정보 처리. | 출시 전 법적 블로커를 등록·해소하거나 연령 정책을 정할 때. |
| `spec/tokens.json` | 디자인 토큰(color/typography/spacing) + 대비 쌍 — 코드 색의 원천. | 색·타이포·간격을 바꿀 때(app/lib/tokens.dart로 반영). |

---

바인딩(화면↔파일)은 `state/bindings.yaml`에서, 진행상태는 `state/tasks.yaml`에서 온다.
