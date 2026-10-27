# Block 28 computation contract

The universal claims are proved separately in Lean. The finite surrogate uses
Python arbitrary-precision integers with exact modular reductions. Matrix entries
are obtained by summing every routed branch into the target/source entry before
testing nonzero support. Independently, every such column is compared with the
predecessor polynomial transition on a basis vector. Least support from bounded
iteration is compared with queue/BFS reachability. All closed coordinate subsets
are enumerated when the declared position count is small.

Generic grid: position count 0..5, modulus in {2,4,5,9}, alphabet size 0..2,
three seeded systems per combination, 216 executions. All 2^N candidate supports
are enumerated. Empty alphabets, empty positions, and zero divisors are included.

Mask grid: p in {2,3,5}, r=1..4, eight curated and two deterministic random mask
pairs per combination, plus four illustrated cases. Total 124 executions (not a
claim that all tuples are distinct). The random generator is random.Random,
MT19937, seed 280920. All matrix columns are compared with routed polynomials.
All candidate supports are enumerated for actual systems with at most eight
profile positions. Each case checks 40 coefficients against the direct Mahler
recurrence, Block27, and the original sufficient machine. One arbitrary pair of
supported vectors per case is checked at each legal digit for embedding and
additivity. The four illustrations include unchanged-support examples.

Restrictions are independently exercised by opposite-branch cancellation,
correlated source cancellation over ZMod5, and zero divisors over ZMod4. Assertions
count whole finite mathematical comparisons such as vector equality, not every
scalar arithmetic operation hidden within them. Any failed assertion aborts. A
resource-limited run is inconclusive and is not included as PASS.

No finite test proves the universal theorem, executable Lean/Python equivalence,
minimal invariant-submodule dimension, or a minimal reachable automaton. Source
and test input hashes are recorded before and after each command. Current evidence
is distinct from preserved predecessor receipts; the large historical audits are
not described as freshly rerun.
