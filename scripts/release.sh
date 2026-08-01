#!/usr/bin/env bash
#
# Release a new LostDock version.
#
# Usage:
#   ./scripts/release.sh            # bump automatically from conventional commits
#   ./scripts/release.sh 0.2.0      # force a specific version
#
# Steps:
#   1. Sanity checks (clean tree, master branch).
#   2. Compute the next version (git-cliff --bumped-version or explicit arg).
#   3. Bump version in pyproject.toml and src/lostdock/__init__.py.
#   4. Run the test suite.
#   5. Regenerate CHANGELOG.md with git-cliff.
#   6. Commit and create an annotated tag vX.Y.Z.
#   7. Print the commands to push commit + tag (which triggers the CI release).

set -euo pipefail

cd "$(dirname "$0")/.."

GIT_CLIFF="${GIT_CLIFF:-git-cliff}"

# --- Sanity checks -----------------------------------------------------------

if [[ -n "$(git status --porcelain)" ]]; then
    echo "error: working tree is dirty; commit or stash changes first" >&2
    exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" != "master" ]]; then
    echo "error: releases must be cut from master, currently on '$BRANCH'" >&2
    exit 1
fi

if ! command -v "$GIT_CLIFF" >/dev/null 2>&1; then
    echo "error: git-cliff is required (cargo install git-cliff)" >&2
    exit 1
fi

# --- Determine version -------------------------------------------------------

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
    VERSION="$("$GIT_CLIFF" --config cliff.toml --bumped-version | sed 's/^v//')"
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "error: invalid version '$VERSION', expected X.Y.Z" >&2
    exit 1
fi

echo "Releasing version: $VERSION"

# --- Bump version in pyproject.toml and __init__.py --------------------------

if [[ "$(uname -s)" == "Darwin" ]]; then
    SED_INPLACE=(-i "")
else
    SED_INPLACE=(-i)
fi

sed "${SED_INPLACE[@]}" -E "s/^(version = \")[0-9]+\.[0-9]+\.[0-9]+(\")/\1$VERSION\2/" pyproject.toml
sed "${SED_INPLACE[@]}" -E "s/^(__version__ = \")[0-9]+\.[0-9]+\.[0-9]+(\")/\1$VERSION\2/" src/lostdock/__init__.py

echo "Bumped pyproject.toml and src/lostdock/__init__.py to $VERSION"

# --- Run tests ----------------------------------------------------------------

uv run pytest -q

# --- Regenerate changelog -----------------------------------------------------

"$GIT_CLIFF" --config cliff.toml --unreleased --tag "v$VERSION" -o CHANGELOG.md

# --- Commit and tag ------------------------------------------------------------

git add pyproject.toml src/lostdock/__init__.py CHANGELOG.md cliff.toml
git commit -m "chore(release): bump version to $VERSION"

git tag -a "v$VERSION" -m "LostDock v$VERSION"

echo
echo "Committed and tagged v$VERSION."
echo
echo "Push to trigger the CI release:"
echo "  git push origin master"
echo "  git push origin v$VERSION"
