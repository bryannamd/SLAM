#!/usr/bin/env python3
"""trace.py — 스펙↔코드 드리프트 lint (advisory).

validate.py는 스펙↔스펙만 검사하고 코드를 읽지 않는다. trace.py가 그 공백을 메운다:
state/bindings.yaml의 화면↔파일 매핑을 따라 실제 코드를 읽고, 스펙이 선언한 것(구현 상태·
이벤트)이 코드에 나타나는지, 하드코딩 색이 새지 않는지 warn으로 알린다.

★ advisory — AST 백엔드 승격 전까지 블로킹 게이트로 만들지 말 것.
정규식·문자열 매칭 수준의 검출은 게임 가능하다(주석에 이름만 적어도 통과, 변수명이 우연히
겹쳐도 통과). 그래서 v1은 warn 전용이고 기본 종료코드 0이다. 사람이 눈으로 볼 신호일 뿐,
"통과=옳음"의 증거가 아니다. --strict일 때만 warn을 종료코드 1로 승격한다(CI 실험용).

검출기 3종:
  1. 하드코딩 색상 — 바인딩된 파일(token_sources 제외)의 #RRGGBB / 0xFF...... 리터럴.
  2. 선언 상태 미구현 — screens.yaml에서 na가 아닌 상태 키가 해당 화면 바인딩 파일에 안 보임.
  3. 선언 이벤트 미발화 — events.yaml의 name이 바인딩된 전체 파일 어디에도 안 보임.
명명규칙은 정규화 후 비교한다: 구분자를 지우고 소문자로 — permission_denied(스펙 snake_case)와
permissionDenied(코드 camelCase)/PermissionDenied(PascalCase)를 같은 것으로 인정한다.

사용:
  python3 scripts/trace.py                         # 루트 검사
  python3 scripts/trace.py --root examples/_complete-min
  python3 scripts/trace.py --strict                # warn을 종료코드 1로 승격
종료코드: 0 통과(warn 있어도) / 1 (--strict + warn>0)
"""
import re
import sys
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 하드코딩 색 리터럴: #RRGGBB 또는 Flutter 0xAARRGGBB(0xFF + 6 hex).
COLOR_RE = re.compile(r"#[0-9A-Fa-f]{6}\b|0x[Ff]{2}[0-9A-Fa-f]{6}")

warns = []
def warn(m): warns.append(m)


def normalize(s):
    """구분자 제거 + 소문자. permission_denied/permissionDenied/PermissionDenied → 'permissiondenied'."""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def load_yaml(path, label):
    """YAML 매핑을 읽는다. 없거나 깨졌거나 매핑이 아니면 warn + None(advisory라 멈추지 않는다)."""
    if not path.exists():
        warn(f"{label} 없음: {path.name} (드리프트 검사 일부 건너뜀)")
        return None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        warn(f"{label} YAML 파싱 실패: {e}")
        return None
    if not isinstance(data, dict):
        warn(f"{label} 최상위가 매핑이 아님")
        return None
    return data


def read_text(path):
    """파일 텍스트를 읽는다. 없으면 None."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def main():
    global ROOT
    argv = sys.argv[1:]
    if "--root" in argv:
        i = argv.index("--root")
        if i + 1 < len(argv):
            ROOT = pathlib.Path(argv[i + 1]).resolve()
    strict = "--strict" in argv

    bindings_doc = load_yaml(ROOT / "state" / "bindings.yaml", "state/bindings.yaml")
    screens_doc = load_yaml(ROOT / "spec" / "screens.yaml", "spec/screens.yaml")
    events_doc = load_yaml(ROOT / "spec" / "events.yaml", "spec/events.yaml")

    token_sources = set()
    bindings = []
    if bindings_doc:
        ts = bindings_doc.get("token_sources") or []
        if isinstance(ts, list):
            token_sources = {str(p) for p in ts}
        bd = bindings_doc.get("bindings") or []
        if isinstance(bd, list):
            bindings = [b for b in bd if isinstance(b, dict)]

    # 화면 id → 바인딩 파일(상대경로) 목록.
    files_by_screen = {}
    all_files = set()          # 이벤트 검사용: 전체 바인딩 파일의 합집합.
    for b in bindings:
        sid = b.get("screen")
        fs = b.get("files") or []
        fs = [str(f) for f in fs] if isinstance(fs, list) else []
        files_by_screen[sid] = fs
        all_files.update(fs)

    # 파일 실재 확인 + 텍스트 캐시(정규화 텍스트도 함께).
    text_cache = {}          # rel -> 원문
    norm_cache = {}          # rel -> 정규화 텍스트
    for rel in sorted(all_files):
        p = ROOT / rel
        txt = read_text(p)
        if txt is None:
            warn(f"바인딩 파일이 실재하지 않음: {rel}")
            continue
        text_cache[rel] = txt
        norm_cache[rel] = normalize(txt)

    # --- 검출기 1: 하드코딩 색상(token_sources 제외) ---
    for rel in sorted(all_files):
        if rel in token_sources or rel not in text_cache:
            continue
        hits = COLOR_RE.findall(text_cache[rel])
        if hits:
            uniq = sorted(set(hits))
            warn(f"하드코딩 색상 {len(hits)}건 in {rel}: {', '.join(uniq[:5])}"
                 f"{' …' if len(uniq) > 5 else ''} (tokens.dart의 AppColors 참조 권장)")

    # 화면 목록(screens.yaml).
    screen_list = []
    if screens_doc and isinstance(screens_doc.get("screens"), list):
        screen_list = [s for s in screens_doc["screens"] if isinstance(s, dict)]

    # --- 바인딩 미기록 화면 ---
    bound_ids = set(files_by_screen)
    for s in screen_list:
        sid = s.get("id")
        if sid not in bound_ids:
            warn(f"바인딩 미기록: 화면 '{sid}' — state/bindings.yaml에 파일 매핑이 없음"
                 f"(코드 미구현이거나 기록 누락)")

    # --- 검출기 2: 선언 상태 미구현 ---
    for s in screen_list:
        sid = s.get("id")
        if sid not in bound_ids:
            continue                      # 위에서 이미 warn.
        rels = [r for r in files_by_screen.get(sid, []) if r in norm_cache]
        joined = "".join(norm_cache[r] for r in rels)
        states = s.get("states")
        if not isinstance(states, dict):
            continue
        for key, val in states.items():
            # na로 명시한 상태는 구현 대상이 아니다 — 건너뛴다.
            if isinstance(val, dict) and "na" in val:
                continue
            if normalize(key) not in joined:
                warn(f"선언 상태 미구현: 화면 '{sid}'의 '{key}' 상태가 바인딩 코드에 없음"
                     f"({', '.join(rels) or '파일 없음'})")

    # --- 검출기 3: 선언 이벤트 미발화 ---
    all_norm = "".join(norm_cache[r] for r in sorted(norm_cache))
    if events_doc and isinstance(events_doc.get("events"), list):
        for e in events_doc["events"]:
            if not isinstance(e, dict):
                continue
            name = e.get("name")
            if not isinstance(name, str) or not name:
                continue
            if normalize(name) not in all_norm:
                warn(f"선언 이벤트 미발화: '{name}'이(가) 바인딩된 어떤 코드에도 없음")

    # --- 리포트 ---
    print("=" * 56)
    print(f"TRACE  root={ROOT.name}  screens={len(screen_list)}  "
          f"bindings={len(bindings)}  files={len(all_files)}")
    for w in warns:
        print(f"  WARN  {w}")
    print("-" * 56)
    if not warns:
        result = "CLEAN"
    elif strict:
        result = f"FAIL(strict) — WARN({len(warns)})"
    else:
        result = f"WARN({len(warns)})"
    print("RESULT:", result)
    print("=" * 56)
    return 1 if (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
