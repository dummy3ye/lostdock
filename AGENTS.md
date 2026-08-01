# AGENTS.md

## Pushing to GitHub

1. Commit with a conventional commit message (see below).
2. Push to the remote:

```bash
git add <files>
git commit -m "feat: your message"
git push origin master
```

The upstream branch is `master`.

## Conventional Commits

Always use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <description>
```

- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation only
- `style` — formatting, no code change
- `refactor` — code change that neither fixes a bug nor adds a feature
- `perf` — performance improvement
- `test` — adding or fixing tests
- `build` — build system or dependencies
- `ci` — CI configuration
- `chore` — maintenance, no production code change

Examples:

```
feat: add duckduckgo engine adapter
fix(ui): handle empty query on run
docs: translate README to spanish
test: cover proxy pool rotation
```
