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
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def main():
    manifest = y("spec/manifest.yaml") or {}
    screens = (y("spec/screens.yaml") or {}).get("screens", [])
    tasks = {t["screen"]: t for t in (y("state/tasks.yaml") or {}).get("tasks", [])}
    decisions = (y("state/decisions.yaml") or {}).get("decisions", [])

    # validate 실행 결과를 대시보드에 반영(같은 --root로)
    v = subprocess.run([sys.executable, str(SCRIPT.parent / "validate.py"), "--root", str(ROOT)],
                       capture_output=True, text=True)
    validate_line = v.stdout.strip().splitlines()[-2] if v.stdout.strip() else "?"
    validate_ok = v.returncode == 0

    L = []
    L.append(f"# STATUS — {manifest.get('name', '?')}")
    L.append("")
    L.append(f"> {manifest.get('one_liner', '')}")
    L.append("")
    L.append("> ⚙️ 이 파일은 `scripts/status.py`가 생성한다. 직접 편집하지 말 것(spec/·state/를 고친다).")
    L.append("")
    L.append(f"- 플랫폼: {', '.join(manifest.get('platforms', []))} | backend: {manifest.get('backend')} "
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
        st = s.get("states", {})
        impl = sum(1 for k in STATE_KEYS if isinstance(st.get(k), dict) and "na" not in st[k])
        na = sum(1 for k in STATE_KEYS if isinstance(st.get(k), dict) and "na" in st[k])
        t = tasks.get(s["id"], {})
        L.append(f"| {s['id']} | {s.get('priority', '')} | {emoji.get(t.get('status'), '⬜ todo')} "
                 f"| {impl}/{na} | {t.get('blocker') or '—'} |")
    L.append("")

    # 인간 승인 대기 큐
    pend = [d for d in decisions if d.get("status") == "pending"]
    L.append(f"## 인간 승인 대기 ({len(pend)})")
    L.append("")
    if not pend:
        L.append("_대기 중인 결정 없음._")
    else:
        for d in pend:
            L.append(f"- **[{d.get('gate')}] {d.get('id')} — {d.get('decision')}**")
            L.append(f"  - 추천: {d.get('recommendation')}")
            L.append(f"  - 리스크: {d.get('risk')} | 되돌리기: {d.get('reversible')} | 영향: {', '.join(d.get('impacts', []))}")
    L.append("")

    out = ROOT / "STATUS.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}  (validate={'PASS' if validate_ok else 'FAIL'})")


if __name__ == "__main__":
    main()
