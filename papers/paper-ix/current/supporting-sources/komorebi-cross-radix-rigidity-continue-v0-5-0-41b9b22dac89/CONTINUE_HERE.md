# CONTINUE HERE — Certified v0.5.0 State

## 1. Authoritative checkpoint

The authoritative persisted checkpoint is now **v0.5.0**, extending v0.4.0 without modifying any v0.4.0 source bytes.

- Lean: `4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict gate: `-DwarningAsError=true`
- source modules: **27**
- theorem/lemma declarations: **196**
- definitions/abbreviations/structures: **100**
- new v0.5 theorem/lemma declarations: **58**
- placeholder scan: **0** `sorry`, **0** `admit`, **0** custom `axiom`
- load-bearing `#print axioms`: only `propext`, `Classical.choice`, `Quot.sound`

Treat `AUDIT.json`, strict logs, and the source files as authoritative if prose conflicts.

## 2. New durable Reynolds/DFT layer

For `T>0` and a divisor width `g|T`, `CrossRadixReynoldsDFT.lean` defines the exact Fourier mask

`M_g(k) = 1` iff `g | k.val`, otherwise `0`,

and defines `reynoldsProjector g` by conjugating this mask through Mathlib's actual `ZMod.dft`. Lean proves idempotence, commutation, lcm composition, and exact range intersection.

`CrossRadixReynoldsAverage.lean` then constructs the literal cyclic subgroup map `Z/gZ -> Z/TZ`, proves it injective, proves the character-annihilator criterion, computes the finite character sum exactly, and proves the uniform subgroup average is equal to the DFT-conjugated projector. Thus “Reynolds projector” is no longer just terminology: it is an actual finite-group averaging operator.

## 3. Raw-radix lcm/intersection layer

`CrossRadixSectionReynolds.lean` defines the projector for a positive radix `m` by the canonical reduction `g_m = gcd(T,m)`. In the positive-radix regime Lean proves

`lcm(gcd(T,m), gcd(T,n)) = gcd(T, lcm(m,n))`,

then derives

`P_m P_n = P_lcm(m,n)`

and

`Range(P_m) ∩ Range(P_n) = Range(P_lcm(m,n))`.

The finite-list versions are also proved. `CrossRadixFiniteLCMIntersection.lean` supplies the corresponding finite divisor-indexed form.

## 4. Affine decoder / generalized inverse

`CrossRadixAffineDecoder.lean` proves that `X -> mX+r` is a complex-linear polynomial equivalence for `m>0`, and identifies its forward map exactly with the retained baseline `affineSubst`.

For the explicitly defined projector-factorized affine section normal form, the saved decoder satisfies

`A B = P_gcd(T,m)`, `A B A = A`, and `B A B = B`.

**Boundary:** this is a theorem about that explicit normal form. v0.5.0 does not identify it with any stronger unsaved root-aggregation operator discussed in exploratory work.

## 5. DFT shells agree with certified Möbius shells

`CrossRadixDFTShellAgreement.lean` labels a frequency by `gcd(T,k.val)`, proves the Fourier width mask is the certified width coordinate at that label, decomposes it into point shells, transports the saved Möbius inversion formula, and proves the resulting DFT shell projectors are idempotent and pairwise orthogonal.

Thus the spectral description and the persisted divisor/Möbius description are now linked by saved Lean theorems rather than narrative analogy.

## 6. Hard boundaries retained verbatim from v0.4.0

1. Bell generalized Cobham theorem remains an external input to the earlier two-radix collapse-to-cyclotomic step and is not formalized here.
2. The integral base-independent normal form remains false in the naive form; the square-sequence radix-prime obstruction is retained.
3. The package proves a product-coordinate algebra equivalence, not a separately constructed categorical tensor-product equivalence of local algebras.

Additional v0.5.0 nonclaims are recorded in `AUDIT.json` and `PROOF_BOUNDARIES.md`.

## 7. Strongest next theorem

The missing Priority-2 block is now the cleanest next target:

For characteristic zero, degree `d`, and positive radix `m`, formalize the exact section-map rank/nullity law

`rank A_(m,s) = (T / gcd(T,m)) * (d+1)`

and

`nullity A_(m,s) = (T - T/gcd(T,m)) * (d+1)`.

The proof should factor the section map into reversible affine polynomial bookkeeping and residue aliasing, using the newly certified projector/decoder layer. The characteristic-positive failure mode when `char` divides `m` must be isolated explicitly rather than hidden in assumptions.

After rank/nullity, add a precise Bell-conclusion **interface** (not a proof of Bell) and prove the downstream uniform all-radix hull bound.
