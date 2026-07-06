# SLAM

**S**pec-driven · **L**ess-prompt · **A**pp · **M**aker

> 스펙을 새기면, 프롬프트 없이 앱이 나온다.
> Build company-grade apps from specs, with less prompting.

SLAM = 1~2인 팀이 AI 코딩 에이전트로 완성도·수익성 높은 모바일 앱을 자율로 만드는 보일러플레이트.
긴 기획서를 매번 프롬프트로 붙여넣지 않는다. `spec/` 폴더 YAML이 **단 하나의 사실(canonical)** — 에이전트가 읽고, 채우고, 검증한다.
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

저장소에 완성된 참조 앱(`examples/sip-reminder`, 물 마시기 알림)이 들어 있다. 클론 직후 바로 검증이 통과한다.

```bash
# 완성된 예시 앱 스펙 검증 → RESULT: PASS 떠야 정상
python3 scripts/validate.py --root examples/sip-reminder

# 출시 게이트까지 검증
python3 scripts/validate.py --root examples/sip-reminder --gate launch

# 대시보드 생성 → examples/sip-reminder/STATUS.md 갱신
python3 scripts/status.py --root examples/sip-reminder
```

`PASS`면 도구 정상. 이 예시를 본보기 삼아 내 앱을 만든다.

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
| 1 | `spec/manifest.yaml` | 앱 이름·플랫폼·수익모델 등 정체성 | — |
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
python3 scripts/validate.py --gate launch     # 출시 블로커 0 + 미성년 규제 + launch 승인
```

> <sup>※</sup> **6상태**: 화면 하나가 가질 수 있는 6가지 상태(로딩·비어 있음·오류·성공·오프라인·권한 거부).
> 화면마다 6가지를 어떻게 보여줄지(또는 해당 없음 사유)를 `screens.yaml`에 적는다. `validate.py`가 누락을 잡는다.
> **WCAG 대비** = 글자색/배경색 명도 대비가 접근성 기준(WCAG AA)을 넘는지. `validate.py`가 자동 계산한다.

---

## 슬래시 명령 (에이전트용 UI)

Claude Code는 `.claude/commands/`, opencode는 `.opencode/commands/`의 명령을 `/이름`으로 부른다.
**명령은 얇은 진입점.** 실제 엔진은 스펙 스키마 + `validate.py` + 상태 파일. 슬래시 명령 없어도 python 명령으로 똑같이 된다.

| 슬래시 명령 | 하는 일 | 슬래시 없이 직접 실행 |
|---|---|---|
| `/spec` | 스펙 점검, 다음 채울 항목·걸린 게이트 안내(읽기 전용) | `python3 scripts/validate.py` |
| `/build-screen <id>` | 화면 하나를 6상태로 구현 → 검증 → 상태 갱신 | (에이전트가 코드 작성) |
| `/verify` | **완료 게이트** — 스펙 무결성 + 코드 검사까지 통과 확인 | `validate.py` + `architecture.yaml` commands(analyze·format·test) |
| `/gate <name>` | 게이트 검증 후 사람 승인 큐에 올림(결정은 사람) | `validate.py --gate <name>` + `state/decisions.yaml`에 항목 추가 |
| `/status` | 대시보드 갱신 후 요약 | `python3 scripts/status.py` |

**`/spec` vs `/verify`:** `/spec`은 "지금 어디까지 왔나" 보는 **읽기 전용 진단**. `/verify`는 "이제 끝났나" 확인하는 **완료 게이트**(코드 검사 포함).

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
  tasks.yaml       화면별 진행·검증 상태
  decisions.yaml   사람 승인 대기 큐 (혼자 결정 못 하는 것이 여기로)
examples/
  sip-reminder/    완성된 참조 앱(물 마시기 알림, 오프라인) — 그대로 PASS
scripts/
  validate.py      검증 커널 = 게이트(자리표시자·6상태·WCAG 대비·이벤트 정합·수익 필드·출시 블로커)
  status.py        STATUS.md 대시보드 생성기(화면 진행·지표 타겟·승인 큐)
.claude/commands/  슬래시 명령: spec · build-screen · verify · gate · status
```

앱의 실제 소스 코드는 `spec/architecture.yaml`에서 정한 스택(Flutter, React Native 등)에 따라 생성된다. 스택마다 관례가 달라 빈 폴더를 미리 두지 않는다.

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

이 설계는 codex(gpt-5.5)·Antigravity(agy) 교차검증을 거쳐, 산문 기획 템플릿을 **spec 중심 파이프라인**으로 뒤집은 결과다.

---

## License

MIT © bryannamd
