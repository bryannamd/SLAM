#!/usr/bin/env python3
"""codemap.py — CODEMAP.md 생성기(초보 네비게이션용).

스펙(spec/*)·바인딩(state/bindings.yaml)·진행상태(state/tasks.yaml)를 읽어, "어디를 열어
무엇을 바꾸는가"를 한 장으로 요약한다. 코드를 grep하지 않는다 — 전부 스펙 기준이라
드리프트 검출이 아니라 지도다(드리프트는 trace.py 담당).

사용:
  python3 scripts/codemap.py                        # 루트 spec/ 기준
  python3 scripts/codemap.py --root examples/_complete-min
출력: <root>/CODEMAP.md (덮어씀 — 직접 편집 금지, 재실행으로 갱신)
"""
import sys
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# spec/ 10파일 인덱스: 파일 → (한 줄 설명, 무엇을 바꿀 때 여는가).
SPEC_INDEX = [
    ("manifest.yaml", "앱 정체성의 단일 원천(이름·플랫폼·수익모델·연령·리스크).",
     "앱 이름·대상 플랫폼·타깃 사용자·수익 모델을 바꿀 때."),
    ("evidence.yaml", "왜 만드는가 — 문제·타깃·실증거·중단(kill) 기준.",
     "문제 정의나 '언제 접는가' 기준을 세우거나 고칠 때."),
    ("product.yaml", "무엇을 만드는가 — 기능 우선순위(p0/p1)·범위 밖(out_of_scope).",
     "기능을 넣고 빼거나 MVP 범위를 조일 때."),
    ("screens.yaml", "화면 명세 + 6상태 계약(loading/empty/error/success + 프로파일 상태).",
     "화면을 추가하거나 상태별 UI·문구를 정할 때."),
    ("events.yaml", "분석 이벤트의 단일 원천(name·trigger·props).",
     "새 분석 이벤트를 추가하거나 이름·속성을 바꿀 때."),
    ("metrics.yaml", "성공·성장 지표 타깃(product는 이벤트를 uses로 참조, client는 성능).",
     "성공 지표나 성능 목표를 세우거나 이벤트 연결을 바꿀 때."),
    ("monetization.yaml", "수익화 상세(model·paid_features·pricing·paywall_trigger).",
     "유료 기능·가격·페이월 트리거를 정할 때(manifest와 일치해야 함)."),
    ("architecture.yaml", "기술 스택·계층·코드 게이트 명령(analyze/format/test).",
     "프레임워크·백엔드·검증 명령을 정하거나 바꿀 때."),
    ("compliance.yaml", "출시 블로커·미성년자(COPPA)·개인정보 처리.",
     "출시 전 법적 블로커를 등록·해소하거나 연령 정책을 정할 때."),
    ("tokens.json", "디자인 토큰(color/typography/spacing) + 대비 쌍 — 코드 색의 원천.",
     "색·타이포·간격을 바꿀 때(app/lib/tokens.dart로 반영)."),
]


def load_yaml(path):
    if not path.exists():
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def esc(v):
    """마크다운 표 셀용: None→'—', 파이프 이스케이프."""
    if v is None or v == "":
        return "—"
    return str(v).replace("|", "\\|").replace("\n", " ")


def as_list(v):
    """리스트가 아니면(bool·int·문자열 등) 빈 리스트 — 순회 전 크래시 방지(validate.req_list 스타일)."""
    return v if isinstance(v, list) else []


def build(root):
    screens_doc = load_yaml(root / "spec" / "screens.yaml") or {}
    events_doc = load_yaml(root / "spec" / "events.yaml") or {}
    metrics_doc = load_yaml(root / "spec" / "metrics.yaml") or {}
    bindings_doc = load_yaml(root / "state" / "bindings.yaml") or {}
    tasks_doc = load_yaml(root / "state" / "tasks.yaml") or {}
    manifest = load_yaml(root / "spec" / "manifest.yaml") or {}

    # id/name/screen 키는 문자열만 인정 — list/dict 등 비해시 값이 dict 키로 흘러들어 크래시하는 것을 막는다.
    screens = [s for s in as_list(screens_doc.get("screens"))
               if isinstance(s, dict) and isinstance(s.get("id"), str)]
    events = [e for e in as_list(events_doc.get("events"))
              if isinstance(e, dict) and isinstance(e.get("name"), str)]

    # 화면 id → 바인딩 파일.
    files_by_screen = {}
    for b in as_list(bindings_doc.get("bindings")):
        if isinstance(b, dict) and isinstance(b.get("screen"), str):
            fs = as_list(b.get("files"))
            files_by_screen[b.get("screen")] = [str(f) for f in fs]

    # 화면 id → status(tasks.yaml).
    status_by_screen = {}
    for t in as_list(tasks_doc.get("tasks")):
        if isinstance(t, dict) and isinstance(t.get("screen"), str):
            status_by_screen[t.get("screen")] = t.get("status")

    # 이벤트 name → 참조 지표(metrics.product[].uses).
    metrics_by_event = {}
    for m in as_list(metrics_doc.get("product")):
        if isinstance(m, dict):
            for u in as_list(m.get("uses")):
                if isinstance(u, str):
                    metrics_by_event.setdefault(u, []).append(m.get("key"))

    out = []
    out.append("<!-- 생성물 — 직접 편집 금지. `python3 scripts/codemap.py"
               " --root <경로>` 재실행으로 갱신한다. -->")
    out.append(f"# CODEMAP — {manifest.get('name') or root.name}")
    out.append("")
    out.append("스펙·바인딩·진행상태를 한 장으로 요약한 네비게이션 지도. "
               "코드를 grep하지 않고 스펙 기준으로만 만든다(드리프트 검출은 `scripts/trace.py`).")
    out.append("")

    # ① 화면 표.
    out.append("## 화면")
    out.append("")
    out.append("| id | 목적 | 우선순위 | status | 바인딩 파일 |")
    out.append("| --- | --- | --- | --- | --- |")
    if screens:
        for s in screens:
            sid = s.get("id")
            files = files_by_screen.get(sid)
            files_cell = "<br>".join(f"`{f}`" for f in files) if files else "미기록"
            out.append(f"| {esc(sid)} | {esc(s.get('purpose'))} | "
                       f"{esc(s.get('priority'))} | {esc(status_by_screen.get(sid))} | "
                       f"{files_cell} |")
    else:
        out.append("| — | (screens.yaml에 화면 없음) | — | — | — |")
    out.append("")

    # ② 이벤트 표.
    out.append("## 이벤트")
    out.append("")
    out.append("발화 화면은 스펙에 직접 매핑이 없어 트리거(발화 시점)로 표기한다"
               "(코드 상 실제 발화 여부는 `scripts/trace.py`가 검사).")
    out.append("")
    out.append("| 이벤트 | 발화 시점(trigger) | 참조 지표 |")
    out.append("| --- | --- | --- |")
    if events:
        for e in events:
            name = e.get("name")
            refs = metrics_by_event.get(name)
            refs_cell = ", ".join(f"`{r}`" for r in refs) if refs else "—"
            out.append(f"| `{esc(name)}` | {esc(e.get('trigger'))} | {refs_cell} |")
    else:
        out.append("| — | (events.yaml에 이벤트 없음) | — |")
    out.append("")

    # ③ 스펙 파일 인덱스.
    out.append("## 스펙 파일 인덱스")
    out.append("")
    out.append("| 파일 | 무엇인가 | 무엇을 바꿀 때 여는가 |")
    out.append("| --- | --- | --- |")
    for fname, what, when in SPEC_INDEX:
        exists = "" if (root / "spec" / fname).exists() else " (없음)"
        out.append(f"| `spec/{fname}`{exists} | {esc(what)} | {esc(when)} |")
    out.append("")
    out.append("---")
    out.append("")
    out.append("바인딩(화면↔파일)은 `state/bindings.yaml`에서, 진행상태는 `state/tasks.yaml`에서 온다.")
    out.append("")

    return "\n".join(out)


def main():
    global ROOT
    argv = sys.argv[1:]
    if "--root" in argv:
        i = argv.index("--root")
        if i + 1 < len(argv):
            ROOT = pathlib.Path(argv[i + 1]).resolve()

    content = build(ROOT)
    target = ROOT / "CODEMAP.md"
    target.write_text(content, encoding="utf-8")
    print(f"생성: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
