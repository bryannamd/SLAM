# SLAM

**S**pec-driven · **L**ess-prompt · **A**pp · **M**aker

> 기획서를 매번 붙여넣지 마세요. 한 번 적어두면, AI가 읽고 앱을 만듭니다.

[한눈에 보기](#한눈에-보기) · [빠른 시작](#빠른-시작-5분) · [어디서 시작할까](#어디서-시작할까) · [명령어](#명령어) · [게이트](#사람이-판단하는-5곳) · [폴더 구조](#폴더-구조)

---

## 한눈에 보기

SLAM은 **혼자, 또는 둘이서 AI 코딩 에이전트로 앱을 만들 때 쓰는 뼈대**입니다. 모바일과 웹 둘 다 됩니다.

보통 AI에게 앱을 시키면 이런 문제가 생깁니다.

- 긴 기획서를 매번 프롬프트로 다시 붙여넣어야 한다.
- AI가 "그럴듯하지만 아무도 원하지 않는 앱"을 열심히 찍어낸다.
- 시간이 지나면 문서와 코드가 조용히 어긋난다.

SLAM은 이걸 세 가지로 막습니다.

| | 방법 |
|---|---|
| 📄 **기획서를 한 곳에** | `spec/` 폴더의 YAML 파일이 유일한 원본. AI가 여기를 읽고, 채우고, 검사한다. |
| ✅ **자동 검사** | `validate.py` 한 줄이 "아직 안 채운 항목"을 목록으로 뱉는다. 통과할 때까지 반복. |
| 🚦 **사람은 5곳에서만** | 돈·법·브랜드·되돌리기 어려운 일. 나머지는 AI가 알아서. |

SLAM 자체는 GUI가 없습니다. **슬래시 명령으로 조작하고, 진행 상황은 자동 생성되는 `STATUS.md` 대시보드로 봅니다.** (만들 앱의 화면은 별개로 `spec/screens.yaml`에 정의하고 소스는 `examples/*/app`처럼 생깁니다.) Claude Code, opencode 같은 에이전트 어디서든 돕니다.

---

## 빠른 시작 (5분)

### 1. 설치

```bash
git clone https://github.com/bryannamd/SLAM.git
cd SLAM
python3 -m pip install pyyaml
```

> 최신 macOS에서 `externally-managed-environment` 오류가 나면 가상환경을 쓰세요.
> `python3 -m venv .venv && source .venv/bin/activate && pip install pyyaml`

필요한 건 **Python 3 + PyYAML**뿐입니다. Claude Code나 opencode가 있으면 `/spec` 같은 슬래시 명령을 쓸 수 있지만, 없어도 아래 python 명령으로 전부 됩니다.

### 2. 완성된 예시를 먼저 돌려본다

저장소에 완성 수준의 참조 앱 두 개가 들어 있습니다(실제 소스는 각 `app/` 폴더에). 출시 검사(`--gate launch`)를 통과합니다.

```bash
# 모바일 예시 (Flutter) → PASS 떠야 정상
python3 scripts/validate.py --root examples/_complete-min --gate launch

# 웹 예시 (React) → PASS 떠야 정상
python3 scripts/validate.py --root examples/web-complete-min --gate launch

# 대시보드 만들어 보기
python3 scripts/status.py --root examples/_complete-min
```

`PASS`가 뜨면 도구가 정상입니다. 이 둘을 본보기 삼으면 됩니다.

### 3. 내 앱 만들기 시작

루트 `spec/` 폴더는 채워야 할 값이 `TODO`로 표시된 템플릿입니다. 이 `TODO`를 실제 값으로 바꾸면 됩니다. (플랫폼·스택 같은 몇몇 값은 기본값이 이미 들어 있으니 필요할 때만 바꾸세요.)

```bash
# 검증 → 아직 안 채운 TODO를 목록으로 알려준다
python3 scripts/validate.py
```

`FAIL` 한 줄 한 줄이 "이 항목이 아직 비어 있다"는 체크리스트입니다. 다 채우면 `PASS`. 막히면 [`examples/sip-reminder/spec/`](examples/sip-reminder/spec/)의 채워진 예시를 열어 보세요.

**핵심 규칙: 키(구조)는 그대로 두고, 값만 바꿉니다.**

---

## 어디서 시작할까

| 지금 상황 | 이렇게 하세요 |
|---|---|
| SLAM이 뭔지 감 잡고 싶다 | 위 [빠른 시작 2번](#2-완성된-예시를-먼저-돌려본다)으로 완성 예시부터 돌려본다 |
| 내 앱을 바로 만들고 싶다 | `spec/manifest.yaml`부터 `TODO`를 채운다 ([순서 표](#채우는-순서)) |
| YAML 직접 고치기 싫다 | Claude Code에서 `/spec fill` — 질문에 답하면 AI가 대신 채운다 |
| 사람이 언제 개입하나 궁금하다 | [사람이 판단하는 5곳](#사람이-판단하는-5곳) 또는 `GATES.md` |
| AI 에이전트를 붙여 자동으로 돌리고 싶다 | `AGENTS.md` (에이전트가 따르는 운영 규칙) |

---

## 채우는 순서

빈 템플릿을 채우는 순서입니다. 게이트 순서와 같습니다.

| 순서 | 파일 | 무엇을 정하나 |
|---|---|---|
| 1 | `spec/manifest.yaml` | 앱 이름 · 플랫폼(mobile/web/hybrid) · 수익 모델 |
| 2 | `spec/evidence.yaml` | **이 앱을 왜 만드나** (근거와 접는 기준) |
| 3 | `spec/product.yaml`, `screens.yaml` | 기능 범위 · 화면 · 화면별 6가지 상태<sup>※</sup> |
| 4 | `spec/tokens.json` | 색 · 글꼴 · 간격 (디자인 토큰) |
| 5 | `spec/architecture.yaml` | 기술 스택 · 코드 검사 명령 · 보안 · 롤백 |
| 6 | `events` · `metrics` · `monetization` · `compliance` | 분석 · 지표 · 수익 · 규제 |

한 항목 바꿀 때마다 `python3 scripts/validate.py`를 돌려 `PASS`가 될 때까지 반복하면 됩니다.

> <sup>※</sup> **6상태**: 화면 하나가 보여줄 수 있는 6가지 모습 — 로딩 · 비어 있음 · 오류 · 성공, 그리고 플랫폼별 2가지.
> mobile은 오프라인 · 권한 거부, web은 없는 페이지(404) · 로그인 필요. `validate.py`가 플랫폼에 맞춰 빠진 상태를 잡아줍니다.
> 화면에서 해당 없는 상태는 사유와 함께 `na`로 표시하면 됩니다 — 6개를 모두 구현해야 하는 건 아닙니다.

---

## 명령어

Claude Code(`/이름`)나 opencode에서 슬래시 명령으로 부릅니다. 슬래시 명령은 **얇은 진입점**일 뿐이고, 실제 엔진은 spec 파일 + `validate.py`입니다. 그래서 슬래시 없이 python으로도 똑같이 됩니다.

**빌드 순서:** `/scaffold` → `/build-data` → `/build-domain` → `/build-screen`(화면마다 반복) → `/verify`
(뼈대 → 데이터 → 로직 → 화면 → 완료 검사, 아래에서 위로 쌓습니다.)

| 슬래시 명령 | 하는 일 | python으로 직접 |
|---|---|---|
| `/spec` | 스펙 점검, 다음에 채울 항목 안내 (읽기 전용) | `scripts/validate.py` |
| `/spec fill` | **대화형** — 질문에 답하면 AI가 spec을 대신 채운다 | — |
| `/scaffold` | 프로젝트 뼈대 + 토큰 상수 생성 | (AI가 코드 작성) |
| `/build-data` | 데이터 계층(엔티티·DB·리포지토리) | (AI가 코드 작성) |
| `/build-domain` | 도메인 로직(순수 유스케이스) | (AI가 코드 작성) |
| `/build-screen <id>` | 화면 하나를 6상태로 구현 → 검증 | (AI가 코드 작성) |
| `/verify` | **완료 게이트** — 스펙 + 코드 검사 통과 확인 | `validate.py` + 코드 검사 |
| `/gate <name>` | 게이트 검증 후 사람 승인 큐에 올림 | `validate.py --gate <name>` |
| `/status` | 대시보드 갱신 후 요약 | `scripts/status.py` |

> **`/spec`과 `/verify` 차이:** `/spec`은 "지금 어디까지 왔나" 보는 읽기 전용 진단. `/verify`는 "이제 끝났나" 확인하는 완료 게이트(코드 검사 포함).

게이트 단계마다 더 엄격한 검사도 걸 수 있습니다.

```bash
python3 scripts/validate.py --gate evidence   # 근거 2종 이상 · 접는 기준 강제
python3 scripts/validate.py --gate scope      # p0 기능 5개 이하 강제
python3 scripts/validate.py --gate brand_ux   # 색 대비(WCAG) 강제
python3 scripts/validate.py --gate launch     # 출시 블로커 0 + 전 화면 검증 완료 강제
```

---

## 사람이 판단하는 5곳

AI는 알아서 돌되, 아래 5곳에서만 멈춰 사람에게 승인을 요청합니다. 대기 항목은 `state/decisions.yaml`에 올라오고 `STATUS.md`에 뜹니다. (상세: `GATES.md`)

| # | 게이트 | 무엇을 판단하나 |
|---|---|---|
| 1 | **Evidence** | 이 앱을 만들 근거가 있나 (없으면 코딩 전에 접는다) |
| 2 | **Scope** | MVP 범위 · 수익 가설이 맞나 |
| 3 | **Brand/UX** | 시각 방향 · 톤 · 스토어 첫인상 |
| 4 | **Risk** | 결제 · 광고 · 미성년/개인정보 · 되돌리기 어려운 작업 |
| 5 | **Launch** | 실제 배포 · 스토어 제출 |

---

## 예시 3개

| 예시 | 무엇 | 출시 검사 |
|---|---|---|
| `examples/_complete-min` | 완성된 모바일 앱 (Flutter, 실제 소스 포함) | ✅ PASS |
| `examples/web-complete-min` | 완성된 웹 앱 (React, 실제 소스 포함) | ✅ PASS |
| `examples/sip-reminder` | **진행 중** 앱 (물 마시기 알림) | ❌ FAIL (일부러) |

> 완성 예시의 검사 통과는 스펙과 상태 파일 기준입니다(`code_gates: PASS`는 기록된 fixture 값 — 매번 Flutter/React 툴체인을 실제로 돌리는 건 아닙니다). 참조용 뼈대로 보세요.

`sip-reminder`는 아직 화면이 덜 됐고 승인 대기 결정이 남아 있어서 **출시 검사에서 FAIL이 뜨는 게 정답**입니다. 이건 "미완성인데 검사가 실수로 통과시키는 버그"를 잡아내는 고정 시험대입니다. 반대로 완성 예시 둘은 "완성인데 실수로 막는 버그"를 잡습니다. 기대값 표는 `examples/REGRESSION.md`에 있습니다.

> `--root` 없이 `python3 scripts/validate.py`를 돌리면 루트의 **빈 템플릿**을 검사합니다.
> 일부러 `FAIL`이 뜹니다. 오류가 아니라 **"앞으로 채울 항목 목록"**입니다.

---

## 폴더 구조

```
spec/     ★ 유일한 원본 — AI가 읽고 채우는 곳
          manifest · evidence · product · screens · tokens.json
          events · metrics · architecture · monetization · compliance
state/
  tasks.yaml       화면별 진행·검증 상태
  decisions.yaml   사람 승인 대기 큐 (혼자 결정 못 하는 것이 여기로)
  bindings.yaml    화면 ↔ 코드 파일 매핑 (빌드 때 AI가 기록)
examples/
  _complete-min/     완성된 모바일 예시 (Flutter)   — 출시 PASS
  web-complete-min/  완성된 웹 예시 (React)          — 출시 PASS
  sip-reminder/      진행 중 예시                    — 출시 일부러 FAIL
  REGRESSION.md      세 예시의 명령·기대값 표
scripts/
  validate.py   검증 엔진 = 게이트 (빈 값·6상태·색 대비·이벤트 정합·출시 블로커)
  status.py     STATUS.md 대시보드 생성기
  trace.py      스펙 ↔ 코드 어긋남 점검 (참고용, 경고만)
  codemap.py    CODEMAP.md 생성 (화면 ↔ 코드 ↔ 이벤트 지도)
.claude/commands/    슬래시 명령 (opencode용 .opencode/commands/에 미러링)
```

앱의 실제 소스는 `spec/architecture.yaml`에서 정한 스택(Flutter, React 등)에 따라 만들어집니다. 스택마다 관례가 달라서 빈 폴더를 미리 두지 않습니다(완성 예시 둘만 참조용 소스를 포함).

---

## 어떤 문서를 언제 읽나

| 문서 | 언제 |
|---|---|
| **README.md** (지금 이것) | 처음 클론했을 때 |
| **GATES.md** | 사람이 판단할 5곳을 자세히 알고 싶을 때 |
| **AGENTS.md** | AI 에이전트를 붙여 자동으로 돌릴 때 |
| **STATUS.md** | 지금 진행 상황을 볼 때 (⚙️ 직접 편집 금지 — `status.py`가 생성) |

**핵심 규칙: 기획은 `spec/`, 진행 상태는 `state/`가 원본이고, 문서와 대시보드(`STATUS.md`·`CODEMAP.md`)는 그걸로 만든 결과물입니다.** 같은 내용을 두 곳에 쓰지 않아야 어긋나지 않습니다.

---

## 왜 이렇게 만들었나

자율 파이프라인의 가장 큰 위험은 **"그럴듯하지만 아무도 원하지 않는 앱"을 공장처럼 찍어내는 것**입니다. 문서·QA·디자인이 좋아질수록 이 위험은 오히려 가려집니다. SLAM은 두 곳에서 막습니다.

- **빌드 전 Evidence 게이트** — 근거가 없으면 코딩 전에 접습니다. `--gate evidence`가 근거 부족을 FAIL로 잡습니다.
- **출시 후 지표 폐루프** — AI의 목표는 "동작하는 코드"가 아니라 `metrics.yaml` 지표 개선입니다. 목표와 실측이 `STATUS.md`에 나란히 뜹니다.

두 번째 위험은 **스펙과 코드가 조용히 어긋나는 것**입니다. `trace.py`가 "선언한 상태·이벤트가 실제 코드에 있는지"를 훑습니다(참고용 경고). 출시 게이트는 더 엄격해서, 모든 화면이 검증을 마치고 대기 중인 결정이 0이어야 통과합니다. 또한 검증 통과는 구현한 에이전트가 스스로 할 수 없고 **별도 검증 에이전트만** 할 수 있습니다 — 자기 코드를 자기가 통과시키지 못하게 막았습니다.

이 설계는 codex(GPT-5.5)와 Antigravity(agy) 교차검증을 거쳐, 산문 기획 템플릿을 **spec 중심 파이프라인**으로 뒤집은 결과입니다.

---

## License

MIT © bryannamd
