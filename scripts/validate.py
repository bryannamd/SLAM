#!/usr/bin/env python3
"""validate.py — spec/·state/의 검증 커널 (에이전트와 무관하게 도는 진실 판정기).

자율 파이프라인의 게이트: 이 스크립트가 green이어야 다음 단계로 간다.
에이전트가 '그럴듯한 쓰레기'를 만들어도 여기서 걸린다.

플랫폼 프로파일(manifest.platform_profile: mobile|web|hybrid)에 따라 상태 계약·권장 지표가 분기한다.
프로파일 미지정 시 platforms로 폴백(web 전용→web, 그 외→mobile)하고 명시를 권장(warn)한다.

사용:
  python3 scripts/validate.py              # 루트 spec/ 검증
  python3 scripts/validate.py --root examples/sip-reminder  # 하위 프로젝트 검증
  python3 scripts/validate.py --gate evidence   # Evidence 게이트: 증거 2종·kill 기준을 FAIL로 강제
  python3 scripts/validate.py --gate scope      # Scope 게이트: p0≤5·out_of_scope 강제
  python3 scripts/validate.py --gate brand_ux   # Brand/UX 게이트: 대비 쌍 존재 강제
  python3 scripts/validate.py --gate launch     # 출시: 블로커 0 + 전 화면 verified(+verify_evidence)/launch_scope 제외 + pending 결정 0 + launch 승인 결정 존재
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
# 상태 계약은 플랫폼 프로파일별로 분기한다. 공통 4 + 프로파일 추가분.
STATE_COMMON = ["loading", "empty", "error", "success"]
STATE_MOBILE = ["offline", "permission_denied"]   # 모바일 고유(네트워크·OS 권한)
STATE_WEB = ["route_404", "auth_required"]          # 웹 고유(라우팅·세션)
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


def state_keys_for(profile):
    """프로파일별 요구 상태 키. mobile=공통+모바일2 / web=공통+웹2 / hybrid=전부."""
    if profile == "web":
        return STATE_COMMON + STATE_WEB
    if profile == "hybrid":
        return STATE_COMMON + STATE_MOBILE + STATE_WEB
    return STATE_COMMON + STATE_MOBILE  # mobile(기본)


def resolve_profile(manifest):
    """manifest.platform_profile를 반환. 없으면 platforms로 폴백(web 전용→web, 그 외→mobile) + warn."""
    prof = manifest.get("platform_profile") if manifest else None
    if prof is not None:
        if enum_ok(prof, {"mobile", "web", "hybrid"}):
            return prof
        err(f"manifest.platform_profile 값 오류: {prof!r} (mobile|web|hybrid)")
        return "mobile"
    plats = manifest.get("platforms") if manifest else None
    if isinstance(plats, list) and plats and all(p == "web" for p in plats):
        fallback = "web"
    else:
        fallback = "mobile"
    warn(f"manifest: platform_profile 미지정 — platforms 기반 '{fallback}'로 폴백(platform_profile 명시 권장)")
    return fallback


def resolve_deploy_target(manifest, profile):
    """manifest.deploy_target을 반환(선택 필드). 없으면 프로파일 폴백(mobile→app_store/web→web_host/hybrid→both)."""
    dt = manifest.get("deploy_target") if manifest else None
    if dt is not None:
        if enum_ok(dt, {"app_store", "web_host", "both"}):
            return dt
        err(f"manifest.deploy_target 값 오류: {dt!r} (app_store|web_host|both)")
    return {"mobile": "app_store", "web": "web_host", "hybrid": "both"}[profile]


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
    # 프로파일별 상태 키 계약
    assert state_keys_for("mobile") == ["loading", "empty", "error", "success", "offline", "permission_denied"]
    assert state_keys_for("web") == ["loading", "empty", "error", "success", "route_404", "auth_required"]
    assert set(state_keys_for("hybrid")) == set(STATE_COMMON + STATE_MOBILE + STATE_WEB)
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
                   ("monetization", monet), ("compliance", compliance),
                   ("tokens", tokens), ("tasks", tasks), ("decisions", decisions)]:
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

    # 플랫폼 프로파일 — 상태 계약·권장 지표·출시 표현이 여기서 갈린다.
    profile = resolve_profile(manifest)
    deploy_target = resolve_deploy_target(manifest, profile)

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

    # screens — 상태 계약(프로파일별 상태 키 집합)
    profile_state_keys = state_keys_for(profile)
    screen_ids = []
    screen_priority = {}   # sid → priority (launch 게이트의 p0 제외 차단에서 참조)
    if screens and isinstance(screens.get("screens"), list):
        for s in screens["screens"]:
            if not isinstance(s, dict):
                err(f"screens: 항목이 매핑이 아님: {s!r}")
                continue
            sid = s.get("id", "?")
            if not isinstance(sid, str) or not sid.strip():
                err(f"screens: id가 비어 있거나 문자열이 아님: {sid!r}")
                continue
            screen_ids.append(sid)
            screen_priority[sid] = s.get("priority")
            if s.get("priority") == "p0" and not s.get("acceptance"):
                err(f"screens[{sid}]: p0 화면은 acceptance 필수")
            st = s.get("states", {})
            if not isinstance(st, dict):
                err(f"screens[{sid}].states: 매핑이어야 함")
                continue
            for k in profile_state_keys:
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
        # 프로파일별 권장 지표: 모바일=cold_start 등, 웹=Core Web Vitals(lcp 등).
        if profile in ("mobile", "hybrid") and "cold_start" not in client_keys:
            warn("metrics.client: 모바일 고유 지표(cold_start 등) 권장")
        if profile in ("web", "hybrid"):
            web_vitals = {"lcp", "fcp", "cls", "inp", "ttfb", "fid", "core_web_vitals"}
            if not (client_keys & web_vitals):
                warn("metrics.client: 웹 고유 지표(lcp 등 Core Web Vitals) 권장")

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
    task_list = []
    if tasks:
        task_list = [t for t in req_list(tasks, "tasks", "tasks") if isinstance(t, dict)]
        for t in req_list(tasks, "tasks", "tasks"):
            if not isinstance(t, dict):
                err(f"tasks: 항목이 매핑이 아님: {t!r}")
                continue
            if t.get("screen") not in screen_ids:
                err(f"tasks: screens에 없는 화면: {t.get('screen')}")
            if not enum_ok(t.get("status"), {"todo", "in_progress", "built", "verified", "blocked"}):
                err(f"tasks[{t.get('screen')}]: status 값 오류: {t.get('status')!r}")
            if "launch_scope" in t and not isinstance(t.get("launch_scope"), bool):
                err(f"tasks[{t.get('screen')}]: launch_scope는 true/false여야 함")
            # verified는 자가 신고가 아니라 verifier 패스의 기록(verify_evidence)이 뒷받침해야 한다(AGENTS.md §5)
            if t.get("status") == "verified" and not isinstance(t.get("verify_evidence"), dict):
                warn(f"tasks[{t.get('screen')}]: verified인데 verify_evidence 없음 — launch 게이트에서 FAIL")

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
        # 출시 = 되돌리기 어려움. 어떤 게이트든 pending이 남아 있으면 GO가 아니다.
        # (rejected는 이미 해소된 결정 — 블로킹하지 않음. 연기하려면 rejected로 기록하고 사유를 남긴다.)
        dl = decisions.get("decisions") if decisions else None
        dl = dl if isinstance(dl, list) else []
        if decisions:
            pend = [d.get("id") for d in dl
                    if isinstance(d, dict) and d.get("status") == "pending"]
            if pend:
                err(f"[launch] 미해소 pending 결정: {pend} — 모든 게이트 결정이 승인/반려돼야 출시")
        # 출시 승인 결정이 실존해야 GO. pending==0만으론 `decisions: []`(빈 리스트)로 우회 가능 —
        # GATES.md #5의 "GO는 decisions.yaml에 launch 결정 approved로 기록돼야 배포된다" 계약의 기계 승격.
        if not any(isinstance(d, dict) and d.get("gate") == "launch" and d.get("status") == "approved"
                   for d in dl):
            err("[launch] launch 승인 결정 없음 — decisions.yaml에 gate:launch·status:approved 결정 필요")
        # 모든 화면이 verified(+verify_evidence)이거나 launch_scope:false(+사유)여야 출시.
        if not task_list:
            err("[launch] tasks 비어 있음 — 검증된 화면 없이 출시 불가")
        covered = {t.get("screen") for t in task_list if isinstance(t.get("screen"), str)}
        for sid in screen_ids:
            if sid not in covered:
                err(f"[launch] tasks에 진행 기록 없는 화면: {sid}")
        in_scope_verified = 0   # 출시 범위(launch_scope:false 아닌) 화면 중 verified 개수
        for t in task_list:
            sid = t.get("screen")
            if not isinstance(sid, str):
                continue  # 비문자열 screen은 위 state/tasks 검사에서 이미 FAIL
            if t.get("launch_scope") is False:
                # p0 화면은 출시 범위에서 제외 불가 — MVP 핵심 화면을 빼고 출시하는 모순을 막는다.
                if screen_priority.get(sid) == "p0":
                    err(f"[launch] tasks[{sid}]: p0 화면은 launch_scope:false로 제외 불가(MVP 핵심 화면)")
                if not str(t.get("launch_scope_reason") or "").strip():
                    err(f"[launch] tasks[{sid}]: launch_scope:false엔 launch_scope_reason 필수")
                continue
            if t.get("status") != "verified":
                err(f"[launch] 미완성 화면: {sid} (status={t.get('status')!r}) — verified 또는 launch_scope:false 필요")
                continue
            in_scope_verified += 1
            ve = t.get("verify_evidence")
            if not isinstance(ve, dict):
                err(f"[launch] tasks[{sid}]: verify_evidence 없음 — verifier 패스 기록 필수(AGENTS.md §5)")
            elif not (ve.get("validate") == "PASS" and ve.get("code_gates") == "PASS"
                      and str(ve.get("by") or "").strip()
                      and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ve.get("date") or ""))):
                err(f"[launch] tasks[{sid}]: verify_evidence 불충분(validate/code_gates=PASS + by + date=YYYY-MM-DD 필요)")
        # 출시 범위에 verified 화면이 하나도 없으면 GO 아님(전 화면 launch_scope:false 우회 차단).
        if task_list and in_scope_verified == 0:
            err("[launch] 출시 범위에 verified 화면이 없음 — 전 화면을 launch_scope:false로 제외할 수 없음")

    # --- 리포트 ---
    print("=" * 56)
    print(f"VALIDATE  gate={gate or 'all'}  profile={profile}  deploy={deploy_target}  "
          f"screens={len(screen_ids)}  events={len(event_names)}")
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
