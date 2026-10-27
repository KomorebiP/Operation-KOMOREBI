# Exact computation contract and interpretation

The exact surrogate is the explicitly constructed example on each page V-29–V-40. Entries belong to Q or Q(i); conjugation and matrix multiplication are exact. Every successful equality is literal rational equality. All finite bounds are recorded in `EXTENDED_CONTRACT.json` and the result's `facts`.

The final fresh run checks 373 positive assertions and rejects 12 deliberately false assertions. There is no randomness, tolerance threshold, finite-difference derivative, curve fit, coordinate sampling, numerical eigensolver or symbolic package in this suite. Matrix ranks are checked by exact Gaussian elimination; selected norms use exact diagonal spectra or scalar Gram certificates. The S3 packet ranks are also checked independently by traces, and Choi positivity by all principal minors of the worked four-by-four matrix.

The V-33 finite code computes all four diagonal error-overlap minimax values. The written triangle-inequality argument, rather than enumerating candidate scalars, establishes the all-complex-scalar lower bound. Infinite geometric tails, logarithms, general functional calculus, all-grid heat convergence and continuum torus asymptotics likewise use their stated written arguments and hypotheses.

A pass verifies these implemented finite assertions in the declared range. It cannot decide an unspecified continuation, arbitrary representation or channel, uniform convergence from a prefix, or any of the five original physical/continuum targets. The code's successful exit and the manifest validator's success are execution/provenance evidence, not theorem certification.

The bounded run used a 30-second timeout, 1 GiB process address-space cap, 20-second per-process CPU cap, one CPU affinity core and cooperative one-thread numerical-library settings. The program uses no numerical library. Actual runtime, command, input hashes, outputs and effective resource settings are in `computations/final-20261006/manifest.json`.

The original `checks/EXACT_CHECKS.json` records 180 inherited finite/symbolic checks with nine rejected controls; it is not overwritten by the new checks. SymPy is unavailable, so original symbolic derivatives, trigonometric simplification and rational enclosure verification are not freshly replayed. The entire original source and saved result are preserved for a suitable environment. No Lean compiler is invoked.
