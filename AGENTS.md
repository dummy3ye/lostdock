# AGENTS.md

## Issue-Driven Workflow

Before doing any work, follow this rule:

1. If the task is listed as an issue in `local/plan.md` OR the user asks you to fix something that IS an issue, create a GitHub issue for it (`gh issue create`) if one does not already exist.
2. Complete the fix.
3. Verify your work (tests / UI smoke check).
4. Commit with a conventional commit message referencing the issue.
5. Close the issue (`gh issue close`).

## Pushing to GitHub

1. BEFORE EVERY PUSH ASK USER FOR CLARIFICALTION (y/N/edit)
2. Commit with a conventional commit message (see below).
3. Push to the remote:

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
