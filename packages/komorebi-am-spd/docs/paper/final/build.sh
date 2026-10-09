#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
latexmk -pdf -interaction=nonstopmode -halt-on-error Adaptive_Multiscale_Singular_Packet_Decomposition_Final.tex
