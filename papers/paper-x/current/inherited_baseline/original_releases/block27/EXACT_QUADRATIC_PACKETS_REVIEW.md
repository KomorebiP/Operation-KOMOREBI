# Independent review of the Block 21 exact computation

Verdict: **implementation and finite assertions verified in the stated range**.
The reviewer read the complete standalone source, the contract, the author's
audit and version 2 evidence, then replayed the unchanged computation in a
fresh output directory. No implementation, execution or interpretation defect
was found in that inspected scope. This is an independent code review and
replay of the existing implementation, not a claim that an independently
written second implementation reproduced every assertion.

## Scope and code-level checks

The three prime-power families are exactly `(2,12)`, `(3,7)` and `(5,5)`,
including depth zero. `range(max_depth + 1)` includes each stated terminal
depth. Every residue is tested. Reduction uses ordinary remainder by the
smaller prime power, which is the actual quotient-ring reduction. Every
loop has its declared finite bound and no early success exit. Computation
uses exact Python integers, no randomness, floating point or external package.

`square_roots_of_one` evaluates the equation directly. `character_values`
independently enumerates units using `gcd`, fixes the identity image and tests
all four multiplication pairs in `C2`. It never calls the root predicate.
At modulus one, `gcd(0,1)=1`, so the unique element is correctly retained as
the unit of the zero ring. This checks the finite correspondence without
silently excluding that base case.

The basis order `(1,X)` and relation `X^2=1` give the implemented product
`(a,b)(c,d)=(ac+bd,ad+bc)`. Evaluation is `a+b*x`. The addition and product
checks therefore test the intended coefficient model of the quotient. All
quotient-element pairs are tested when the coefficient modulus is at most
16. For larger moduli, the source really uses only the declared 25 coefficient
probes in `[-2,2]^2`, and the contract and prose correctly retain that limit.
These computations alone do not construct a universal algebra equivalence.

For each consecutive pair of levels, the source enumerates all `p` residue
lifts `x+k*p^m`, independently of the stored root table at depth `m+1`.
That checks the accepted edges against the complete candidate fiber. Direct
projection of terminal roots is compared with backward pruning. The pruning
loop correctly starts at the preceding level and stops at the requested
source level; it does not prune the terminal level itself. A terminal root
determines a unique preceding sequence under quotient reduction, so enumerating
one finite branch per terminal root is complete within the declared horizon.

All high/low pairs, including equal depths and depth zero, are covered by the
naturality loops. The group-action check covers both `C2` elements. Ring-point
naturality covers the same declared 25 coefficient probes at every pair.

For `F2[epsilon]/epsilon^r`, `binary_mul` performs polynomial convolution by
XOR of shifted coefficient vectors, then removes coefficients of degree at
least `r` with a bit mask. Addition is XOR and the constant term is bit zero.
The unit enumeration checks existence of an inverse directly. The root and
character tables are independently obtained before comparison. All quotient
coefficient pairs are tested for `r=2,3,4`. Truncation to every smaller length,
including `r=1`, is checked on every source root and coefficient pair. This
correctly exhibits extra roots in rings with nilpotents, where the two signs
coincide and a domain-based classification would be invalid.

## Orthogonal count and boundary checks

The reported counts agree with direct formulas from the declared loops:

* Residue candidates: `8191 + 3280 + 3906 = 15377` across 27 levels.
* Retained prime-power roots: `44 + 15 + 11 = 70`; four group-law pairs per
  retained character give 280 pairs.
* Every next-level root has exactly one reduction parent. Thus the accepted
  edges total `70 - 3 = 67`, excluding the three depth-zero roots.
* Candidate lifts total `2*(44-4) + 3*(15-2) + 5*(11-2) = 164`.
* High/low/root triples total 461, giving 922 character values and
  `25*461 = 11525` ring-point naturality values.
* Terminal branch counts are `4+2+2=8`. These count finite branches only.
* Nonreduced quotient-evaluation pairs total
  `2*4^4 + 2*8^4 + 4*16^4 = 270848`.

The smallest substantive boundary has both residue lifts of `3 mod 8`,
namely 3 and 11 modulo 16. Their squares are both 9, so neither satisfies the
equation at the next level. The sign values collide modulo 2 but differ
modulo 4. In characteristic two with `epsilon^2=0`, `(1+epsilon)^2=1` gives
the advertised nonreduced boundary. These are controls against stronger
false claims, not failures of the intended root/character correspondence.

## Replay and provenance

The reviewer validated the author's manifest with the project root supplied,
then used the computation-audit bounded runner to execute:

```text
python3 checks/exact_quadratic_packets.py --output checks/quadratic_review/results.json
```

The fresh version 2 manifest is `checks/quadratic_review/manifest.json`.
It records CPython 3.12.13, exit status zero, runtime **1.218686 seconds**, a
120-second wall limit, 110-second CPU limit, 1 GiB address-space limit and
one CPU. Its input hash stayed unchanged. The cooperative thread limit is
reported as such. The replay manifest passed validation with `--root`.

The following files are **byte-identical**, including all forests and counts:

* `exact_quadratic_packets.json`
* `checks/quadratic_run/results.json`
* `checks/quadratic_review/results.json`

Result SHA256:
`8858092f3bb0287317c88642286e702ba6b5de0b35d76fb1ec426fe97afaecbf`.

Reviewed script SHA256:
`8cfabd54a7e723ff9d60591631b29430597db69cd8dbcc234dffc450a6b35b71`.

The extracted project has no available Git revision. Reproducibility here
uses the explicit source hash, interpreter version, commands and result
hashes. No stale scientific output was reused by the fresh replay.

## Limits and mathematical interpretation

Every stable core is relative to its stated terminal depth. The two extra
dyadic roots at depth 12 remain valid terminal points in this run. Their
finite branches are not counted as infinite branches. Finite enumeration,
even with complete edge tables or larger terminal depths, does not establish
the existence or classification of branches at all precisions.

The source does not execute an absolute Galois group, continuity proof,
arithmetic packet attachment, Hodge--Tate comparison or Weil--Deligne
comparison. It does not prove that every finite root lifts, or that all roots
in arbitrary commutative rings are signs. Any universal or arithmetic
conclusion must come from the separate Lean proofs and their stated
hypotheses. The finite run by itself changes none of the full arithmetic
claim statuses.
