# Contributing

Thanks for considering a contribution to LostDock.

## Getting started

```bash
git clone https://github.com/your-user/lostdock.git
cd lostdock
uv venv
uv pip install -e ".[dev]"
uv run pytest
```

## Guidelines

- **Keep it ethical.** This is a security-research and OSINT tool. Reject features whose
  primary purpose is to bypass authorization, mass-scrape personal data, or facilitate
  illegal activity.
- **Respect engine ToS.** Keep default rate limits conservative. When adding an adapter,
  ship it with a sane default limiter and anti-block handling.
- **One adapter, one interface.** New search engines must subclass `SearchEngine` in
  `src/lostdock/adapters/base.py` and register in `adapters/__init__.py`.
- **Type hints.** Use `from __future__ import annotations` and type everything.
- **No comments unless needed.** Follow the existing style; the codebase prefers
  self-documenting code and docstrings over inline comments.
- **Tests.** Add pytest coverage for any new module under `tests/`. Run the suite before
  opening a PR: `uv run pytest`.
- **READMEs.** When behaviour changes, update the English `README.md`. Translation files
  (`README.*.md`) only need the English Installation section updated.

## Code of conduct

Be respectful and constructive. Harassment or discrimination of any kind will not be
tolerated.
