# Beal visual companion computation report

The generator reconstructs exact finite-field data for twenty-four figures. It verifies all 49 Frobenius conjugations in F49, derives the fifteen q=11 trace roots from the stored source polynomials, and checks the rational parametrization at three exact rational inputs. It recomputes ranks over F7 for all four L, J, A, N, and homogeneous-kernel matrices. Matrix multiplication checks EJ=A, LJ=0, NA=0, and all kernel relations. It also checks every support/inertia normalization against the pinned table, the Pattern C minor, and a synthetic translated-target control.

The matrix checks independently validate the finite linear assertion. Their interpretation as actual Galois localization uses the written theorem and its stated hypotheses. No computation constructs a global bare primitive p0 or evaluates its actual affine target. The q=11 root reconstruction uses archived trace polynomials and does not perform new curve point counts. Diagram coordinates and color palettes are approximate drawing devices. Every represented field coefficient, rank, count, matrix, and example equality is exact.

Run `python3 visual/figures.py` from the package root. The bounded provenance run additionally uses the packaged mathbox runner with `visual/COMPUTATION_CONTRACT.json`, declares every input, and records input/output SHA256 hashes, resource limits, logs, actual software versions, and execution status. The manifest under `visual/computations/atlas-final-v1.0b/` is the accepted scientific run.

All twenty-four native figures must pass text/canvas and per-card containment before acceptance. The exported guide PDF receives separate full-page rendering inspection. See `FIGURE_LAYOUT_CHECK.json`, `COMPUTATION_REPORT.json`, `PROOFREADING.md`, and `DEVELOPMENT_FAILURES.md` for exact outcomes, input pins, and corrected preflight failures.

This is not a Beal proof, an arithmetic realization certificate, or an authentication of a supplied synthetic target. It does not extend a bounded support contract to arbitrary conductors, depths, or signatures.
