#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BUILD="$ROOT/_build"
EXPECTED="$ROOT/expected"
rm -rf "$BUILD"
mkdir -p "$BUILD"

compile_and_check() {
  local stem="$1"
  g++ -O3 -std=c++20 "$ROOT/${stem}.cpp" -o "$BUILD/${stem}"
  "$BUILD/${stem}" > "$BUILD/${stem}.out"
  diff -u "$EXPECTED/${stem}.out" "$BUILD/${stem}.out"
  printf 'PASS %s\n' "$stem"
}

compile_and_check small_dimensions_f2
compile_and_check circuit_census_f2

cp "$ROOT/circuit_packet_tests.py" "$BUILD/"
(
  cd "$BUILD"
  python3 circuit_packet_tests.py > circuit_packet_tests.out
)
diff -u "$EXPECTED/circuit_packet_tests.out" "$BUILD/circuit_packet_tests.out"
diff -u "$EXPECTED/circuit_packet_results.json" "$BUILD/circuit_packet_results.json"
printf 'PASS circuit_packet_tests\n'

compile_and_check small_dimensions_q3
compile_and_check q3_n5_census
compile_and_check canonical_q3_test
compile_and_check canonical_q5_test

cp "$ROOT/higher_family_tests.py" "$BUILD/"
(
  cd "$BUILD"
  python3 higher_family_tests.py > higher_family_tests.out
)
diff -u "$EXPECTED/higher_family_tests.out" "$BUILD/higher_family_tests.out"
diff -u "$EXPECTED/higher_family_results.json" "$BUILD/higher_family_results.json"
printf 'PASS higher_family_tests\n'

cp "$ROOT/resource_generalization_tests.py" "$BUILD/"
(
  cd "$BUILD"
  python3 resource_generalization_tests.py > resource_generalization_tests.out
)
diff -u "$EXPECTED/resource_generalization_tests.out" "$BUILD/resource_generalization_tests.out"
diff -u "$EXPECTED/resource_generalization_results.json" "$BUILD/resource_generalization_results.json"
printf 'PASS resource_generalization_tests\n'

cp "$ROOT/further_generalization_tests.py" "$BUILD/"
(
  cd "$BUILD"
  python3 further_generalization_tests.py > further_generalization_tests.out
)
diff -u "$EXPECTED/further_generalization_tests.out" "$BUILD/further_generalization_tests.out"
diff -u "$EXPECTED/further_generalization_results.json" "$BUILD/further_generalization_results.json"
printf 'PASS further_generalization_tests\n'

compile_and_check small_snapshot_exact

printf '\nAll circuit-threshold computations match the frozen expected outputs.\n'
