#!/usr/bin/env bash
set -euo pipefail
repository="${1:?usage: publish_to_github.sh OWNER/REPO [public|private]}"
visibility="${2:-public}"
cd "$(dirname "$0")/.."
version="$(tr -d '[:space:]' < VERSION)"
command -v git >/dev/null
command -v gh >/dev/null
python3 scripts/check_release.py
python3 scripts/package_release.py
if [[ ! -d .git ]]; then
  git init
  git branch -M main
  git add .
  git commit -m "Initial release v${version}"
fi
if [[ "$visibility" == "private" ]]; then
  gh repo create "$repository" --private --source . --remote origin --push
else
  gh repo create "$repository" --public --source . --remote origin --push
fi
git tag -a "v${version}" -m "Universal Lane Transport Theorem v${version}"
git push origin "v${version}"
