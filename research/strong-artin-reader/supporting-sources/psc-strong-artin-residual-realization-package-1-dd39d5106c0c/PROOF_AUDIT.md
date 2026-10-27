# Proof audit

## Counts

- Theorems: 29
- Propositions: 8
- Lemmas: 4
- Corollaries: 37
- Internally proved theorem type records: 78
- Proved examples: 2
- Complete proof environments: 80
- Definitions: 23
- Examples: 3
- Remarks: 13
- Imported standard facts: 8

Every theorem, proposition, lemma, and corollary has a proof environment. Two examples also contain proof environments, giving 80 proofs for 78 theorem type records.

## Hypothesis audit

- The cyclic torsor statements assume irreducibility and extension existence.
- The finite Satake root theorem assumes a finite Galois base change.
- The finite trace image theorem assumes semisimplicity and residual characteristic greater than the rank.
- The large residual theorem excludes finitely many primes for irreducibility, trace pairing, cross characteristic, and alphabet separation.
- The one prime attachment theorem assumes a good separating prime and absolute irreducibility after restriction.
- The l adic rigidity theorem assumes continuity, semisimplicity, finite ramification, and a density one Frobenius set.
- The recursive theorem remains conditional on a realization gate at every invariant extension step.

## Verification

The residual realization verifier reports 38956 passing checks. The earlier base and maximal suites report 37686 and 32772 passing checks. The suites overlap and are retained as regression tests, not as independent evidence.

## Conclusion

No internal proof obligation is missing. The full Strong Artin conjecture is not claimed. Independent review is especially important for the finite trace image theorem, cross characteristic lifting application, one prime residual attachment, and l adic finite trace rigidity.
