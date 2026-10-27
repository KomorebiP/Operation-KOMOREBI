# Computation audit for Conjecture Series 06

Edition: 9 October 2026. Author: Komorebi P., Operation Komorebi.

The latest three Fermat certificate suites reproduce their 24, 46 and 137
grouped checks. The Weil audit also reproduces its exact exterior-algebra and
tangent assertions. Fifteen bounded scientific runs completed and all fifteen
schema-version 2 manifests validated with unchanged input hashes and matching
result hashes. These executions certify the stated finite assertions. They do
not execute mixed Hodge theory, construct an unspecified algebraic cycle, or
prove the general Hodge conjecture.

## Contract and arithmetic

The mathematical target is rational algebraicity, with signed rational cycle
combinations allowed. The executable surrogate consists of exact character
ages, integer residue graphs, matrix identities, polynomial identities,
Groebner reductions, Smith forms and finite-dimensional exterior algebra.
The original 18 projector examples form a separate numerical toy suite with
float64 residual tolerances. No geometric interpretation is inferred from
passing a numerical matrix illustration.

The latest code uses Python integers, Fraction and exact SymPy arithmetic over
Q or Q(i). Randomness is absent except in the old numerical examples and in
the deterministic hash screen for dyadic enumeration. The dyadic screen
cannot discard a truly balanced packet: its exact equality necessarily has
equal additive hashes. Hash collisions only admit extra candidates, which are
fully rechecked for exact balance. The seed formula is 12345 + modulus + length.

The runner records actual argv, UTC start, elapsed time, Python and library
versions, supplied input hashes before and after execution, output hashes,
exit status and resource limits. The environment used Python 3.12.14 and
SymPy 1.14.0. The individual toy contract records NumPy and Matplotlib versions.
The repository commit was unavailable and the runner marked the working state
dirty. File hashes, rather than a fabricated commit identity, pin these runs.

## Results and exact ranges

| Run | Implemented finite assertion | Result |
| --- | --- | --- |
| Carrier70 | One degree70 character, its degree210 lift, 6x6 exponent matrices, toric strata and five radical membership certificates | 24 grouped checks pass |
| Transfer210 | Fourteen signed generator packets, exact incidence, all compositions of lengths1 through13, a 210-state shortest return certificate and q6 through80 K5 benchmarks | 46 grouped checks pass |
| Dual and Cycles | Seven capacity inputs, Newton and Vandermonde identities, intermediate determinants at q2,3,4,5,7,11,17, family support at q2 through64 and specified socle tests | 137 grouped checks pass |
| Weil candidate | All 924 exterior basis forms and all 18 real tangent directions in the stated model | Exact assertions pass |
| Dyadic symbolic evaluation | Moduli2^3 through 2^9, tree structure, triangle identities and star formulas | 56 grouped checks pass |
| Dyadic exhaustive | Moduli8,16,32,64,128, balanced four- and six-multisets, full-conductor orbits, exact SAT2 and tree predictions | All five complete implemented finite censuses pass |
| Weighted dyadic | Every odd lift and unit at 2^3 through 2^9, on the two coefficient basis vectors | 87,376 coefficient equalities pass |
| K23 regeneration | Seven recorded representatives at degrees50,70,90, every unit conjugate and admissible phase-pair partition | 364 certificates and 8,336 exact age rows pass |
| Independent checks | Bellman-Ford duals, sparse incidence, integer Bareiss determinant evaluations, restriction determinants and direct small censuses | 226 grouped checks pass |
| August Fermat33 | Exact exponent, lattice, character and Jacobian checks | 14 grouped checks pass |
| August Klein tower | k1 through12 and stated composition/Tate samples | Four grouped checks pass |
| August conductor | Moduli33,66,99,132,165,231,330, promotion k1 through12 and stated joins | Four grouped checks pass |
| August odd-prime | Complete implemented censuses at9,27,25 and stated prime-power samples | 13 grouped checks pass |
| Numerical toys | Original deterministic finite matrix illustrations with source tolerances | 18 numerical checks pass |

There are two dyadic exhaustive runs, one through 32 and the subsequent complete
implemented replay through 128. They are both preserved. Grouped checks have
different granularities across scripts and must not be added into a theorem
count or interpreted as independent mathematical results.

The exact dyadic census is:

| Modulus | Balanced4 | Balanced6 | Full-conductor orbits | Pair | SAT2 | Star |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 8 | 12 | 30 | 13 | 9 | 4 | 0 |
| 16 | 46 | 216 | 45 | 27 | 18 | 0 |
| 32 | 162 | 1,344 | 134 | 91 | 42 | 1 |
| 64 | 586 | 8,352 | 419 | 331 | 87 | 1 |
| 128 | 2,202 | 55,648 | 1,435 | 1,259 | 175 | 1 |

The original code's MITM census was independently benchmarked by direct
combinations-with-replacement enumeration at moduli 8 and 16, for both lengths 4
and 6. No randomized hash was used in that independent census.

## Load-bearing independent checks

For the degree210 target, the original verifier enumerates 27,131 nonzero
composition vectors of lengths at most13. Exactly143 are invariant, and their
minimum dual numerator is420. All longer vectors cost at least 14*31 > 420.
The shortest positive return on the 210 residue states also has cost 420.
The new implementation uses repeated Bellman-Ford relaxation in place of the
original Dijkstra routine and verifies every Bellman inequality. The direct
dual optimum is 1, with the invariant all-ones column giving the matching primal
value. This finite potential certificate supports the stated all-invariant-
column inequality through a separate elementary last-edge argument. It does
not assert the existence or normality of a geometric carrier.

The seven finite capacity values are25:6/5, 33:2, 35:1, 39:2, 40:1, 55:1 and
70:11/10. Each has an exact primal equality and an independently checked
residue-graph dual lower bound. Positive primitive full support is explicitly
required. The criterion is a necessary combinatorial capacity test and is not
silently upgraded to a sufficient geometric construction.

The five-phase replay tests 241,920 distinct support monomials and 218,836
balance/conjugacy instances across q2 through64. Exact symbolic determinant
identities were replayed at the seven stated q values. Twenty-one independent
integer substitutions were checked with Bareiss elimination. These bounded
substitutions corroborate the implementation. The uniform determinant and
period formula still require their manuscript arguments and external geometric
normalization.

For K23, the archived fifteen-line verifier only checks JSON flags and the
reported count364. It does not regenerate certificates. The new implementation
reconstructs every admissible pair/triple partition at every unit conjugate of
the seven recorded packet representatives. Counts by representative are
40,60,48,48,48,48,72. Every regenerated packet identity and age row is checked,
as are opposite CM signs, the minimal conductor of the sign function and a
half-plane translate. The selector is checked to be nonzero and to satisfy
conjugate(Delta) = -Delta in Q[x]/Phi_q(x). The conductor distribution is
(degree50, conductor5):100, (degree70, conductor7):96,
(degree90, conductor3):48 and (degree90, conductor9):120.
Matching these character data supplies no rank-one Chow correspondence.

## Weil candidate and negative results

The convention is integral(x1 y1 ... x6 y6) = -1, with polarization weights
(1,1,1,-1,-1,-3). The exact intersection Gram matrix on(theta^3,u,v) is
diag(2160,-32,-32). The correspondence polynomial projects all 924 basis
forms onto the two-dimensional span of u and v. The seed graph periods are
(96,0,-8), and its projected class is v/4. These periods were independently
checked by determinants of the graph restriction matrix.

The chosen graph has a three-complex-dimensional preserving tangent space
at the nonsplit seed, compared with six at the split control. This is a
statement about that graph. It does not bound all components of a cycle space
or show that another algebraic representative cannot exist. The tested mixed
direction loses the old product factors, but an alternative three-pair divisor
factorization survives. The tested counterexample path therefore fails to
establish nonalgebraicity. The nilpotent is square-zero and has rational rank 4.
It does not by itself construct an algebraic semistable degeneration.

No scientific run failed or timed out. Two deliberately corrupted controls
were rejected: a transfer sign mutation and an invalid uniform dual. These
expected negative controls are recorded in the independent result. They are
implementation falsification checks, not mathematical counterexamples.

## Historical counts and residual risks

The historical 89,478,480 weighted coefficient checks through 2^14 are retained
as historical evidence. This edition verifies the count formula
sum_{s=3}^{14}2^(2s-2) = 89,478,480 and replays only 87,376 corresponding
coefficient checks through 2^9. The triangle/tree evaluation is a different
implemented assertion and its56 grouped checks must not be substituted for
the historical weighted count. The general balanced-packet census through
degree100 was not independently re-enumerated.

Legacy universal `theorem_summary` strings are historical manuscript claims,
not consequences established by running their finite samples. The general
geometric proof, rational cycle construction and imported theorem hypotheses
remain outside these Python runs. SymPy's exact polynomial algorithms and
the recorded mathematical conventions remain dependencies. Memory limits
were 0.5 to 4 GiB, CPU limits 20 or 90 seconds and wall limits 30 or 120 seconds
depending on the run. Numerical thread caps are cooperative. CPU-time limits
are per process, as the runner records.

The portable driver uses fixed reviewed commands and writes into a new copied
destination. The original recovered sources remain unchanged. Current source
copies, contracts, raw results and the newly reconstructed K23 certificates are
included with this audit. There was no `.mathbox` ledger in the recovered
project, so no mathematical claim state was invented from a pass label.
The driver was tested end to end in a fresh destination. All 15 runs completed
and matched the shipped scientific outputs after excluding timestamps,
elapsed times and displayed commands. The record is `portable_validation.json`.
The K23 half-plane comparison uses half-integer cutoffs at conductors3,5,7,9,
which are exactly representable. No tolerance is used in those comparisons.
