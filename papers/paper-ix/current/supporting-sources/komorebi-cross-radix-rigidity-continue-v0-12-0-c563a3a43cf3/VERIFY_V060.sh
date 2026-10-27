#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "usage: bash VERIFY_V060.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2" >&2
  exit 2
fi
ROOT="$(cd "$(dirname "$0")" && pwd)"
R="$(cd "$1" && pwd)"
export PATH="$R/toolchain/bin:$PATH"
PKG="$R/workspace/.lake/packages"
if [ ! -d "$PKG" ]; then
  echo "pinned runtime package cache not found: $PKG" >&2
  exit 2
fi
cd "$ROOT"
sha256sum -c SHA256_SOURCES_V050.txt >/dev/null
mkdir -p "$ROOT/.lake"
created_link=0
if [ ! -e "$ROOT/.lake/packages" ]; then
  ln -s "$PKG" "$ROOT/.lake/packages"
  created_link=1
fi
OUT="$(mktemp -d)"
cleanup() {
  rm -rf "$OUT"
  if [ "$created_link" -eq 1 ]; then rm -f "$ROOT/.lake/packages"; fi
}
trap cleanup EXIT
mods=(
  CrossRadixWidthOperatorBasis
  CrossRadixCyclotomicClosure
  CrossRadixReynoldsDFT
  CrossRadixAffineDecoder
  CrossRadixReynoldsAverage
  CrossRadixRankNullity
  CrossRadixV06AxiomAudit
)
for m in "${mods[@]}"; do
  echo "=== $m ==="
  LEAN_PATH="$OUT" lake env lean -DwarningAsError=true -o "$OUT/${m}.olean" "$ROOT/src/${m}.lean"
done
if grep -RInE '\b(sorry|admit)\b|^[[:space:]]*axiom\b' "$ROOT/src" --include='*.lean'; then
  echo "placeholder/custom-axiom scan FAILED" >&2
  exit 1
fi
echo "VERIFY_V060 PASS"
