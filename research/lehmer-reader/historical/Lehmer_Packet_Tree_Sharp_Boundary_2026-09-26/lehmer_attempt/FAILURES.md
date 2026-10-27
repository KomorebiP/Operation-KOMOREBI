# Failures and their meaning

## Mathematical routes

1. **Sector-preserving one-sign completion fails.** At prime 7 the three
   depth-1 sectors have masses -1848, -17248 and 2352. Preserving those three
   masses is incompatible with making every corrected packet weakly positive
   or every packet weakly negative. This is a proof of impossibility for the
   stated correction class, not a refutation of Lehmer.
2. **Global nullity does not localize automatically.** Q8 has weighted sums
   -67060224000000, 65383718400000 and 1676505600000 in those sectors. They add
   to zero but are individually nonzero. Multiplying this correction by a
   sector indicator does not preserve its null identity.
3. **A unique least-valued terminal packet is not guaranteed.** Every terminal
   orbit mass is a 5-adic unit. At index primes p>20 it is also a p-adic unit.
   At p=31 multiple lowest 2-adic masses persist after complete resolution.
4. **Abstract completeness is not nonvanishing.** Even the entire hyperplane of
   weighted-zero corrections admits a nontrivial one-sign corrected sum exactly
   when the original total is nonzero. A uniform construction still needs an
   independent arithmetic reason for a nonzero margin.

## Execution failures

- The first execution of `checks/explore_bound.py` with system Python failed
  at `import sympy` with `ModuleNotFoundError: No module named 'sympy'`.
- Trying the provided primary runtime's Python produced the same import error.
- The dependency was removed. A rational determinant/inverse implementation
  for 3 by 3 matrices replaced the SymPy operations. The revised exploratory
  script completed and produced exact witnesses.
- The final verifier is standard-library-only and completed successfully.

No timed-out or incomplete computation is reported as evidence. These failures
are distinct from the successfully proved sharp geometric threshold.
