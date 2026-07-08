# SLAM

**S**pec-driven · **L**ess-prompt · **A**pp · **M**aker

> 스펙을 새기면, 프롬프트 없이 앱이 나온다.
> Build company-grade apps from specs, with less prompting.

SLAM = 1~2인 팀이 AI 코딩 에이전트로 완성도·수익성 높은 앱을 자율로 만드는 보일러플레이트.
모바일·웹 둘 다 1급이다(`platform_profile`로 갈린다). 긴 기획서를 매번 프롬프트로 붙여넣지 않는다.
`spec/` 폴더 YAML이 **단 하나의 사실(canonical)** — 에이전트가 읽고, 채우고, 검증한다.
사람은 돈·법·브랜드·되돌리기 어려운 일이 걸린 **5개 게이트에서만** 판단한다.

Claude Code, opencode 같은 에이전트 런타임 어디서든 돈다. 여기서 "UI"는 화면이 아니라 **슬래시 명령 + 자동 생성 `STATUS.md` 대시보드**다.

---

## 필요한 것

- **Python 3** + **PyYAML** — 검증·대시보드 스크립트용
- (선택) **Claude Code** 또는 **opencode** — 슬래시 명령(`/spec` 등)용. 없어도 아래 python 명령으로 전부 대체된다.

```bash
git clone https://github.com/bryannamd/SLAM.git
cd SLAM
python3 -m pip install pyyaml
# 최신 macOS 등에서 "externally-managed-environment" 오류가 나면 가상환경:
#   python3 -m venv .venv && source .venv/bin/activate && pip install pyyaml
```

---

## 60초 체험 — 먼저 돌려본다

저장소에 **완성 앵커** 두 개가 들어 있다: `examples/_complete-min`(모바일, Flutter)과 `examples/web-complete-min`(웹, TypeScript/React). 둘 다 출시 게이트까지 통과한다.

```bash
# 모바일 완성 앵커 → RESULT: PASS
python3 scripts/validate.py --root examples/_complete-min
python3 scripts/validate.py --root examples/_complete-min --gate launch    # PASS

# 웹 완성 앵커 → RESULT: PASS
python3 scripts/validate.py --root examples/web-complete-min
python3 scripts/validate.py --root examples/web-complete-min --gate launch  # PASS

# 대시보드 생성 → 각 STATUS.md에 ✅ PASS
python3 scripts/status.py --root examples/_complete-min
```

`PASS`면 도구 정상. 이 둘을 본보기 삼아 내 앱을 만든다.

### 일부러 FAIL하는 앵커 — `examples/sip-reminder`

세 번째 예시(`sip-reminder`, 물 마시기 알림)는 **진행 중** 앱이다. 화면 4개 중 하나만 verified, 결정 하나가 승인 대기.
그래서 출시 게이트에서 **FAIL이 뜨는 게 정답이다.**

```bash
python3 scripts/validate.py --root examples/sip-reminder          # PASS(+warn) — 전역 검증은 통과
python3 scripts/validate.py --root examples/sip-reminder --gate launch   # FAIL — 미완성 화면·pending 결정 때문
```

이 FAIL이 게이트의 **음성 앵커**다. "미완성인데 게이트가 잘못 PASS 해버리는 버그"를 잡는 고정 fixture다.
완성 앵커 둘은 반대로 "완성인데 잘못 FAIL 해버리는 버그"를 잡는다. 기대값 표는 **`examples/REGRESSION.md`**.

> `--root` 없이 `python3 scripts/validate.py`를 돌리면 저장소 루트의 **빈 템플릿**을 검사한다.
> 일부러 `FAIL`이 뜬다. 오류가 아니라 **"앞으로 채울 항목 목록"**이다(아래 참고).

---

## 내 앱 만들기 — 단계별

루트 `spec/` 폴더는 값이 전부 `TODO`인 **빈 템플릿**. 이 TODO를 실제 값으로 바꾸는 것이 전부다.
막히면 `examples/sip-reminder/spec/`의 같은 파일을 연다 — 채운 예시가 있다.

**핵심 원칙: 키(구조)는 그대로, 값만 바꾼다.** `validate.py`가 남은 TODO를 잡아 미완성을 막는다.

### 채우는 순서 (게이트 순서와 같다)

| 순서 | 파일 | 무엇을 정하나 | 관련 게이트 |
|---|---|---|---|
| 1 | `spec/manifest.yaml` | 앱 이름·`platform_profile`(mobile/web/hybrid)·수익모델 등 정체성 | — |
| 2 | `spec/evidence.yaml` | **이 앱을 왜 만드는가**(증거·kill 기준) | ① Evidence |
| 3 | `spec/product.yaml`, `spec/screens.yaml` | 기능 범위·화면·6상태<sup>※</sup> | ② Scope |
| 4 | `spec/tokens.json` | 색·타이포·간격 디자인 토큰 | ③ Brand/UX |
| 5 | `spec/architecture.yaml` | 기술 스택·코드 게이트 명령·보안·롤백 | — |
| 6 | `events` · `metrics` · `monetization` · `compliance` | 분석·지표·수익·규제 | ④ Risk / ⑤ Launch |

### 반복 루프

```bash
# 1. spec/의 TODO 하나를 실제 값으로 바꾼다 (막히면 examples/sip-reminder 참고)
# 2. 검증 — 남은 TODO를 목록으로 뱉는다
python3 scripts/validate.py

# 3. RESULT: PASS 뜰 때까지 1~2 반복
# 4. 대시보드 갱신, 진행 상황 확인
python3 scripts/status.py
```

`FAIL` 줄 하나하나가 "이 파일의 이 필드가 아직 TODO"라는 체크리스트다. 전부 채우면 `PASS`.

게이트 단계마다 더 엄격한 검사를 걸 수 있다:

```bash
python3 scripts/validate.py --gate evidence   # 증거 2종·필수 필드·kill 기준을 FAIL로 강제
python3 scripts/validate.py --gate scope      # p0 5개 이하·out_of_scope 강제
python3 scripts/validate.py --gate brand_ux   # 대비 쌍(contrast_pairs) 존재 강제
python3 scripts/validate.py --gate launch     # 블로커 0 + 미성년 규제 + 전 화면 verified(+verify_evidence)/launch_scope 제외 + pending 결정 0 + launch 승인 결정 존재
```

> <sup>※</sup> **6상태**: 화면 하나가 가질 수 있는 6가지 상태(로딩·비어 있음·오류·성공 + 플랫폼별 2종).
> 뒤 2종은 `manifest.platform_profile`로 갈린다 — **mobile**은 오프라인·권한 거부, **web**은 route_404·인증 필요.
> 화면마다 6가지를 어떻게 보여줄지(또는 해당 없음 사유)를 `screens.yaml`에 적는다. `validate.py`가 프로파일에 맞춰 누락을 잡는다.
> **WCAG 대비** = 글자색/배경색 명도 대비가 접근성 기준(WCAG AA)을 넘는지. `validate.py`가 자동 계산한다.

---

## 슬래시 명령 (에이전트용 UI)

Claude Code는 `.claude/commands/`, opencode는 `.opencode/commands/`의 명령을 `/이름`으로 부른다(두 폴더는 같은 내용을 미러링 — 함께 고친다).
**명령은 얇은 진입점.** 실제 엔진은 스펙 스키마 + `validate.py` + 상태 파일. 슬래시 명령 없어도 python 명령으로 똑같이 된다.

**빌드 파이프라인 순서:** `/scaffold` → `/build-data` → `/build-domain` → `/build-screen`(화면별 반복) → `/verify`.
계층을 아래에서 위로 쌓는다(뼈대 → 데이터 → 도메인 → 화면 → 완료 게이트).

| 슬래시 명령 | 하는 일 | 슬래시 없이 직접 실행 |
|---|---|---|
| `/spec` | 스펙 점검, 다음 채울 항목·걸린 게이트 안내(**읽기 전용**) | `python3 scripts/validate.py` |
| `/spec fill` | **대화형 인테이크** — 질문에 답하면 에이전트가 spec을 대신 채운다(YAML 직접 편집 불필요) | (에이전트가 대화하며 기입) |
| `/scaffold` | 프로젝트 뼈대 + 토큰 상수 생성(1/4) | (에이전트가 코드 작성) |
| `/build-data` | 데이터 계층(엔티티·DB·리포지토리) 생성(2/4) | (에이전트가 코드 작성) |
| `/build-domain` | 도메인 유스케이스(순수 로직) 생성(3/4) | (에이전트가 코드 작성) |
| `/build-screen <id>` | 화면 하나를 6상태로 구현 → 검증 → 상태 갱신(4/4, 화면별 반복) | (에이전트가 코드 작성) |
| `/verify` | **완료 게이트** — 스펙 무결성 + 코드 검사 통과 확인 후 tasks.yaml에 `verify_evidence`(validate·code_gates=PASS·by·date) 기록 | `validate.py` + `architecture.yaml` commands(analyze·format·test) |
| `/gate <name>` | 게이트 검증 후 사람 승인 큐에 올림(결정은 사람) | `validate.py --gate <name>` + `state/decisions.yaml`에 항목 추가 |
| `/status` | 대시보드 갱신 후 요약 | `python3 scripts/status.py` |

**`/spec` vs `/verify`:** `/spec`은 "지금 어디까지 왔나" 보는 **읽기 전용 진단**(`/spec fill`은 대화로 값 기입). `/verify`는 "이제 끝났나" 확인하는 **완료 게이트**(코드 검사 포함).

---

## 사람이 판단하는 5개 게이트

에이전트는 자율로 돌되, 아래 5곳에서만 멈춰 사람 승인을 요청한다(상세: **`GATES.md`**).
승인 대기 항목은 `state/decisions.yaml`에 올라오고 `STATUS.md`에 뜬다.

1. **Evidence** — 이 앱을 만들지 (증거·kill 기준)
2. **Scope** — MVP 범위·수익 가설
3. **Brand/UX** — 시각 방향·톤·스토어 첫인상
4. **Risk** — 결제/IAP·광고·미성년/개인정보·되돌리기 어려운 작업
5. **Launch** — 실제 배포·스토어 제출

---

## 폴더 구조

```
spec/     ★ 단 하나의 사실(canonical) — 에이전트가 읽고 채우는 곳
          manifest · evidence · product · screens · tokens.json
          events · metrics · architecture · monetization · compliance
state/
  tasks.yaml       화면별 진행·검증 상태(verified는 verify_evidence 포함)
  decisions.yaml   사람 승인 대기 큐 (혼자 결정 못 하는 것이 여기로)
  bindings.yaml    화면↔코드 파일 매핑(빌드 시 에이전트가 기록) — trace·codemap의 입력
examples/
  _complete-min/     모바일 완성 앵커(Flutter, 실소스 포함) — launch PASS
  web-complete-min/  웹 완성 앵커(TypeScript/React, 실소스 포함) — launch PASS
  sip-reminder/      진행 중 예시(물 마시기 알림) — launch는 일부러 FAIL(음성 앵커)
  REGRESSION.md      세 앵커의 명령·기대값 표(게이트 로직 고친 뒤 재확인)
scripts/
  validate.py      검증 커널 = 게이트(자리표시자·6상태·WCAG 대비·이벤트 정합·수익 필드·출시 블로커)
  status.py        STATUS.md 대시보드 생성기(화면 진행·지표 타겟·승인 큐)
  trace.py         스펙↔코드 드리프트 lint(advisory — warn 전용, `--strict`만 exit 1)
  codemap.py       CODEMAP.md 생성(화면↔코드↔이벤트 지도 + 스펙 인덱스)
.claude/commands/  슬래시 명령 8개(아래 .opencode/commands/에 미러링)
.opencode/commands/  opencode용 미러(같은 8개 — 두 곳을 함께 고친다)
```

앱의 실제 소스 코드는 `spec/architecture.yaml`에서 정한 스택(Flutter, React Native, React 등)에 따라 생성된다. 스택마다 관례가 달라 빈 폴더를 미리 두지 않는다(완성 앵커 두 개만 참조용 실소스를 포함).

---

## 어떤 문서를 언제 읽나

| 문서 | 언제 | 편집 |
|---|---|---|
| **README.md** (지금 이것) | 처음 클론했을 때 | — |
| **`GATES.md`** | 사람이 판단할 5개 지점을 알고 싶을 때 | — |
| **`AGENTS.md`** | 에이전트를 붙여 돌릴 때(운영 계약: 무엇을 읽고 쓰고 검증하는가) | — |
| **`STATUS.md`** | 지금 진행 상황을 볼 때 | ⚙️ **직접 편집하지 않는다** — `status.py`가 생성 |

핵심 규칙: **`spec/`가 사실, 문서와 대시보드는 생성물.** 같은 내용을 두 곳에 쓰지 않는다(드리프트 방지).

---

## 왜 이렇게 만들었나

자율 파이프라인 최대 위험 = "그럴듯하지만 아무도 원하지 않는 앱"을 공장식으로 찍어내는 것.
문서·QA·디자인이 좋아질수록 이 위험은 오히려 가려진다. SLAM은 두 지점에서 막는다.

- **빌드 전 Evidence 게이트** — 증거 없으면 코딩 전에 접는다(빠르게 접기). `--gate evidence`가 증거 부족을 FAIL로 잡는다.
- **출시 후 지표 폐루프** — 에이전트 목표는 "동작하는 코드"가 아니라 `metrics.yaml` 지표 개선. 지표 타겟과 실측이 `STATUS.md`에 나란히 뜬다.

두 번째 위험 = **스펙과 코드가 조용히 어긋나는 것**(선언한 상태·이벤트가 코드엔 없음). `trace.py`가 `bindings.yaml`을 읽어
"선언한 6상태·이벤트가 실제 코드 파일에 있는가"를 훑는다 — advisory lint(warn 전용, 게임 가능한 정규식 수준이라 게이트로는 쓰지 않는다).
출시 게이트(`--gate launch`)도 강화했다: 모든 화면이 `verify_evidence`를 갖춘 verified(또는 launch_scope 제외 명시)이고 모든 게이트의 pending 결정이 0이어야 통과한다.
verified 전환은 구현 에이전트가 못 하고 **별도 verifier 패스**만 할 수 있다 — 자기 코드를 자기가 통과시키지 못하게 막았다.

이 설계는 codex(gpt-5.5)·Antigravity(agy) 교차검증을 거쳐, 산문 기획 템플릿을 **spec 중심 파이프라인**으로 뒤집은 결과다.

---

## License

MIT © bryannamd
