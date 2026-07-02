#!/usr/bin/env python3
"""validate.py — spec/·state/의 검증 커널 (에이전트와 무관하게 도는 진실 판정기).

자율 파이프라인의 게이트: 이 스크립트가 green이어야 다음 단계로 간다.
에이전트가 '그럴듯한 쓰레기'를 만들어도 여기서 걸린다.

사용:
  python3 scripts/validate.py              # 전체 검증
  python3 scripts/validate.py --gate launch  # 출시 블로커까지 검사
  python3 scripts/validate.py --selftest     # 대비 계산 자가검증
  python3 scripts/validate.py --strict       # 경고도 실패로 취급
종료코드: 0 통과 / 1 실패
"""
import sys
import re
import json
import pathlib
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent  # docs/_template
STATE_KEYS = ["loading", "empty", "error", "success", "offline", "permission_denied"]
PLACEHOLDER = re.compile(r"\[[^\]]*\]|___|TODO|FIXME")

errors = []
warns = []
def err(m): errors.append(m)
def warn(m): warns.append(m)


def load_yaml(rel):
    p = ROOT / rel
    if not p.exists():
        err(f"{rel} 없음")
        return None
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(f"{rel} YAML 파싱 실패: {e}")
        return None


def load_json(rel):
    p = ROOT / rel
    if not p.exists():
        err(f"{rel} 없음")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{rel} JSON 파싱 실패: {e}")
        return None


# --- WCAG 대비 (유일한 비자명 로직) ---
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def _lum(hexstr):
    h = hexstr.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

def contrast(fg, bg):
    l1, l2 = _lum(fg), _lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def selftest():
    assert round(contrast("#000000", "#FFFFFF"), 1) == 21.0, "black/white must be 21:1"
    assert round(contrast("#FFFFFF", "#FFFFFF"), 2) == 1.0, "same color must be 1:1"
    assert contrast("#0F172A", "#FFFFFF") > 15, "textPrimary/bg should be high"
    assert contrast("#94A3B8", "#FFFFFF") < 4.5, "disabled/bg should fail AA-normal"
    print("selftest OK")


def check_placeholders(name, obj):
    """자리표시자([...]·___·TODO)가 값에 남아 있으면 미완성 → 실패."""
    def walk(v, path):
        if isinstance(v, str):
            if PLACEHOLDER.search(v):
                err(f"{name}: 자리표시자 미해결 at {path}: {v!r}")
        elif isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{path}.{k}")
        elif isinstance(v, list):
            for i, x in enumerate(v):
                walk(x, f"{path}[{i}]")
    walk(obj, name)


def main():
    gate = None
    if "--gate" in sys.argv:
        i = sys.argv.index("--gate")
        gate = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
    strict = "--strict" in sys.argv

    manifest = load_yaml("spec/manifest.yaml")
    evidence = load_yaml("spec/evidence.yaml")
    product = load_yaml("spec/product.yaml")
    screens = load_yaml("spec/screens.yaml")
    events = load_yaml("spec/events.yaml")
    metrics = load_yaml("spec/metrics.yaml")
    monet = load_yaml("spec/monetization.yaml")
    compliance = load_yaml("spec/compliance.yaml")
    tokens = load_json("spec/tokens.json")
    tasks = load_yaml("state/tasks.yaml")
    decisions = load_yaml("state/decisions.yaml")

    for nm, ob in [("manifest", manifest), ("evidence", evidence), ("product", product),
                   ("screens", screens), ("monetization", monet), ("compliance", compliance)]:
        if ob is not None:
            check_placeholders(nm, ob)

    # manifest
    if manifest:
        for k in ["name", "one_liner", "platforms", "backend", "audience",
                  "risk_class", "monetization_model"]:
            if k not in manifest:
                err(f"manifest: 필수 키 없음: {k}")
        if manifest.get("risk_class") not in {"low", "medium", "high"}:
            err(f"manifest.risk_class 값 오류: {manifest.get('risk_class')}")
        if manifest.get("audience") not in {"general", "minors"}:
            err(f"manifest.audience 값 오류: {manifest.get('audience')}")
        if manifest.get("monetization_model") not in {"free", "freemium", "subscription", "iap", "ads"}:
            err(f"manifest.monetization_model 값 오류: {manifest.get('monetization_model')}")

    # evidence
    if evidence:
        if not evidence.get("evidence"):
            warn("evidence: 실증거가 비어 있음(가상 페르소나 금지 — 실제 증거 2종 이상 권장)")
        elif len(evidence["evidence"]) < 2:
            warn("evidence: 증거가 2종 미만")
        if not evidence.get("kill_criteria"):
            err("evidence: kill_criteria 필수(언제 중단할지 없으면 좀비 앱 위험)")

    # screens — 6상태 계약
    screen_ids = []
    if screens and isinstance(screens.get("screens"), list):
        for s in screens["screens"]:
            sid = s.get("id", "?")
            screen_ids.append(sid)
            if s.get("priority") == "p0" and not s.get("acceptance"):
                err(f"screens[{sid}]: p0 화면은 acceptance 필수")
            st = s.get("states", {})
            for k in STATE_KEYS:
                if k not in st:
                    err(f"screens[{sid}]: 상태 누락: {k} (구현하거나 {{na: 사유}}로 명시)")
                    continue
                v = st[k]
                if not isinstance(v, dict):
                    err(f"screens[{sid}].{k}: 매핑이어야 함")
                elif "na" in v:
                    if not str(v.get("na", "")).strip():
                        err(f"screens[{sid}].{k}: na 사유가 비어 있음")
                elif not str(v.get("ui", "")).strip():
                    err(f"screens[{sid}].{k}: ui 정의 또는 na 사유 필요")
    else:
        err("screens: screens 리스트 없음")

    # events
    event_names = set()
    if events and isinstance(events.get("events"), list):
        for e in events["events"]:
            if not e.get("name") or not e.get("trigger"):
                err(f"events: name/trigger 누락: {e}")
            else:
                event_names.add(e["name"])

    # metrics — 이벤트 참조 정합성 + 모바일 지표 존재
    if metrics:
        for m in metrics.get("product", []) or []:
            for u in m.get("uses", []) or []:
                if u not in event_names:
                    err(f"metrics.product[{m.get('key')}]: 미정의 이벤트 참조: {u}")
        client_keys = {c.get("key") for c in (metrics.get("client") or [])}
        if "cold_start" not in client_keys:
            warn("metrics.client: 모바일 고유 지표(cold_start 등) 권장")

    # monetization ↔ manifest 정합
    if monet and manifest and monet.get("model") != manifest.get("monetization_model"):
        err(f"monetization.model({monet.get('model')}) != manifest.monetization_model({manifest.get('monetization_model')})")

    # tokens — 대비 검사
    if tokens:
        for g in ["color", "typography", "spacing"]:
            if g not in tokens:
                err(f"tokens.json: 그룹 없음: {g}")
        colors = tokens.get("color", {})
        for pair in tokens.get("contrast_pairs", []):
            fg, bg, role = pair.get("fg"), pair.get("bg"), pair.get("role", "normal")
            if fg not in colors or bg not in colors:
                err(f"tokens.contrast_pairs: 미정의 색 {fg}/{bg}")
                continue
            ratio = contrast(colors[fg], colors[bg])
            need = 3.0 if role == "large" else 4.5
            if ratio < need:
                err(f"tokens 대비 미달: {fg}/{bg} = {ratio:.2f}:1 (필요 {need}:1, {role})")

    # state/tasks
    if tasks:
        for t in tasks.get("tasks", []) or []:
            if t.get("screen") not in screen_ids:
                err(f"tasks: screens에 없는 화면: {t.get('screen')}")
            if t.get("status") not in {"todo", "in_progress", "built", "verified", "blocked"}:
                err(f"tasks[{t.get('screen')}]: status 값 오류: {t.get('status')}")

    # decisions
    if decisions:
        for d in decisions.get("decisions", []) or []:
            if d.get("status") not in {"pending", "approved", "rejected"}:
                err(f"decisions[{d.get('id')}]: status 오류: {d.get('status')}")

    # --- Launch 게이트 전용 ---
    if gate == "launch":
        if compliance:
            for b in compliance.get("blockers", []) or []:
                if not b.get("resolved"):
                    err(f"[launch] 미해소 블로커: {b.get('id')} — {b.get('desc')}")
            if manifest and manifest.get("audience") == "minors":
                mn = compliance.get("minors", {})
                if not mn.get("applicable"):
                    err("[launch] audience=minors인데 compliance.minors.applicable=false")
                for k in ["coppa", "parental_consent"]:
                    if "N/A" in str(mn.get(k, "N/A")):
                        err(f"[launch] minors.{k} 미작성(COPPA 필수)")
        if decisions:
            pend = [d["id"] for d in decisions.get("decisions", []) if d.get("gate") == "launch" and d.get("status") == "pending"]
            if pend:
                err(f"[launch] 미승인 launch 결정: {pend}")

    # --- 리포트 ---
    print("=" * 56)
    print(f"VALIDATE  gate={gate or 'all'}  screens={len(screen_ids)}  events={len(event_names)}")
    for w in warns:
        print(f"  WARN  {w}")
    for e in errors:
        print(f"  FAIL  {e}")
    fail = bool(errors) or (strict and bool(warns))
    print("-" * 56)
    print("RESULT:", "FAIL" if fail else ("PASS(+warn)" if warns else "PASS"))
    print("=" * 56)
    return 1 if fail else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    sys.exit(main())
