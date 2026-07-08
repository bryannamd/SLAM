# SLAM 사용법 데모 — `vhs docs/demo.tape`로 재생성 (저장소 루트에서 실행)
# 산출물: docs/demo.gif

Output docs/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1180
Set Height 720
Set Padding 22
Set Theme "Dracula"
Set TypingSpeed 45ms

Sleep 600ms

# 1) 완성된 예시 — 출시 게이트 통과
Type "# 1. 완성된 예시를 검사 → 출시 게이트 PASS"
Enter
Sleep 700ms
Type "python3 scripts/validate.py --root examples/_complete-min --gate launch"
Enter
Sleep 2.2s

# 2) 상태 대시보드 자동 생성
Type "# 2. 대시보드 자동 생성 (STATUS.md)"
Enter
Sleep 700ms
Type "python3 scripts/status.py --root examples/_complete-min && sed -n '1,9p' examples/_complete-min/STATUS.md"
Enter
Sleep 2.6s

# 3) 미완성 앱 — 게이트가 FAIL로 잡아준다
Type "# 3. 미완성 앱은 출시 게이트가 FAIL로 잡는다"
Enter
Sleep 700ms
Type "python3 scripts/validate.py --root examples/sip-reminder --gate launch"
Enter
Sleep 3s

# 4) 내 앱 만들기 — 빈 템플릿이 남은 할 일을 알려준다
Type "# 4. 내 앱: 빈 템플릿 검사 → 채울 항목이 체크리스트로"
Enter
Sleep 700ms
Type "python3 scripts/validate.py | tail -6"
Enter
Sleep 3s
