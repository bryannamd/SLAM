# SLAM

**S**pec-driven · **L**ess-prompt · **A**pp · **M**aker

> 스펙을 새기면, 프롬프트 없이 앱이 나온다.
> Build company-grade apps from specs, with less prompting.

SLAM은 소규모 팀(1~2인)이 **AI 에이전트로 완성도·수익성 높은 모바일 앱을 자율로 찍어내기 위한 보일러플레이트**다.
산문 기획서를 사람이 채우는 대신, `spec/`을 **단일 진실(canonical)**로 두고 에이전트가 읽고·쓰고·검증한다.
사람은 되돌리기 어렵거나 돈·법·브랜드가 걸린 **5개 게이트에서만** 판단한다.

Claude Code / opencode 등 에이전트 런타임 어디서든 동작한다. "UI"는 GUI가 아니라 **슬래시 명령 + 생성되는 `STATUS.md` 대시보드**다.

---

## 왜 이렇게 만들었나

자율 파이프라인의 최대 위험은 "그럴듯하지만 아무도 원하지 않는 앱"을 공장식으로 찍어내는 것이다.
문서·QA·디자인이 좋아질수록 이 위험은 오히려 가려진다. SLAM은 두 지점에서 이를 막는다.

- **빌드 전 Evidence Gate** — 증거 없으면 코딩 전에 죽인다(빨리 죽이기).
- **출시 후 지표 폐루프** — 에이전트의 목표는 "동작하는 코드"가 아니라 `metrics.yaml` 지표 개선이다.

설계는 codex(gpt-5.5)·Antigravity(agy) 교차검증을 거쳐, 산문 템플릿을 **spec-canonical 파이프라인**으로 뒤집은 결과다.

---

## 구조

```
spec/     ★ canonical — 에이전트가 읽고 쓰는 '사실'
  manifest · evidence · product · screens · tokens.json
  events · metrics · architecture · monetization · compliance
state/
  tasks.yaml       화면별 진행·검증 상태
  decisions.yaml   인간 승인 큐 (혼자 결정 금지 항목이 여기로)
scripts/
  validate.py      검증 커널 = 게이트 (자리표시자·6상태·WCAG 대비·이벤트 정합·출시 블로커)
  status.py        STATUS.md 대시보드 생성기
.claude/commands/  슬래시 명령(얇은 진입점): spec · build-screen · verify · gate · status
AGENTS.md          에이전트 운영 계약 (소유권·루프·자율 vs 승인 경계)
GATES.md           인간 판단 5개 게이트
STATUS.md          ⚙️ 생성물 — 진행 대시보드 (직접 편집 금지)
```

spec와 문서의 관계: **spec가 진실, 문서·대시보드는 생성물**이다. 같은 사실을 두 곳에 쓰지 않는다(드리프트 방지).

---

## 빠른 시작

```bash
python3 scripts/validate.py            # 전체 무결성 검증 (0=PASS)
python3 scripts/validate.py --gate launch   # 출시 블로커까지
python3 scripts/validate.py --selftest      # 대비 계산 자가검증
python3 scripts/status.py              # STATUS.md 갱신
```

이 저장소의 `spec/`은 중립 예시 앱(**SipReminder** — 물 마시기 알림, 오프라인)으로 채워져 있어 바로 green이다.
새 프로젝트는 **키 구조는 유지하고 값만 교체**한다. `validate.py`가 남은 자리표시자를 잡아 미완성을 막는다.

의존성: Python 3 + PyYAML (`pip install pyyaml`).

---

## 슬래시 명령 (에이전트 UI)

Claude Code는 `.claude/commands/`, opencode는 `.opencode/command/`에 두면 `/명령`으로 호출된다.
명령은 진입점일 뿐 — 실제 엔진은 spec 스키마 + `validate.py` + 상태 전이다.

| 명령 | 하는 일 |
|---|---|
| `/spec` | spec 무결성 검증 후 부족한 필드·다음 게이트 안내 |
| `/build-screen <id>` | 화면 하나를 6상태로 구현 → 검증 → tasks 갱신 |
| `/verify` | validate + 코드 게이트(analyze/format/test) |
| `/gate <name>` | 게이트 판단 항목을 decisions.yaml에 올림 |
| `/status` | STATUS.md 갱신 후 요약 |

---

## 인간 판단 5개 게이트

자율로 돌되, 아래에서만 사람이 멈춰 판단한다(상세: `GATES.md`).

1. **Evidence** — 이 앱을 만들지(증거·kill 기준)
2. **Scope** — MVP 범위·수익 가설
3. **Brand/UX** — 시각 방향·톤·스토어 첫인상
4. **Risk** — 결제/IAP·광고·미성년/개인정보·되돌리기 어려운 작업
5. **Launch** — 실제 배포·스토어 제출

---

## License

MIT © bryannamd
