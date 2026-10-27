#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "usage: $0 /path/to/Komorebi_Portable_Lean_4.34.0-rc2" >&2
  exit 64
fi
R=$(cd "$1" && pwd)
HERE=$(cd "$(dirname "$0")/.." && pwd)
W="$R/workspace"
export TERM=${TERM:-xterm}
mkdir -p "$W/Komorebi" "$W/.lake/build/lib/lean/Komorebi"
cp "$HERE/deps/GeneralScalarGaussianConditioning.lean" "$W/Komorebi/GeneralScalarGaussianConditioning.lean"
cp "$HERE/deps/BayesianMultiscaleKalmanPosteriorPerturbation.lean" "$W/Komorebi/BayesianMultiscaleKalmanPosteriorPerturbation.lean"
cd "$W"
"$R/toolchain/bin/lake" env lean -DwarningAsError=true -o Komorebi/GeneralScalarGaussianConditioning.olean Komorebi/GeneralScalarGaussianConditioning.lean
cp Komorebi/GeneralScalarGaussianConditioning.olean .lake/build/lib/lean/Komorebi/
"$R/toolchain/bin/lake" env lean -DwarningAsError=true -o Komorebi/BayesianMultiscaleKalmanPosteriorPerturbation.olean Komorebi/BayesianMultiscaleKalmanPosteriorPerturbation.lean
for ext in olean olean.server olean.private ir ir.sig; do
  if [ -f "Komorebi/BayesianMultiscaleKalmanPosteriorPerturbation.$ext" ]; then
    cp "Komorebi/BayesianMultiscaleKalmanPosteriorPerturbation.$ext" .lake/build/lib/lean/Komorebi/
  fi
done
"$R/toolchain/bin/lake" env lean -DwarningAsError=true "$HERE/src/ScalarGaussianPosteriorPerturbationBridge.lean"
