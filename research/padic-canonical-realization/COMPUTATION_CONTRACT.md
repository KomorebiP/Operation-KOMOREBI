# Block34 finite computation contract

Claim: the new residual-module interpretation and cross-realization simulations
agree with independent exact finite constructions. Universal validity is provided
by Lean, not by a bounded experiment.

Arithmetic: arbitrary-precision Python integers, modular residues, SymPy exact
integer Smith normal form. No floating-point decision, heuristic tolerance, OCR,
or unrecorded external data.

Generic grid: (p,r)=(2,0),(2,1),(2,2),(3,1),(3,2); source dimensions 0,1,2;
alphabet sizes 0,1,2; two seeded trials each, for 90 pairs. A competitor adds a
driven unobservable coordinate and is conjugated by an integral unimodular change.
Both reachable spans are independently enumerated from full digit orbits and
scalar/additive spans. Joint observation partitions use a finite length bound.
The largest possible competitor ambient set has 9^3 elements. Every retained
behavior-class representative is checked for output and digit transport. Four
additional additive/scalar pairs are sampled in each case. Seed=34092126,
Python random.Random (Mersenne Twister). Matrix orientation is destination row,
source column. Prefixes are consumed before suffixes.

Actual masks: p in {2,3}, r in {1,2}, each with (A,B)=(1,1-z),(1+z,1),(1+z,1+z),
plus (2,4,1,1+4z),(2,8,1,1-z),(2,8,1,1+16z),(3,6,1,1+81z): 16 cases total.
The predecessor reachable and observable lattice implementations determine their
stabilization horizons. For each case all prefixes shorter than max(1,reach rounds)
and all suffixes shorter than max(1,observation rounds) are enumerated. The Hankel
entry is computed by the independent direct Mahler recurrence at
value(prefix)+p^length(prefix)*value(suffix). The matrix Smith image signature is
compared with the predecessor observable-module signature. Individual coefficient
outputs are also compared at n=0,...,31. Exact ranges and all Hankel matrices are
retained in results/audit_residual.json. Maximum actual recurrence index is reported
per case; no undeclared truncation is allowed.

Additional controls: noncommuting word orientation; empty word; binary words ending
in 1 versus [0]; zero precision and empty alphabets/coordinate sets. One assertion
is one tested equality/inequality of a scalar, vector, set or signature, not one
assertion per unseen matrix entry. All enumerator counts are recorded by tag.

Pass: every stated assertion is true, a result JSON is written, and code exits 0.
Failure: an exact mismatch aborts and preserves its diagnostic. Timeout or external
termination is inconclusive, not a pass. Final runs use a 600-second subprocess
limit and before/after hashes. No claim of a hard memory or whole-service limit.

Non-claims: minimum DFA, optimized executable refinement, infinite-precision
compatibility, general field-rank reasoning over residue rings, new runtime saving,
or a universal theorem inferred solely from finite checks.
