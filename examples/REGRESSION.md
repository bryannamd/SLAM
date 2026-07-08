# REGRESSION.md — examples/ 회귀 기대값

`scripts/validate.py`의 게이트 판정이 의도대로 동작하는지 확인하는 고정 fixture들.
게이트 로직을 고치고 나면 항상 아래 표를 재실행해서 기대값이 그대로인지 확인한다.
(음성 앵커 하나만으로는 "항상 FAIL하는 버그"를 못 잡는다 — 양성 앵커가 있어야 "항상 PASS/FAIL하는 버그" 둘 다 잡힌다.)

## 앵커 세 개

| fixture | 역할 | 무엇을 잡는가 |
|---|---|---|
| `examples/sip-reminder/` | 음성 앵커 (negative anchor) | 미완성 프로젝트인데 게이트가 잘못 PASS 해버리는 버그 |
| `examples/_complete-min/` | 양성 앵커 (positive anchor, mobile) | 완성된 모바일 프로젝트인데 게이트가 잘못 FAIL 해버리는 버그(과잉 엄격) |
| `examples/web-complete-min/` | 양성 앵커 (positive anchor, web) | 완성된 웹 프로젝트인데 게이트가 잘못 FAIL 해버리는 버그 + web 프로파일(route_404/auth_required, lcp 등) 분기 자체가 깨지는 회귀 |

`sip-reminder`는 의도적으로 미완성 상태로 남겨둔다(화면 4개 중 verified 1개, pending 결정 1건,
in_progress/todo/blocked 화면 존재) — **수정 대상이 아니다.** `_complete-min`은 화면 1개(home)를
spec 10파일 + state 3파일 + 최소 실제 소스(`app/lib/`)까지 전부 완비해 "출시해도 되는 최소 앱"을
흉내낸다(모바일 프로파일). `web-complete-min`은 화면 2개(bookmarks, tags)를 spec 10파일 + state
3파일 + 최소 실제 소스(`app/src/`, TypeScript/React)까지 전부 완비한 web 프로파일 대응물이다 —
`platform_profile: web`이라 상태 계약이 `route_404`/`auth_required`로 바뀌고, `deploy_target:
web_host`, client 지표에 `lcp`/`cls` 등 Core Web Vitals가 들어간다.

## 실행 명령과 기대값

| 명령 | 기대 RESULT | 기대 exit code |
|---|---|---|
| `python3 scripts/validate.py --root examples/_complete-min` | `PASS` (warn 0) | 0 |
| `python3 scripts/validate.py --root examples/_complete-min --gate launch` | `PASS` | 0 |
| `python3 scripts/validate.py --root examples/web-complete-min` | `PASS` (warn 0) | 0 |
| `python3 scripts/validate.py --root examples/web-complete-min --gate launch` | `PASS` | 0 |
| `python3 scripts/trace.py --root examples/web-complete-min` | `CLEAN` | 0 |
| `python3 scripts/validate.py --root examples/sip-reminder` | `PASS(+warn)` | 0 |
| `python3 scripts/validate.py --root examples/sip-reminder --gate launch` | `FAIL` | 1 |
| `python3 scripts/status.py --root examples/_complete-min` | `STATUS.md` 생성, 본문에 `✅ PASS` | — |
| `python3 scripts/status.py --root examples/web-complete-min` | `STATUS.md` 생성, 본문에 `✅ PASS` | — |
| `python3 scripts/status.py --root examples/sip-reminder` | `STATUS.md` 생성, 본문에 `✅ PASS(+warn)`(전역 검증 기준) | — |

`sip-reminder`의 전역 검증(`--gate` 없이)은 PASS(+warn)를 유지한다 — warn은 있지만 FAIL은 아니다.
FAIL은 `--gate launch`에서만 발생해야 한다(미완성 화면·pending 결정 때문). 전역 검증까지 FAIL로
바뀌면 그것 자체가 회귀다.

## 정직성 caveat — code_gates:PASS의 의미

`examples/_complete-min/state/tasks.yaml`의 `verify_evidence.code_gates: PASS`는 **이 저장소에서
`flutter analyze` / `dart format` / `flutter test`를 실제로 실행해 얻은 결과가 아니다.** 이 fixture는
`spec/architecture.yaml`의 `commands`를 채우기 위한 최소 예시일 뿐, 완전한 Flutter 프로젝트
(`pubspec.yaml`, 의존성, `flutter pub get`)를 갖추고 있지 않다 — `app/lib/`은 스펙-코드 정합성을
보여주기 위한 **소스 구조 샘플**이다.

실제로 확인한 것은 `dart format --output=none --set-exit-if-changed app/lib`(구문 유효성, exit 0)
뿐이다. `flutter analyze`/`flutter test`는 이 fixture 범위 밖이다(패키지 해석에 실제 Flutter
프로젝트 셋업이 필요). 따라서 `verify_evidence.code_gates: PASS`는 "이 화면을 verified로 전환하는
verifier 패스가 있었다고 가정한 기록값"으로 읽어야 하며, launch 게이트가 이 필드의 **존재와 값**만
검사하고 실제 툴체인을 재실행하지 않는다는 `AGENTS.md §5`의 한계(커널은 code_gates를 신뢰만 하고
재검증하지 않는다)를 그대로 반영한다.

`examples/web-complete-min/state/tasks.yaml`의 `verify_evidence.code_gates: PASS`도 같은 한계를
공유한다 — `app/src/`는 `pubspec.yaml` 상당의 완전한 프로젝트 셋업(`package.json`의 빌드 스크립트,
번들러 설정, 실제 `vitest` 테스트 파일)을 갖추지 않은 **소스 구조 샘플**이다. 다만 이쪽은 mobile
fixture보다 한 단계 더 실제로 검증했다: 임시 디렉터리에 `typescript`·`@types/react`·`prettier`를
`npm install`로 내려받아 `tsc --noEmit`(strict, jsx: react-jsx)과 `prettier --check`을 **네 파일
전부에 대해 실제로 실행**해 exit 0을 확인했다(타입 오류 없음, 포맷 이슈 없음 — 발견된 포맷 이슈는
`prettier --write`로 실제 반영). `architecture.yaml`의 `test: "vitest run"`은 테스트 파일 자체가
없어 실행하지 않았다 — 그 부분만 mobile fixture와 동일한 "기록값" caveat이 적용된다.
