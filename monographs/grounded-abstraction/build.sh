#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
for pass in 1 2 3; do
  pdflatex -halt-on-error -interaction=nonstopmode -output-directory=build Grounded_Abstraction_v1.0.0.tex > "build/pass_${pass}.stdout.log"
done
cp build/Grounded_Abstraction_v1.0.0.pdf .
