#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
python3 explore.py > run_initial.log
python3 dyadic_check.py > run_dyadic.log
g++ -O3 -std=c++17 verify_eta_ntt.cpp -o verify_eta_ntt
./verify_eta_ntt > eta_ntt_results.txt
python3 check_trace_inverse.py > run_trace.log
python3 validate_results.py > run_validation.log
printf 'All finite checks completed. This is not a proof of Lehmer.\n'
