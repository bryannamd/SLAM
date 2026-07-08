# STATUS — LinkBox

> 로그인 없이 브라우저에 저장해 태그로 찾는 가장 가벼운 북마크 정리 웹앱

> ⚙️ 이 파일은 `scripts/status.py`가 생성한다. 직접 편집하지 말 것(spec/·state/를 고친다).

- 플랫폼: web | backend: False | audience: general | risk: low | 수익: free
- 검증: ✅ PASS  (`RESULT: PASS`)

## 화면 진행

| 화면 | 우선 | 상태 | 6상태(구현/NA) | blocker |
|---|---|---|---|---|
| bookmarks | p0 | ✅ 검증 | 5/1 | — |
| tags | p1 | ✅ 검증 | 4/2 | — |

## 지표 타겟

| 지표 | 구분 | 목표 | 실측 |
|---|---|---|---|
| bookmarks_per_active_user | product | 10개+/월 | — |
| tag_filter_usage_rate | product | 40%+ | — |
| lcp | client | < 2.5s | — |
| cls | client | < 0.1 | — |
| local_storage_write | client | < 10ms (북마크 1건 저장) | — |

## 인간 승인 대기 (0)

_대기 중인 결정 없음._

