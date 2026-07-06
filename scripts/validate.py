#!/usr/bin/env python3
"""validate.py — spec/·state/의 검증 커널 (에이전트와 무관하게 도는 진실 판정기).

자율 파이프라인의 게이트: 이 스크립트가 green이어야 다음 단계로 간다.
에이전트가 '그럴듯한 쓰레기'를 만들어도 여기서 걸린다.

사용:
  python3 scripts/validate.py              # 루트 spec/ 검증
  python3 scripts/validate.py --root examples/sip-reminder  # 하위 프로젝트 검증
  python3 scripts/validate.py --gate evidence   # Evidence 게이트: 증거 2종·kill 기준을 FAIL로 강제
  python3 scripts/validate.py --gate scope      # Scope 게이트: p0≤5·out_of_scope 강제
  python3 scripts/validate.py --gate brand_ux   # Brand/UX 게이트: 대비 쌍 존재 강제
  python3 scripts/validate.py --gate launch     # 출시 블로커까지 검사
  python3 scripts/validate.py --selftest     # 대비 계산 자가검증
  python3 scripts/validate.py --strict       # 경고도 실패로 취급
종료코드: 0 통과 / 1 실패
"""
import sys
import re
import json
import pathlib
import yaml

# 검증 대상 프로젝트 루트(기본=repo 루트). --root 로 examples/sip-reminder 등을 가리킨다.
ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE_KEYS = ["loading", "empty", "error", "success", "offline", "permission_denied"]
PLACEHOLDER = re.compile(r"\[[^\]]*\]|___|TODO|FIXME")

errors = []
warns = []
def err(m): errors.append(m)
def warn(m): warns.append(m)


def enum_ok(v, allowed):
    """v가 허용 문자열 집합에 속하는가 — 비문자열(매핑·리스트 등 unhashable 포함)도 안전하게 False."""
    return isinstance(v, str) and v in allowed


def req_list(container, key, label):
    """container[key]를 리스트로 요구. 없으면 [], 리스트가 아니면(false·0·문자열 포함) FAIL + []."""
    v = container.get(key)
    if v is None:
        return []
    if not isinstance(v, list):
        err(f"{label}: 리스트여야 함")
        return []
    return v


def load_yaml(rel):
    p = ROOT / rel
    if not p.exists():
        err(f"{rel} 없음")
        return None
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(f"{rel} YAML 파싱 실패: {e}")
        return None
    if not data:  # 빈 파일/빈 매핑 → 검사 스킵으로 게이트가 뚫리는 것을 막는다
        err(f"{rel} 비어 있음")
        return None
    if not isinstance(data, dict):
        err(f"{rel} 최상위는 매핑이어야 함")
        return None
    return data


def load_json(rel):
    p = ROOT / rel
    if not p.exists():
        err(f"{rel} 없음")
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{rel} JSON 파싱 실패: {e}")
        return None
    if not data:
        err(f"{rel} 비어 있음")
        return None
    if not isinstance(data, dict):
        err(f"{rel} 최상위는 매핑이어야 함")
        return None
    return data


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
    global ROOT
    if "--root" in sys.argv:
        i = sys.argv.index("--root")
        ROOT = pathlib.Path(sys.argv[i + 1]).resolve()
    gate = None
    if "--gate" in sys.argv:
        i = sys.argv.index("--gate")
        gate = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        # risk 게이트는 기계 검사 없음(사람 판단 전용) — 이름만 허용, 전역 검증만 돈다
        if gate not in {"evidence", "scope", "brand_ux", "risk", "launch"}:
            print(f"알 수 없는 게이트: {gate!r} (evidence|scope|brand_ux|risk|launch)")
            return 1
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
                   ("screens", screens), ("architecture", load_yaml("spec/architecture.yaml")),
                   ("monetization", monet), ("compliance", compliance)]:
        if ob is not None:
            check_placeholders(nm, ob)

    # manifest
    if manifest:
        for k in ["name", "one_liner", "platforms", "backend", "audience",
                  "risk_class", "monetization_model"]:
            if k not in manifest:
                err(f"manifest: 필수 키 없음: {k}")
        plats = manifest.get("platforms")
        if not isinstance(plats, list) or not plats:
            err("manifest.platforms: 비어 있지 않은 리스트여야 함")
        else:
            for p in plats:
                if not enum_ok(p, {"ios", "android", "web"}):
                    err(f"manifest.platforms 값 오류: {p!r}")
        # manifest.backend는 bool(서버 유무). architecture.yaml stack.backend(문자열 none|firebase|...)와 별개 키.
        if "backend" in manifest and not isinstance(manifest.get("backend"), bool):
            err("manifest.backend: true/false여야 함(문자열 backend는 architecture.stack.backend)")
        if not enum_ok(manifest.get("risk_class"), {"low", "medium", "high"}):
            err(f"manifest.risk_class 값 오류: {manifest.get('risk_class')!r}")
        if not enum_ok(manifest.get("audience"), {"general", "minors"}):
            err(f"manifest.audience 값 오류: {manifest.get('audience')!r}")
        if not enum_ok(manifest.get("monetization_model"), {"free", "freemium", "subscription", "iap", "ads"}):
            err(f"manifest.monetization_model 값 오류: {manifest.get('monetization_model')!r}")

    # evidence — 전역에선 warn(작성 초기 소음 방지), --gate evidence에선 FAIL로 승격
    if evidence:
        ev = err if gate == "evidence" else warn
        for k in ["problem", "target_user", "acquisition_channel",
                  "value_hypothesis", "willingness_hypothesis"]:
            if not str(evidence.get(k) or "").strip():
                ev(f"evidence: 필수 필드 비어 있음: {k}")
        evs = evidence.get("evidence")
        if not evs:
            ev("evidence: 실증거가 비어 있음(가상 페르소나 금지 — 실제 증거 2종 이상)")
        elif not isinstance(evs, list):
            ev("evidence: evidence는 리스트여야 함")
        elif len(evs) < 2:
            ev("evidence: 증거가 2종 미만")
        kc = evidence.get("kill_criteria")
        if not kc:
            ev("evidence: kill_criteria 필수(언제 중단할지 없으면 좀비 앱 위험)")
        elif not isinstance(kc, list):
            ev("evidence: kill_criteria는 리스트여야 함")

    # --gate scope — MVP 범위 강제
    if gate == "scope" and product:
        feats = product.get("features")
        feats = feats if isinstance(feats, dict) else {}
        p0 = feats.get("p0") or []
        if not p0:
            err("[scope] features.p0 비어 있음(MVP 필수 기능 없음)")
        elif not isinstance(p0, list):
            err("[scope] features.p0는 리스트여야 함")
        elif len(p0) > 5:
            err(f"[scope] p0가 5개 초과({len(p0)}개) — MVP 범위 아님")
        oos = product.get("out_of_scope")
        if not oos:
            err("[scope] out_of_scope 비어 있음(scope creep 방지 필수)")
        elif not isinstance(oos, list):
            err("[scope] out_of_scope는 리스트여야 함")

    # screens — 6상태 계약
    screen_ids = []
    if screens and isinstance(screens.get("screens"), list):
        for s in screens["screens"]:
            if not isinstance(s, dict):
                err(f"screens: 항목이 매핑이 아님: {s!r}")
                continue
            sid = s.get("id", "?")
            screen_ids.append(sid)
            if s.get("priority") == "p0" and not s.get("acceptance"):
                err(f"screens[{sid}]: p0 화면은 acceptance 필수")
            st = s.get("states", {})
            if not isinstance(st, dict):
                err(f"screens[{sid}].states: 매핑이어야 함")
                continue
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
    if events and not isinstance(events.get("events"), list):
        err("events: events 리스트 없음")
    elif events:
        for e in events["events"]:
            if not isinstance(e, dict):
                err(f"events: 항목이 매핑이 아님: {e!r}")
                continue
            if not (isinstance(e.get("name"), str) and e.get("name")) or not e.get("trigger"):
                err(f"events: name(문자열)/trigger 누락: {e}")
            else:
                event_names.add(e["name"])

    # metrics — 이벤트 참조 정합성 + 모바일 지표 존재
    if metrics:
        for m in req_list(metrics, "product", "metrics.product"):
            if not isinstance(m, dict):
                err(f"metrics.product: 항목이 매핑이 아님: {m!r}")
                continue
            for u in req_list(m, "uses", f"metrics.product[{m.get('key')}].uses"):
                if not isinstance(u, str):
                    err(f"metrics.product[{m.get('key')}]: uses 항목이 문자열이 아님: {u!r}")
                elif u not in event_names:
                    err(f"metrics.product[{m.get('key')}]: 미정의 이벤트 참조: {u}")
        client_keys = {c.get("key") for c in req_list(metrics, "client", "metrics.client")
                       if isinstance(c, dict) and isinstance(c.get("key"), str)}
        if "cold_start" not in client_keys:
            warn("metrics.client: 모바일 고유 지표(cold_start 등) 권장")

    # monetization ↔ manifest 정합
    if monet and manifest and monet.get("model") != manifest.get("monetization_model"):
        err(f"monetization.model({monet.get('model')}) != manifest.monetization_model({manifest.get('monetization_model')})")

    # monetization — 유료 모델이면 수익 필수 필드가 있어야 한다(수익 가설 없는 유료 전환 방지)
    if monet and monet.get("model") not in (None, "free"):  # 튜플 멤버십(==) — unhashable 값도 안전
        pf = monet.get("paid_features")
        if not pf:
            err("monetization: 유료 모델인데 paid_features 비어 있음")
        elif not isinstance(pf, list):
            err("monetization: paid_features는 리스트여야 함")
        pr = monet.get("pricing")
        if not pr:
            err("monetization: 유료 모델인데 pricing 없음(currency·base_price·model_type)")
        elif not isinstance(pr, dict):
            err("monetization: pricing은 매핑이어야 함")
        else:
            for k in ["currency", "base_price", "model_type"]:
                if not str(pr.get(k) or "").strip():
                    err(f"monetization.pricing: 필수 키 없음: {k}")
        if not str(monet.get("paywall_trigger") or "").strip():
            err("monetization: 유료 모델인데 paywall_trigger 미정의")

    # tokens — 대비 검사
    if tokens:
        for g in ["color", "typography", "spacing"]:
            if g not in tokens:
                err(f"tokens.json: 그룹 없음: {g}")
        if gate == "brand_ux" and not tokens.get("contrast_pairs"):
            err("[brand_ux] tokens.contrast_pairs 비어 있음 — 대비 검사 불가")
        colors = tokens.get("color", {})
        if not isinstance(colors, dict):
            err("tokens.color: 매핑이어야 함")
            colors = {}
        for pair in req_list(tokens, "contrast_pairs", "tokens.contrast_pairs"):
            if not isinstance(pair, dict):
                err(f"tokens.contrast_pairs: 항목이 매핑이 아님: {pair!r}")
                continue
            fg, bg, role = pair.get("fg"), pair.get("bg"), pair.get("role", "normal")
            if not isinstance(fg, str) or not isinstance(bg, str) or fg not in colors or bg not in colors:
                err(f"tokens.contrast_pairs: 미정의 색 {fg!r}/{bg!r}")
                continue
            fgv, bgv = colors[fg], colors[bg]
            if not all(isinstance(v, str) and re.fullmatch(r"#?[0-9A-Fa-f]{6}", v) for v in (fgv, bgv)):
                err(f"tokens 색상 형식 오류(#RRGGBB 필요): {fg}={fgv!r} / {bg}={bgv!r}")
                continue
            ratio = contrast(fgv, bgv)
            need = 3.0 if role == "large" else 4.5
            if ratio < need:
                err(f"tokens 대비 미달: {fg}/{bg} = {ratio:.2f}:1 (필요 {need}:1, {role})")

    # state/tasks
    if tasks:
        for t in req_list(tasks, "tasks", "tasks"):
            if not isinstance(t, dict):
                err(f"tasks: 항목이 매핑이 아님: {t!r}")
                continue
            if t.get("screen") not in screen_ids:
                err(f"tasks: screens에 없는 화면: {t.get('screen')}")
            if not enum_ok(t.get("status"), {"todo", "in_progress", "built", "verified", "blocked"}):
                err(f"tasks[{t.get('screen')}]: status 값 오류: {t.get('status')!r}")

    # decisions
    if decisions:
        for d in req_list(decisions, "decisions", "decisions"):
            if not isinstance(d, dict):
                err(f"decisions: 항목이 매핑이 아님: {d!r}")
                continue
            if not enum_ok(d.get("status"), {"pending", "approved", "rejected"}):
                err(f"decisions[{d.get('id')}]: status 오류: {d.get('status')!r}")

    # --- Launch 게이트 전용 ---
    if gate == "launch":
        if compliance:
            for b in req_list(compliance, "blockers", "[launch] compliance.blockers"):
                if not isinstance(b, dict):
                    err(f"[launch] blockers 항목이 매핑이 아님: {b!r}")
                    continue
                if not b.get("resolved"):
                    err(f"[launch] 미해소 블로커: {b.get('id')} — {b.get('desc')}")
            if manifest and manifest.get("audience") == "minors":
                mn = compliance.get("minors", {})
                if not isinstance(mn, dict):
                    err("[launch] compliance.minors: 매핑이어야 함")
                    mn = {}
                if not mn.get("applicable"):
                    err("[launch] audience=minors인데 compliance.minors.applicable=false")
                for k in ["coppa", "parental_consent"]:
                    if "N/A" in str(mn.get(k, "N/A")):
                        err(f"[launch] minors.{k} 미작성(COPPA 필수)")
        if decisions:
            dl = decisions.get("decisions")
            pend = [d.get("id") for d in (dl if isinstance(dl, list) else [])
                    if isinstance(d, dict) and d.get("gate") == "launch" and d.get("status") == "pending"]
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
