# Continue after Block 47

Canonical result: `notes/mod7_good_reduction_irreducibility.md` proves the
attached RM representation absolutely irreducible for 14 not dividing C,
using source-checked written arithmetic inputs. Read its independent review
before extending it. No primitive (3,5,7) solution or indexed modular form
was excluded by a completed elimination.

## Exact open obligations

1. **Remaining irreducibility case:** 14 divides C. At seven the curve is
   semistable rather than good. The finite-flat comparison used in the
   good-reduction proof is not available unchanged. Do not substitute
   a singular fiber into the Cartier good-reduction theorem.
2. **Level lowering:** close every source hypothesis specifically at seven.
   The statement of PV Theorem 7.8 has no explicit seven exclusion, but that
   does not replace checking its cited dependencies. PV main theorems that
   exclude seven cannot finish this signature.
3. **Actual candidate data:** acquire or recompute exact coefficient-field
   definitions, integral Hecke values and prime/embedding data for every
   surviving form. Public aggregate transcripts do not determine those
   missing labels. No Magma runtime or full form-space recomputation was
   available in this block.
4. **A correlated elimination certificate:** retain one form, one prime
   above seven and a consistent embedding across all auxiliary tests.
   Resolve the t-versus-inverse-t dictionary before adding parameter labels.
   The Lean exclusion interface still needs arithmetic coverage, attachment,
   sound local tests and genuinely empty survivor sets.
5. **Full Beal:** even solving (3,5,7) would not solve all exponent signatures.

## Do not reopen disproved shortcuts

- Coefficient-only local refinement is saturated: (3,5,2) and (2,3,11)
  have primitive points over every Z_p. Arbitrary prime-power precision
  does not remove these families.
- Every regular motive parameter is locally populated by the polynomial
  universal identity. A fixed global candidate may still be excluded.
- The actual hypergeometric period is not 7-integral as written; the old
  factorial unit-tail theorem cannot be imported without normalization.
- Scalar support is already all F49 at21 of 36 audited auxiliary primes.
  More tests of that same type at those primes do not constrain F49 traces.
- The dyadic joint coefficient relation and coefficient-conjugate trace
  relation carry information that their individual marginals discard.
- The generic Lean certificate does not itself prove the arithmetic inputs.
- The unpublished/working septic classification mentioned in the prior
  addendum is not promoted to a fully audited theorem here.

## Ready-to-use conditional restrictions

Under the explicitly stated modular and multiplicative-prime comparisons,
rank-two trace zero at 11 forces 11|A, and trace zero at 19 forces 19|B.
The full good-reduction point tables are independently checked on all 452
residue pairs. CM by K(sqrt(-3)) gives the first condition; do not infer
the second for an indexed CM form without its actual CM/Hecke data.

## Reproduction

All finite arithmetic uses Python 3.12 standard library. The scripts in
`computations/` have their own CLI and bounded contracts. To avoid changing
the retained output snapshots, direct replay output to a new path.

For example, from this directory:

```sh
python3 computations/primitive_scaling.py --output /tmp/block47_scaling_replay.json
python3 computations/hypergeometric_audit.py --output /tmp/block47_hypergeometric_replay.json
python3 computations/modular_correlations.py --output /tmp/block47_modular_replay.json
```

For Lean use the existing pinned runtime or equivalent Lean 4.34.0-rc2 with
Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06:

```sh
python3 verification/formal/verify_block47.py --runtime /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The runtime and generated oleans are not included in this source archive.
Formal verification records retain the original absolute execution paths;
the driver resolves source paths from its own location for replay.

`predecessor/` contains unchanged copies of the load-bearing Block46 notes,
their audits and the partial-results addendum. The earlier full archive is
not overwritten. `PACKAGE_SHA256SUMS.txt` authenticates packaged file bytes;
it does not certify their mathematics.
