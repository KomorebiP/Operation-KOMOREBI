# Symmetry Collapse in Quantum Computation

This release contains the extended publication-style monograph

**Symmetry Collapse in Quantum Computation: Exact Packet Simulation, Polynomial-Time Classical Regimes, and the Boundary of Global Interference**

by **Komorebi P.**

## Release contents

- 104-page compiled PDF
- standalone master LaTeX source and modular chapter sources
- 19 vector figures generated entirely in Python
- packet-state and moving-frame numerical utilities, with exact integer parameter counts
- validation tests and archival benchmark tables
- two materialized project records used as the principal source basis
- theorem and evidence-status ledger, extension notes, and build audit

## New extension in this release

The additional theorem layer moves beyond one fixed invariant projector.

1. **Dynamic packet simulation.** A circuit may follow a computable sequence of polynomial-dimensional subspaces rather than one conserved sector.
2. **Moving-frame collapse.** A time-dependent change of coordinates can reveal one fixed small packet, provided the frame schedule is independently discoverable and efficiently usable.
3. **Sparse packet-transfer graphs.** Exact sector-changing gates remain classically polynomial when the total reachable packet dimension stays polynomial.
4. **Bounded-excitation collapse.** Exact particle-number conservation is stronger than necessary. A fixed union of low-excitation sectors remains polynomial.
5. **Schur-commutant compression.** For fixed local dimension, permutation-invariant mixed-state dynamics admit a polynomial operator record even when symmetric-group multiplicity spaces are exponential. The qubit record uses `O(n^3)` parameters.
6. **Scaling phase diagrams.** Fixed particle number is polynomial, logarithmic particle number is quasipolynomial, sublinear power-law particle number is subexponential, and finite-density sectors remain exponential in the explicit occupation basis.

## Reproduction

From the source directory, run:

```bash
./run_all.sh
```

The script:

1. runs exact rational tests, numerical packet/full-state and moving-frame validations, and input-boundary controls;
2. regenerates every figure with Python;
3. compiles the LaTeX monograph with `latexmk`;
4. updates the checksum manifest.

## Logical status

The monograph visibly separates:

- proved packet and simulation theorems;
- derived symmetry-collapse corollaries;
- recorded computational benchmarks;
- contextual external results;
- formal research programs and open problems.

The benchmark values are implementation records, not universal speedup constants. Polynomial-time conclusions require explicit hypotheses on discoverability, active representation size, gate application, measurement access, and leakage.

## Principal conclusion

An apparently exponential quantum state-space computation collapses to deterministic classical polynomial time when its reachable dynamics admit an efficiently discoverable, polynomial-size classical representation preserved by the evolution and sufficient for the final measurement. The representation may be a fixed packet, a moving packet, a sparse union of packets, or a symmetry commutant record. None of these results implies that arbitrary BQP computation collapses to P.

## Completion review

The current source corrects the entropy estimate for a varying particle density, states the normalization convention for zero-weight Schur blocks, and makes initialization and enumeration costs explicit. It adds a proved adaptive discarded-state error certificate and an exact rational worked example. The numerical packet compiler now rejects every represented nonzero off-packet coefficient rather than silently dropping small leakage.

Run `PYTHONPATH=code python3 code/validate_exact.py` for 308 exact rational/integer assertions and `PYTHONPATH=code python3 code/validate_boundaries.py` for 21 API controls. The original `validate.py` remains the numerical reconstruction path with tolerance 2e-12. These finite checks do not prove the general theorems.

The original standalone PDF and original checksum manifest are retained as historical inputs. They do not contain these source revisions. The rebuilt combined Quantum and Circuits volume is the current reader edition.
