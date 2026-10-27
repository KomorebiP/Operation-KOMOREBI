# Strong Artin Lean v0.14.0 — Cyclotomic-Depth / Pre-Chebotarev Selection — Checked

**Author:** Komorebi P.  
**Base checkpoint:** `Strong_Artin_Lean_v0.13.0_Relative_Projector_Detection_Checked.zip`  
**Base SHA-256:** `a1bb7aa1b591fbe6e8bb15261d3b26cf3dfc5e033b328ffd6df3c4a525c20057`  
**Status:** fifteen additive modules, with the v0.12/v0.13 dependency closure, are replayed by the included verifier with warnings treated as errors.

## Purpose

v0.13 proved that relative/off-scalar spectral projectors separate the adjoint quotient by the scalar cyclic line. v0.14 connects that finite representation-theoretic result to degree-one group cohomology and to the element-selection step immediately before Chebotarev.

The main coefficient object is now the quotient representation

```text
End_k(W) / k·1
```

rather than the full adjoint representation together with a separate “nonscalar cocycle value” hypothesis.

## Main progression

1. A residual-kernel cocycle value detected by a linear probe can be combined with any prescribed residual element using only two candidates, `g` and `sigma * g`.
2. Actual centered projector traces instantiate that abstract two-point selector.
3. For a finite quotient of order nonzero in the coefficient field, restriction on `H¹` is injective.
4. Hence every nonzero `H¹` class has a nonzero cocycle value on the corresponding normal subgroup.
5. The scalar line is invariant under conjugation, so the transverse adjoint quotient is an actual `Rep` object.
6. Relative spectral projectors descend to this quotient and jointly separate it.
7. Therefore a nonzero transverse `H¹` class automatically supplies a detected subgroup value; no extra nonscalar-value assumption is needed.
8. If `T ≤ S`, conjugation is trivial on `S/T`, and the coefficient representation has no fixed vectors, nonvanishing on `S` survives to `T`.
9. Finite-group averaging plus Schur’s lemma proves that the transverse adjoint quotient has no fixed vectors for an irreducible finite residual image whose order is nonzero in the coefficient field.
10. Pullback through a surjective global-to-residual map preserves that no-fixed-vector result.
11. Combining all blocks gives a relative Taylor–Wiles pre-Chebotarev element: a nonzero transverse `H¹` class produces an element with the prescribed residual image, trivial cyclotomic label, and nonzero actual centered-projector evaluation.

## Main capstone

The final theorem is

```text
Komorebi.StrongArtin.RelativeTaylorWilesPreChebotarev.
  exists_deep_label_preserving_projector_detected_element
```

In symbolic form, under the stated finite residual-image, irreducibility, prime-to-characteristic, subgroup, centrality, and relative spectral-detection hypotheses,

```text
0 != [f] in H¹(G, Res_res(End(W)/k·1))
```

implies the existence of an actual centered projector index `i` and an element `gamma` satisfying

```text
res gamma = res g
cyc gamma = 1
transverseProjectorProbe i (f gamma) != 0.
```

The theorem is deliberately pre-Chebotarev. It constructs the group element with the correct finite labels and nonzero probe evaluation. It does not assert that this element occurs as an unramified Frobenius class.

## Cyclotomic-depth survival theorem

The new survival block proves the following abstract mechanism. Let `T ≤ S ≤ G`. Assume:

- `S` acts trivially on the coefficient representation;
- conjugation by `G` is trivial on `S/T`;
- the coefficient representation has no nonzero `G`-fixed vector.

Then

```text
(exists s : S, f s != 0) -> (exists t : T, f t != 0).
```

The proof is elementary but structurally important. If `f` vanished on `T`, then the cocycle conjugation identity and centrality of `S/T` would force every value `f(s)` to be fixed by `G`, contradicting the no-fixed-vector condition.

For the transverse adjoint quotient, the no-fixed-vector condition is proved by:

```text
irreducibility + Schur + finite-group averaging + |Gamma| != 0 in k.
```

## Exact boundary

This checkpoint does **not** prove:

- a Chebotarev theorem or the occurrence of the selected element as Frobenius;
- the arithmetic centrality/linear-disjointness statement for a concrete cyclotomic tower;
- identification of the centered trace probe with the local Tate-duality quotient defining a Taylor–Wiles condition;
- simultaneous selection of a complete finite Taylor–Wiles set;
- relative patching, `R=T`, or maximal Cohen–Macaulay support over the cyclic defect algebra;
- occurrence of every weight-zero finite-Satake packet in determinant-bearing cohomology;
- Strong Artin.

The next external/arithmetic interface is now exact:

```text
pre-Chebotarev group element
    + finite Galois quotient carrying all labels
    + Chebotarev
    + local Tate-duality identification
-> one genuine detecting Taylor–Wiles prime.
```

## Verification

Pinned environment:

- Lean `4.34.0-rc2`
- mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- `-DwarningAsError=true`
- no `sorry`
- no `admit`
- no custom `axiom` declarations

The verifier checks the exact v0.13 base archive hash, extracts the required v0.12/v0.13 source closure, and compiles it together with all v0.14 modules. It supports bounded resumable runs:

```bash
python3 verify.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --max-checks 4 \
  --resume
```

Repeat until the verifier reports `PASS`. Omit `--max-checks` to compile all remaining modules in one process.

## Fresh release replay

The release replay completed with exit code `0` after the verifier-path repair recorded in `FAILURE_LEDGER.md`.

- dependency modules replayed: `14`
- additive v0.14 modules replayed: `15`
- additive theorem/lemma declarations: `29`
- additive definitions/abbreviations: `3`
- prohibited proof escapes: `0`
- result manifest: `RESULT.json`

The first packaged attempt failed only because sources from several checkpoints were compiled under the wrong Lean `-R` root. The corrected verifier stages the exact dependency closure beneath one root and then recompiles every module.
