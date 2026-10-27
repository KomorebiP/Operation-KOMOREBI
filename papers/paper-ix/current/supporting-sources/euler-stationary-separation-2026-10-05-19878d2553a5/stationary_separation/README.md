# Euler stationary separation checkpoint

**The Euler simplicity goal remains open.** This phase worked on the missing
arithmetic separation rather than extending the multiplier range.

Checkpoint: `Euler-stationary-separation-20261005`. Immutable base:
`Euler_Bernoulli_Structure_2026-10-05.zip`, SHA256
`b1dd12d9e0904b7d9a0b999e961fd1b12b4e3afde71995da4064d7849cdfacf7`.

The actual function now has a proved degree-two reduction whose reduced discriminant
has exactly the stationary value's valuation. Actual Jacobi approximation
also reaches unbounded precision with every undepletion factor retained.
Finite exponential models now approximate the actual function at every
depth as well, with explicit order and height costs. None of these
theorems supplies a nonzero discriminant.

Start with [SYNTHESIS.md](SYNTHESIS.md) for the mathematical results and
[ROUTE_INDEX.md](ROUTE_INDEX.md) for proof and review links. The exact target
and fixed controls are in [TARGET.md](TARGET.md).

The next decision is whether a new constraint on the actual reduced
discriminant numerator can force a strict precision comparison. The tested
projective height criterion fails at the frozen inputs; the full recurrence
and contact identities balance their nonzero terms without excluding a
double zero. Increasing ranks or multiplier digits would not address those
specific failed implications.

The parent retains terminal129 and higher-address obligations. A proof of
the focused terminal161 family would still need those obligations for
universal Euler simplicity.
