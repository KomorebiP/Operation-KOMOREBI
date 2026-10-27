# Strong Artin Lean v0.26 — Representation H² Obstruction

**Author label:** Komorebi P.  
**Release date:** 11 September 2026, America/Chicago.  
**Outcome:** checked algebraic obstruction construction and exact lifting criteria, including a fixed-subgroup condition. **Not a Strong Artin theorem.**

## Starting point and ancestry

This is a new, uniquely named branch above the audited checkpoint:

```text
Strong_Artin_Lean_v0.25.0_Graded_Compatibility_Lifting_Checked.zip
cf9669502a2cfa332e4c6d9da5b40d51f98b226e2099a5593017287cfdbb492c
```

Only `SquareZeroRepresentationDefect.lean` is imported from that archive, byte for byte. Its full archive is preserved in `base/`. The preceding audit is preserved in `audit/PRIOR_AUDIT_2026-09-11.md`. Sibling branches are not silently merged and historical declaration totals are not updated by addition.

The audit's central missing arrow was:

```text
actual multiplication defect -> compatible two-cochain
                           ?-> correctable defect
                           -> original representation lift
```

This release constructs the missing obstruction quotient in the proper degree and proves an exact criterion. It does not assume every compatible defect is correctable.

## Absolute lifting theorem

Let `q : A -> B` be a surjective unital homomorphism of rings, possibly noncommutative. Assume its kernel `K` is square-zero: `K*K=0`. Let `rho : G -> B^×` be a representation of an arbitrary abstract group.

Unit lifting supplies a normalized set-theoretic map `r : G -> A^×` with `q(r(g))=rho(g)`. The action

\[
g\cdot x=r(g)x r(g)^{-1},\qquad x\in K,
\]

is a genuine action and is independent of the chosen unit lifts. The coefficient object is the actual additive kernel as a `Z[G]`-module, not an assumed Selmer space or cotangent homology.

Define

\[
c_r(g,h)=\bigl(r(g)r(h)-r(gh)\bigr)r(gh)^{-1}\in K.
\]

Associativity gives `d²c_r=0`. Replacing `r` by another lift changes `c_r` by an actual group-cochain coboundary. Consequently the class

\[
o(\rho,q)=[c_r]\in H^2(G,K)
\]

is independent of the provisional lift, in the common coefficient action. This uses Mathlib's actual `groupCohomology.H2`, defined by its inhomogeneous cochain complex.

The release proves

\[
\boxed{\exists\widetilde\rho:G\to A^\times,\ q\widetilde\rho=\rho
\quad\Longleftrightarrow\quad o(\rho,q)=0.}
\]

If `c_r=db`, the correction is explicit:

\[
\widetilde\rho(g)=(1-b(g))r(g).
\]

The square-zero condition makes `1-b(g)` a unit. This corrects the original representation, not an auxiliary enlargement.

Principal declaration:

```text
Komorebi.StrongArtin.SquareZeroH2.lifts_iff_constructed_H2_class_zero
```

## Matrix representations

For a surjective homomorphism of commutative coefficient rings `R -> S` with square-zero kernel, the entrywise map on finite square matrices is surjective and also has square-zero kernel. The theorem therefore applies to genuine invertible-matrix representations:

\[
\rho:G\to\mathrm{GL}_n(S),\qquad
\rho\text{ lifts to }\mathrm{GL}_n(R)\iff o(\rho,q)=0.
\]

The coefficients here are the actual kernel of the matrix-ring map. No residual irreducibility, finite-group-order, or principal-ideal assumption is needed.

```text
Komorebi.StrongArtin.SquareZeroH2.matrix_representation_lifts_iff_H2_zero
```

## Fixed restriction

Let `H <= G` and suppose the provisional section is already a prescribed multiplicative lift on `H`. A correction must satisfy `b|H=0` to preserve this map literally.

Define the relative degree-two quotient explicitly:

\[
H^2_{\mathrm{fix}(H)}
=\frac{\{c\in Z^2(G,K):c|_{H\times H}=0\}}
{d\{b:G\to K:b|_H=0\}}.
\]

Lean proves that the constructed relative defect class vanishes exactly when there is a representation lift agreeing with the prescribed map on `H`.

```text
Komorebi.StrongArtin.SquareZeroH2.Datum.
  fixed_restriction_lifts_iff_relativeObstruction_zero
```

This is degree two of the explicit kernel-of-restriction cochain complex. The absolute component uses genuine Mathlib H²; the relative component is an explicit quotient built using Mathlib's actual cocycles and differential. No comparison with continuous relative Galois cohomology is claimed.

## Two nonvanishing tests

1. **Absolute obstruction:** the character `C3 -> (Z/9)^×` sending a generator to `4` does not lift to `(Z/27)^×`. All residues above `4` have cube `10`, not `1`, modulo `27`. Its constructed Mathlib H² obstruction is proved nonzero. The wrap-around defect of the chosen section is `9`.
2. **Relative obstruction despite absolute liftability:** the trivial `C4 -> (Z/2)^×` representation lifts absolutely. But prescribe that the order-two subgroup generator lift to `3` modulo `4`. No extension exists because every unit modulo `4` squares to `1`. Lean proves the absolute obstruction is zero and the relative obstruction is nonzero.

These are counterexamples to universal lifting shortcuts, not to Strong Artin.

## Verification and scope

- 9 additive source modules, 783 lines.
- 49 theorem declarations, 29 definitions, 8 abbreviations, 1 structure.
- 1 unchanged ancestral source module.
- 10 source modules plus 1 all-constant axiom audit in the direct fresh replay.
- 87 explicitly named additive constants audited.
- No active `sorry`, `admit`, custom `axiom`, custom `opaque`, `unsafe`, or `native_decide` markers.
- Axiom dependencies limited to `propext`, `Classical.choice`, and `Quot.sound`.

The finite examples use kernel-checked `decide`. Mathlib's pinned compiled cache is reused. This is not a fresh rebuild of Mathlib or all ancestor branches.

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

For deliberately bounded batches use `--max-modules 5`, then `--resume`. The verifier records `PARTIAL` until all required invocations and axiom checks have succeeded.

See `PROOF_LEDGER.md` for exact declarations, `RESULT.json` for compiler evidence, and `RESEARCH_BOUNDARY.md` for the remaining arithmetic gaps.
