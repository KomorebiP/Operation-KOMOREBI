#!/usr/bin/env bash
# Downloads an explicitly versioned upstream installer. The Lean compiler and
# every dependency revision are checked separately by bootstrap_lake_kit.py.
set -euo pipefail
: "${RUNNER_TEMP:?RUNNER_TEMP must identify temporary build storage}"
: "${ELAN_HOME:?ELAN_HOME must identify the temporary elan installation}"
: "${GITHUB_PATH:?This installer is intended for GitHub Actions}"
installer_dir="$(mktemp -d "$RUNNER_TEMP/lsm-elan-installer.XXXXXX")"
trap 'rm -rf "$installer_dir"' EXIT
installer_url='https://github.com/leanprover/elan/releases/download/v4.2.4/elan-x86_64-unknown-linux-gnu.tar.gz'
curl --fail --location --retry 3 --proto '=https' --tlsv1.2 \
  "$installer_url" --output "$installer_dir/elan.tar.gz"
sha256sum "$installer_dir/elan.tar.gz" > "$installer_dir/download.sha256"
mkdir -p "${LSM_CI_OUTPUT:-$RUNNER_TEMP/lsm-ci}"
cp "$installer_dir/download.sha256" "${LSM_CI_OUTPUT:-$RUNNER_TEMP/lsm-ci}/elan-download.sha256"
# Expected digest retrieved from the official elan v4.2.4 release metadata.
expected_installer_sha256='42b94d4244e8353142c456ec0e4ca6528fd898a6c604d4059f494e706e431f63'
printf '%s  %s\n' "$expected_installer_sha256" "$installer_dir/elan.tar.gz" | sha256sum --check --status
tar -xzf "$installer_dir/elan.tar.gz" -C "$installer_dir"
"$installer_dir/elan-init" -y --default-toolchain none
printf '%s\n' "$ELAN_HOME/bin" >> "$GITHUB_PATH"
