# Strong Artin Lean v0.10.0 — checked modular continuation

## Status

This release **does not prove Strong Artin**. It closes the principal internal finite
representation-theory gap left at v0.9 for the prime-cyclic quotient-prime residual step.

The v0.9 base source is preserved byte-for-byte. Four additive Lean modules prove, in
characteristic `p`, that finite-dimensional semisimple representations of a finite group
with equivalent restrictions across a normal subgroup `H` with `G/H ≃ C_p` are already
equivalent. The exported application theorem is:

```text
Komorebi.StrongArtin.QuotientRestriction.semisimple_residual_collapse_cp
```

Conceptually:

```text
char K = p
G finite, H normal, G/H ≃ C_p
rho, sigma finite-dimensional semisimple K-representations
Res_H rho ≃ Res_H sigma
---------------------------------------------------------
rho ≃ sigma
```

Specializing `K = ZMod p` yields the unconditional internal residual-collapse theorem
needed by the Strong Artin cyclic recursion. The v0.9 property
`SemisimpleCharpolyRigidityFp` is retained as a useful general Brauer–Nesbitt interface,
but it is **not needed** by this new prime-cyclic collapse theorem.

## New proof chain

1. Convert group-algebra linear maps/equivalences back to representation intertwiners.
2. Prove a stronger Hom-lifting statement: across a defining-characteristic `C_p`
   quotient, every nonzero restricted intertwiner yields a nonzero ambient intertwiner.
3. Deduce support reflection for irreducible ambient types.
4. Prove restricted equivalences preserve each ambient isotypic component.
5. Apply the inverse restricted equivalence to obtain equality of field dimensions of
   corresponding isotypic components.
6. Prove equal-dimensional finite isotypic modules of the same simple type are
   `K[G]`-equivalent.
7. Map nonzero isotypic components from source to target, prove injectivity, and use the
   reverse construction plus finiteness to prove bijectivity.
8. Assemble the componentwise equivalences through Mathlib's internal direct-sum
   equivalence to obtain a global `K[G]`-linear equivalence.
9. Convert that module equivalence back to `Representation.Equiv`.

## Verification

Pinned inherited runtime:

- Lean/Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

The v0.9 base source SHA-256 in this release is
`231f1833dc3f0eb783c2a827463f0a929ded245199d7179d68e27fb2bc758e99`, exactly matching
the canonical v0.9 source used at the start of this continuation.

The base was freshly rebuilt successfully in the restored pinned runtime. The final
`BrauerNesbittStep04.lean` root was freshly compiled with `-DwarningAsError=true` after
the base rebuild and returned RC=0. Representative `#print axioms` output for the final
collapse theorem contains only:

```text
propext
Classical.choice
Quot.sound
```

The new modules contain no `sorry`, `admit`, or custom `axiom` declaration.

A direct monolithic merge was also attempted. It exceeded the execution limit without
emitting a Lean theorem error, so that monolithic file is **not certified** and is not the
canonical v0.10 form. The checked form is the modular chain included here.

## Files

- `src/StrongArtinFiniteCore.lean` — exact inherited v0.9 core.
- `src/BrauerNesbittStep01.lean` — Hom-lifting and representation/module bridges.
- `src/BrauerNesbittStep02.lean` — finite isotypic multiplicity from field dimension.
- `src/BrauerNesbittStep03.lean` — block preservation, equal block dimensions, block equivalence.
- `src/BrauerNesbittStep04.lean` — component bijection, global direct-sum assembly, final residual collapse.
- `PROOF_LEDGER.md` — theorem-level summary and boundary.
- `FAILURE_LEDGER.md` — failed development/integration attempts and their disposition.
- `logs/` — positive compiler evidence and inherited-base rebuild evidence.
- `development_logs/` — preserved intermediate compiler diagnostics.

## Remaining Strong Artin boundary

Still external/open, as applicable:

- cross-characteristic Brauer/Nesbitt lifting for the large-residual realization funnel;
- Chebotarev/global Frobenius identification;
- cyclic/solvable automorphic base change and automorphic induction;
- local Langlands compatibility;
- unrestricted residual or ordinary `l`-adic realization of the singular weight-zero
  finite-Satake descents occurring in cyclic Clifford recursion;
- quotient-prime nonregular weight-zero automorphy lifting;
- global cyclic attachment / full Strong Artin.

The main research target after this release is therefore the **global realization gate**,
not the now-closed internal prime-cyclic semisimple restriction step.
