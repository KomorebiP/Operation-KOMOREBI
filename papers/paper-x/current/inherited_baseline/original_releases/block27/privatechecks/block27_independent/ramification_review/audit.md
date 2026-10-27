# Block 27 ramification and witness independence audit

Verdict: PASS at the exact stated conditional scope. No mathematical gap found in the two primary modules. This reviewer read the raw Lean files and the exact pinned Mathlib sources listed and hashed in `source_paths.json`; compiler and transitive axiom checks are the parent audit's separate responsibility.

## Arithmetic hypotheses

`UnramifiedFrobeniusUniqueness` uses an actual number field L normal over Q, a natural prime p, and an actual maximal ideal P of its ring of integers lying over (p). Characteristic zero supplies separability, so normality yields the finite Galois extension needed by the actual Galois action. The local `IsGaloisGroup` instance is constructed from fraction-ring actions. It is a faithful action/fixed-ring property, not an assumption of etaleness or inertia triviality.

The exact Mathlib inertia-cardinality theorem requires domains, a finite flat integral extension, a finite acting group, and perfect base residue field. The actual integer/ring-of-integers setup supplies these: finite free Z-module structure, finite Galois group, and perfect residue field of Z. The conversion from `ramificationIdxIn` to the local `ramificationIdx` uses transitivity for the actual finite Galois group. Cardinality one implies the actual inertia subgroup is bottom. There is no Nat.card infinite-group loophole.

The residue homomorphism is the actual decomposition-group action on O_L/P over Z/(p). Its kernel equals the inertia subgroup inside the decomposition group. The proof explicitly converts subgroup inertia to ambient inertia before concluding injectivity. Equality of residues is checked on all ring-of-integers elements; quotient surjectivity extends it to every residue. Consequently p-power Frobenius is unique at the fixed unramified P, as claimed.

The discriminant argument uses the actual integral-basis discriminant. Nonzero discriminant is proved in Mathlib. Prime-factor membership therefore gives the required finite exceptional set without a zero-discriminant exception. The exact discriminant theorem provides `Algebra.IsUnramifiedAt Z P`; actual local ramification length is then one. The finite-ramified-primes theorem only asserts inclusion in a finite set and does not need normality, matching its omission of that hypothesis.

## Restriction and witness comparison

`NumberFieldWitnessIndependence` uses the same contracted actual prime and same chosen integral embedding as the restriction modules. Absolute inertia restricts into that finite prime's inertia by equivariance and the ideal definition. Outside the discriminant, this proves the restricted element is identity. It does not assert that inertia in the full algebraic closure is trivial.

For two witnesses u,v, the earlier actual-prime conjugation theorem gives v^{-1}(a u a^{-1}) in inertia at v's prime. Applying the restriction homomorphism and multiplying by the image of v yields precisely conjugacy of the finite restrictions, with the correct order and inverse placement. The representation application kills this actual inertia and obtains trace independence. The equality is valid for the stated module generality; in finite dimension it is the usual representation character statement.

## Scope boundaries

No existence of a prime realizing an arbitrarily prescribed finite conjugacy class is proved here. No density or cofinite prescribed-conjugacy coverage follows merely from finiteness of ramified primes. Frobenius uniqueness and witness independence establish that finite Frobenius classes and traces are well-defined outside a concrete finite exceptional set. General Claim 9.1 remains partial pending its actual coverage input.

No production files were edited by this reviewer. No broad build was run. One initial search used the project directory instead of the Mathlib directory and returned file-not-found errors; it was corrected before source inspection and has no effect on the mathematical conclusions.

## Compiler repair and final-source re-review

The first semantically reviewed version of `NumberFieldWitnessIndependence.lean` had SHA256 `00a7c1383488ab93fa35e1b1a963a0babcf1f8a41462ed8a41ff0ecc39f99a08`. The parent subsequently reported an isolated compilation failure in `restricted_witnesses_conjugate` caused by homomorphism-domain alias elaboration. The final proof explicitly binds `r : GQ →* Gal(L/ℚ)` and changes the equation and goal to that homomorphism before the same multiplication calculation. This reviewer read the repaired proof and confirms that the mathematical argument and hypotheses are unchanged. The source manifest now records the repaired file hash `1b7e8dabe652f0dcf2b982e793723941dab90b108d0dae6bb3118a6280a8332b`. The parent retains the failed source and compiler log and handles recompilation; this reviewer does not claim an independent compile.

The failed-source hash was verified against the retained `NumberFieldWitnessIndependence_attempt1.lean` and its compiler JSON record. The initially supplied historical hash was actually the repaired source hash; that bookkeeping mismatch was corrected before this audit was returned.
