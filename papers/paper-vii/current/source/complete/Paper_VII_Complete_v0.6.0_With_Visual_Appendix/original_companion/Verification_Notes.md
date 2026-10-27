# Verification Notes

## Projector-Resolved Seed Calculus VII
### Quantum Seed Calculus: Symmetry Packets, Circuits, Effective Dynamics, and Quantum Spacetime

Author: Komorebi P.

## Build summary

- Final paper length: 25 pages.
- Automated tests: 22 passed.
- Figures: 19 PNG figures and 19 vector-PDF figures.
- Numerical device: CPU only.
- GPU used: no.
- Package wheel: `projector_seed_quantum-1.0.0-py3-none-any.whl`.

## Mathematical and numerical checks

The test suite verifies:

- exact basis-state generation and seed reachability;
- cyclic projector completeness, orthogonality, and tensor refinement;
- exact circuit packet-path reconstruction;
- exact symmetry blocks and controlled symmetry-breaking leakage;
- the commutator leakage inequality on the sampled time grid;
- exact Feshbach projected-resolvent reconstruction;
- moving-frame evolution with and without the required connection;
- the canonical projector-connection identity;
- Bloch-sphere projector curvature;
- Kraus completeness and trace preservation;
- exact syndrome-packet completeness and Knill-Laflamme conditions for the three-qubit bit-flip code;
- exact recovery of a nontrivial logical superposition after a mixed single-bit-flip channel;
- periodic-lattice dispersion bounds and second-order convergence;
- finite heat-trace spectral dimensions;
- positivity and semigroup composition of the Euclidean transfer matrix.

Representative numerical values are stored in `results/numerical_results.json` and summarized in `tables/numerical_summary.csv`.

## Representative residuals

- Bell-state residual: `0`.
- Parity off-block norm: `0`.
- Circuit path reconstruction residual: `0`.
- Maximum leakage-bound violation: `0`.
- Feshbach projected-resolvent residual: `3.2291e-17`.
- Bare-truncation residual: `1.3091e-2`.
- Moving-frame residual with connection: `1.0645e-10`.
- Moving-frame residual without connection: `7.0000e-1`.
- Canonical packet-connection residual: `0`.
- Bloch-curvature residual: `2.0803e-11`.
- Knill-Laflamme residual: `0`.
- Bit-flip recovery residual: `1.0385e-16`.
- Tensor parity-refinement residual: `0`.
- Euclidean-transfer semigroup residual: `0`.

## Document audit

- The LaTeX source compiled successfully with `latexmk`.
- No unresolved references were reported.
- No overfull or underfull boxes were reported in the final log.
- The PDF was rendered page by page at 150 dpi.
- All 25 rendered pages were included in `Verification_Render.png`.
- The title page, dense theorem pages, error-correction figure, numerical table, software map, and final page were inspected at full size.
- No clipping, overlapping text, missing figures, or blank pages were found.
- The source contains no `\\cite`, `\\bibitem`, or `thebibliography` commands.
- Classical sources remain in the separate series reference ledger.

## Package audit

- The wheel was built without network dependency resolution by using the installed build toolchain.
- The wheel was installed into a clean target directory with `--no-deps`.
- A clean import of `projector_quantum_calculus` succeeded.
- Both the complete and source-focused archives are intended to be extracted and retested before final delivery.

## Claim boundary

The finite-dimensional theorems and certificates do not establish the continuum quantum-spacetime conjectures. The paper separates theorem, classical input, numerical certificate, and conjecture environments throughout.
## Independent package checks

- A clean copy of the complete release passed all 22 tests, regenerated all 19 figure pairs, passed all 22 tests again, and recompiled to a 25-page PDF.
- A clean copy of the source-focused package passed all 22 tests and recompiled to a 25-page PDF.
- The complete wheel installed into an isolated target and imported successfully.
- The final archives are additionally extracted and checked after their checksum ledgers are generated.

