#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "usage: bash VERIFY_V050.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2" >&2
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
mkdir -p "$ROOT/.lake"
created_link=0
if [ ! -e "$ROOT/.lake/packages" ]; then
  ln -s "$PKG" "$ROOT/.lake/packages"
  created_link=1
fi
cleanup() {
  if [ "$created_link" -eq 1 ]; then rm -f "$ROOT/.lake/packages"; fi
}
trap cleanup EXIT
cd "$ROOT"
mods=(
  CrossRadixWidthOperatorBasis
  CrossRadixPrimitiveSpectralAlgebra
  CrossRadixMobiusSpectralAlgebra
  CrossRadixCyclotomicClosure
  CrossRadixReynoldsDFT
  CrossRadixFiniteLCMIntersection
  CrossRadixAffineDecoder
  CrossRadixDFTShellAgreement
  CrossRadixReynoldsAverage
  CrossRadixSectionReynolds
  CrossRadixV05AxiomAudit
)
for m in "${mods[@]}"; do
  echo "=== $m ==="
  LEAN_PATH="$ROOT/src" lake env lean -DwarningAsError=true -o "/tmp/${m}.v050.verify.olean" "$ROOT/src/${m}.lean"
done
if grep -RInE '\b(sorry|admit)\b|^[[:space:]]*axiom\b' "$ROOT/src" --include='*.lean'; then
  echo "placeholder/custom-axiom scan FAILED" >&2
  exit 1
fi
echo "VERIFY_V050 PASS"
