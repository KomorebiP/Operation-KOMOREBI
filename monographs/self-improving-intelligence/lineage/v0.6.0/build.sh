#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Self_Improving_Intelligence_v0.6.0.tex
cp build/Self_Improving_Intelligence_v0.6.0.pdf Self_Improving_Intelligence_v0.6.0.pdf
