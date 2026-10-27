# Execution record: centered continuum block

The selected goal was to close the centered free-Dirac approximation block on
the fixed flat torus: bounded centered operators, maximal-domain convergence,
all-nonreal strong resolvents, and third-order-moment error estimates. It was
not a request to certify the entire physics corpus or solve cosmology.

The accepted fresh gate is `formal/continuum/verification/block51/current/receipt.json`.
It records 26 local compilation targets, five root-module kernel replays,
209 recursively audited environment declarations (162 in the four new modules),
and 21 controls with their intended outcomes. The four new source modules contain
74 theorems, 15 definitions and 11 abbreviations. Generated helpers account for
the difference between source and environment counts. There are no custom
axioms or admitted production proofs in the audited roots. Standard Lean axioms
`propext`, `Classical.choice` and `Quot.sound` remain allowed.

## Unsuccessful attempts retained

The runtime required its supplied host-path compatibility adapter. A strict
full-runtime file audit found nine changed dependency Git index files after
Lake/Git metadata activity. This strict audit remains a failure in the record.
The accepted gate explicitly excludes those mutable index files from the
source/compiler/cache identity comparison; all relevant runtime inputs match
the authenticated manifest and remained unchanged through verification.

An early baseline command used an unsupported `lake build -j2` option and
stopped before compilation. A later baseline attempt exhausted disk space;
its incomplete receipt and empty log are not counted as success. Reproducible
download intermediates were removed, and the corrected baseline build passed.
An initial declaration-auditor probe failed on numeric type inference; the
corrected auditor compiled and passed before the final audit was used.

Development compiles and control probes encountered elaboration, coercion,
normalization, namespace, syntax and warning diagnostics. Their source and
logs are retained under `formal/continuum/verification/block51/development/`.
These were implementation failures, not evidence that the claimed mathematical
statements were false. The first resolvent-control cycle also contained
ambiguous aliases. That cycle is explicitly invalidated; the corrected controls
passed their intended checks in the final gate.

Fresh acceptance run 01 stopped before proof compilation because the verifier
incorrectly required a compiled cache directory for the unused `Cli` dependency.
The corrected verifier authenticates actual imported objects, records the
absent directory, and keeps all dependency pin and runtime checks. The failed
run is preserved under `formal/continuum/verification/block51/failed_run01/`.
Fresh run 02 passed without changing any frozen mathematical source.

Independent source review required the manuscript's compact-time statements
to state `T >= 0` explicitly. Those two clarifications were made. The underlying
proof bodies and numerical figure inputs were preserved; the verification-scope
diagram and status prose were updated to reflect the accepted results.

## Trust and mathematical limits

The full local import closure was rebuilt into an empty object directory using
the pinned portable Lean runtime. External compiled dependencies were reused
and authenticated. Kernel replay uses the same Lean kernel and imported
environment; it is not an independent kernel implementation or a rebuild of
Lean and Mathlib. The separate semantic review did inspect the exact source
statements and proof dependencies. The broad historical corpus was preserved,
not freshly certified as a whole.

The result concerns the same infinite Fourier Hilbert space throughout. The
generator uses the full maximal first-order domain. The spacing limit is
two-sided and punctured, the resolvent parameter has nonzero imaginary part,
and rate bounds require actual summability of the third-order Fourier moment.
The propagator estimate retains absolute time, and the compact-time estimate
requires nonnegative horizon. No cross-Hamiltonian commutation is assumed.
The constant 1/6 is retained; a separate optimality theorem is not claimed.
Centered generator and inverse identities require nonzero spacing. At zero,
the bounded centered operator is auxiliary zero, whereas the modal propagator
and resolvent use their continuum fills; these different conventions are not
identified as one operator and its evolution or inverse.

Remaining work includes the abstract unbounded spectral-functional-calculus
API link, comparison with changing finite sampled grids, interacting dynamics,
the wider historical evidence audit, and cosmological cutoff/energy/vacuum
obligations. The earlier cosmological failures remain open. No GitHub push,
release publication, or external submission was performed.
