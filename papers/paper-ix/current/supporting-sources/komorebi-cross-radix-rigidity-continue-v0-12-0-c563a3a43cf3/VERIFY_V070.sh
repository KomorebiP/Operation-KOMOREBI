#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "usage: bash VERIFY_V070.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2" >&2
  exit 2
fi
ROOT="$(cd "$(dirname "$0")" && pwd)"
R="$(cd "$1" && pwd)"
export PATH="$R/toolchain/bin:$PATH"
PKG="$R/workspace/.lake/packages"
[ -d "$PKG" ] || { echo "pinned package cache missing: $PKG" >&2; exit 2; }
cd "$ROOT"
sha256sum -c SHA256_SOURCES_V060.txt >/dev/null
mkdir -p "$ROOT/.lake"
backup=''
if [ -e "$ROOT/.lake/packages" ]; then
  backup="$(mktemp -d)/packages"
  mv "$ROOT/.lake/packages" "$backup"
fi
ln -s "$PKG" "$ROOT/.lake/packages"
OUT="$(mktemp -d)"
cleanup() {
  rm -rf "$OUT"
  rm -f "$ROOT/.lake/packages"
  if [ -n "$backup" ] && [ -e "$backup" ]; then mv "$backup" "$ROOT/.lake/packages"; fi
}
trap cleanup EXIT
mods=(
  CrossRadixWidthOperatorBasis
  CrossRadixCyclotomicClosure
  CrossRadixReynoldsDFT
  CrossRadixAffineDecoder
  CrossRadixReynoldsAverage
  CrossRadixRankNullity
  CrossRadixBellCommonHull
  CrossRadixV07AxiomAudit
)
for m in "${mods[@]}"; do
  echo "=== $m ==="
  LEAN_PATH="$OUT" lake env lean -DwarningAsError=true -o "$OUT/${m}.olean" "$ROOT/src/${m}.lean"
done
if grep -RInE '\b(sorry|admit)\b|^[[:space:]]*axiom\b' "$ROOT/src" --include='*.lean'; then
  echo "placeholder/custom-axiom scan FAILED" >&2
  exit 1
fi
echo "VERIFY_V070 PASS"
