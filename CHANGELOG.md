## [0.1.1] - 2026-08-01

### Features

- Initial release of lostdock dorking tool
- Register bing engine in the UI dropdown (closes #3)
- Wire on_result and on_export hooks (closes #4)
- Add google-chrome engine that drives real Chrome via CDP
- Tag-driven release pipeline with git-cliff

### Bug Fixes

- Render missing search toolbar (closes #1)
- Retry with backoff on 429 and actionable error (closes #2)
- Run URL re-check off the UI thread and persist results (closes #5)
- Annotate results by original URL and use a dedicated Status column (closes #6)

### Refactoring

- Google-chrome engine just opens the search in Chrome

### Documentation

- Fix translated README back-links after moving to i18n/

### CI

- Build linux and windows binaries on push
- Add auto github releases with binaries on push
- Checkout repo in release job so gh can resolve the repo
- Install Qt system deps for headless PySide6 tests

### Chore

- Ignore local plan.md tracking notes
- Remove redundant bot/AI-flavored comments
