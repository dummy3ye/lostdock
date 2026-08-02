## [0.2.1] - 2026-08-02

### Features

- Add logo png and ascii art
- Headless-browser fallback for Google CAPTCHA blocks
- Label chrome engine as 'chrome (pipe)' and default to it

### Bug Fixes

- Preserve search query on results round-trip
- Remove duplicate schedule save on settings accept
- Apply rate limiter jitter once per acquire
- Scope google SERP parsing to organic result blocks
- Add chrome adapter to pyinstaller hiddenimports

### Refactoring

- Consolidate query execution into run_query
- Drop dead import branch for MainWindow

### Chore

- Enable ruff, auto-fix style debt, add CI lint step


**Full Changelog**: https://github.com/dummy3ye/lostdock/compare/v0.1.1...v0.2.1
