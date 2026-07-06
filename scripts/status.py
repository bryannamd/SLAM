#!/usr/bin/env python3
"""status.py — spec/·state/에서 STATUS.md 대시보드를 생성한다.

터미널 에이전트 환경의 '직관적 UI'는 GUI가 아니라 이 생성 대시보드다.
사람이 STATUS.md 하나로 게이트 상태·화면 진행·blocker·승인 대기·지표 타겟을 본다.

사용:
  python3 scripts/status.py                          # 루트 STATUS.md 갱신
  python3 scripts/status.py --root examples/sip-reminder   # 하위 프로젝트 STATUS 갱신
"""
import pathlib
import subprocess
import sys
import yaml

SCRIPT = pathlib.Path(__file__).resolve()          # scripts/validate.py 위치 고정용
ROOT = SCRIPT.parent.parent                         # 대시보드 대상 프로젝트 루트(기본=repo 루트)
if "--root" in sys.argv:
    ROOT = pathlib.Path(sys.argv[sys.argv.index("--root") + 1]).resolve()
STATE_KEYS = ["loading", "empty", "error", "success", "offline", "permission_denied"]


def y(rel):
    p = ROOT / rel
    if not p.exists():
        return {}
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return {}  # 파싱 실패는 validate가 FAIL로 보고 — 대시보드는 크래시 없이 빈 값 진행
    return data if isinstance(data, dict) else {}  # 형식 오류도 validate가 잡는다


def lst(v):
    """리스트가 아니면(false·0·문자열 포함) 빈 리스트 — 대시보드는 크래시하지 않고 건너뛴다."""
    return v if isinstance(v, list) else []


def cell(v, dash="—"):
    """Markdown 표 셀 값 — 복합 값(매핑·리스트)·빈 값은 대시, 파이프는 이스케이프."""
    if v is None or isinstance(v, (dict, list)):
        return dash
    s = str(v).replace("|", "\\|").replace("\n", " ")
    return s or dash


def main():
    manifest = y("spec/manifest.yaml")
    screens = lst(y("spec/screens.yaml").get("screens"))
    tasks = {t.get("screen"): t for t in lst(y("state/tasks.yaml").get("tasks"))
             if isinstance(t, dict) and isinstance(t.get("screen"), str) and t.get("screen")}
    decisions = lst(y("state/decisions.yaml").get("decisions"))
    metrics = y("spec/metrics.yaml")

    # validate 실행 결과를 대시보드에 반영(같은 --root로)
    v = subprocess.run([sys.executable, str(SCRIPT.parent / "validate.py"), "--root", str(ROOT)],
                       capture_output=True, text=True)
    validate_line = next((ln for ln in reversed(v.stdout.splitlines()) if ln.startswith("RESULT:")), "?")
    validate_ok = v.returncode == 0

    L = []
    L.append(f"# STATUS — {manifest.get('name', '?')}")
    L.append("")
    L.append(f"> {manifest.get('one_liner', '')}")
    L.append("")
    L.append("> ⚙️ 이 파일은 `scripts/status.py`가 생성한다. 직접 편집하지 말 것(spec/·state/를 고친다).")
    L.append("")
    L.append(f"- 플랫폼: {', '.join(map(str, lst(manifest.get('platforms'))))} | backend: {manifest.get('backend')} "
             f"| audience: {manifest.get('audience')} | risk: {manifest.get('risk_class')} "
             f"| 수익: {manifest.get('monetization_model')}")
    L.append(f"- 검증: {'✅ PASS' if validate_ok else '❌ FAIL'}  (`{validate_line}`)")
    L.append("")

    # 화면 진행 + 6상태 커버리지
    L.append("## 화면 진행")
    L.append("")
    L.append("| 화면 | 우선 | 상태 | 6상태(구현/NA) | blocker |")
    L.append("|---|---|---|---|---|")
    emoji = {"todo": "⬜ todo", "in_progress": "🔨 진행", "built": "🧱 완성",
             "verified": "✅ 검증", "blocked": "⛔ 막힘"}
    for s in screens:
        if not isinstance(s, dict) or not isinstance(s.get("id"), str) or not s.get("id"):
            continue  # 형식 오류는 validate가 FAIL로 잡는다 — 대시보드는 건너뛰고 그린다
        st = s.get("states", {})
        st = st if isinstance(st, dict) else {}
        impl = sum(1 for k in STATE_KEYS if isinstance(st.get(k), dict) and "na" not in st[k])
        na = sum(1 for k in STATE_KEYS if isinstance(st.get(k), dict) and "na" in st[k])
        t = tasks.get(s["id"], {})
        status_key = t.get("status") if isinstance(t.get("status"), str) else None
        L.append(f"| {cell(s['id'])} | {cell(s.get('priority'), '')} | {emoji.get(status_key, '⬜ todo')} "
                 f"| {impl}/{na} | {cell(t.get('blocker'))} |")
    L.append("")

    # 지표 타겟 — 출시 후 폐루프의 기준선(actual은 출시 후 수동 기입)
    rows = [(m, "product") for m in lst(metrics.get("product")) if isinstance(m, dict)] \
         + [(m, "client") for m in lst(metrics.get("client")) if isinstance(m, dict)]
    if rows:
        L.append("## 지표 타겟")
        L.append("")
        L.append("| 지표 | 구분 | 목표 | 실측 |")
        L.append("|---|---|---|---|")
        for m, kind in rows:
            if not isinstance(m.get("key"), str) or not m.get("key"):
                continue  # 형식 오류는 validate가 FAIL로 잡는다
            L.append(f"| {cell(m['key'])} | {kind} | {cell(m.get('target'))} | {cell(m.get('actual'))} |")
        L.append("")

    # 인간 승인 대기 큐
    pend = [d for d in decisions if isinstance(d, dict) and d.get("status") == "pending"]
    L.append(f"## 인간 승인 대기 ({len(pend)})")
    L.append("")
    if not pend:
        L.append("_대기 중인 결정 없음._")
    else:
        for d in pend:
            L.append(f"- **[{d.get('gate')}] {d.get('id')} — {d.get('decision')}**")
            L.append(f"  - 추천: {d.get('recommendation')}")
            L.append(f"  - 리스크: {d.get('risk')} | 되돌리기: {d.get('reversible')} | 영향: {', '.join(map(str, lst(d.get('impacts'))))}")
    L.append("")

    out = ROOT / "STATUS.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  (validate={'PASS' if validate_ok else 'FAIL'})")


if __name__ == "__main__":
    main()
