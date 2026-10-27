# Computational supplement

This directory reproduces the exact finite computations used in the paper.

## Runtime note

The complete `run_all.sh` driver recompiles and reruns several exhaustive finite searches. On a typical multicore workstation it may require several minutes. Each program can also be run independently using the commands below, and every result is compared with a frozen expected output.

## Programs

- `small_dimensions_f2.cpp`: complete no-defect search over `F_2` in dimensions 2 through 5.
- `circuit_census_f2.cpp`: complete restricted BFS in `U_6(F_2)` and exact ambient radius-four right-coset meet in the middle.
- `circuit_packet_tests.py`: independent generation of the twenty catalytic motifs, exact comparison with the census, Green coefficients, five endpoint signature packets, and the Pasch incidence check.
- `small_dimensions_q3.cpp`: complete no-defect search over `F_3` in dimensions 2 through 4.
- `q3_n5_census.cpp`: complete dimension-five ternary census.
- `canonical_q3_test.cpp`, `canonical_q5_test.cpp`: independent exact audits of the universal atom over `F_3` and `F_5`.
- `higher_family_tests.py`: symbolic and modular audits of the snapshot circuits, interval-tree potential, tensor certificate, recursive lift, connected higher cases, and the 21-dimensional rate optimizer.
- `resource_generalization_tests.py`: exact integer checks of total unimodularity for the `M(K_4)` carrier representation, its four triangle circuits, the two-upper-gate formulas through dimension 100, and the weighted-penalty identities.
- `further_generalization_tests.py`: audits the displayed six- and seven-gate words over `Z/4Z`, `Z/6Z`, and `Z/8Z`; verifies rank-one, bandwidth-one snapshot paths over `F_2`, `F_3`, and `F_5`; and checks the finite-field density and stable tensor normalization formulas.
- `small_snapshot_exact.cpp`: exact bidirectional ambient-distance certificates for the selected targets in dimensions 7, 8, and 9 over `F_2`.

The `expected/` directory contains the frozen outputs used for comparison. The exact searches and algebraic checks use no floating-point decisions or internet access. The displayed decimal tensor coefficient is only a formatted value of the exact expression `8/(21*log2(21))`.

## One-command reproduction

```bash
./run_all.sh
```

Requirements: `g++` with C++20 support, Python 3.10 or newer, and standard Unix utilities.
