# Strong Artin Lean v0.11.0 — Cyclic Defect / Equivariant Support — Checked

**Author:** Komorebi P.  
**Checkpoint:** v0.11.0 additive continuation from `Strong_Artin_Lean_v0.10.0_Checked_Modular.zip`  
**Status:** fresh Lean replay PASS

## Purpose

This checkpoint formalizes the exact local algebra of the quotient-character defect at a prime-cyclic Strong Artin step and closes the finite branch-support propagation argument needed by a future equivariant patching theorem.

It does **not** prove Strong Artin, an `R=T` theorem, automorphic support nonvanishing, or twist-equivariance of a global Hecke quotient.

## Runtime

- Lean/Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- warnings treated as errors
- fresh packaged verifier exit code: **0**
- prohibited proof escapes in active source: **0 `sorry`, 0 `admit`, 0 custom `axiom` declarations**
- additive theorem/lemma declarations: **31**
- additive definitions/abbreviations: **9**

Representative `#print axioms` reports use only ordinary Lean/Mathlib foundations (`propext`, `Classical.choice`, `Quot.sound`; some results use a subset).

## Main local algebra

For

`A_cyc = O[u] / ((1+u)^p - 1)`, 

the special fiber in characteristic `p` is modeled by

`F_p[u] / (u^p)`.

Lean checks:

- the defect polynomial reduces exactly to `X^p` over `ZMod p`;
- the special-fiber parameter `u` is nonzero, `u^p = 0`, and `u^(p-1) != 0`;
- the special fiber has `F_p`-dimension exactly `p`;
- every algebra map from the special fiber to a reduced `F_p`-algebra kills `u`, hence the reduced special fiber has a unique geometric point;
- the universal defect polynomial is monic of exact degree `p` and its adjoin-root algebra is finite free;
- when a coefficient field contains a primitive `p`th root `zeta`, there are `p` distinct generic evaluation branches `zeta^j - 1`.

Thus the quotient-character ambiguity degenerates from `p` distinct generic branches to one residual point with exact nilpotent thickness `p`.

## Exact cyclic symmetry

Lean constructs the algebra automorphism

`u |-> zeta * (1+u) - 1`

with inverse obtained from `zeta^-1`. On the generic evaluation branches it acts as the cyclic successor, including the final wrap back to branch zero.

## Support propagation

The checkpoint then proves three levels of support propagation.

1. A nonempty subset of `ZMod p` stable under `x |-> x+1` is all of `ZMod p`.
2. For any property of actual generic branch homomorphisms, one supported branch plus stability under the defect twist implies every generic branch has the property.
3. If a quotient ideal is twist-stable and is killed by one generic branch, it is killed by every generic branch; therefore every branch factors through the quotient algebra.

The patching-facing capstone is:

`Komorebi.StrongArtin.CyclicEquivariantQuotient.all_branches_factor_through_equivariant_surjection`

It states that if

- `q : A_cyc -> B` is a surjective algebra map,
- `q` is equivariant for the cyclic defect twist and a compatible endomorphism of `B`, and
- one generic branch factors through `q`,

then **every** generic branch factors through `q`.

## New research boundary

The finite/local branch-propagation problem is closed under an explicit equivariant quotient hypothesis. The next genuinely global target is therefore:

> Construct the automorphic/Hecke quotient `q` in the Strong Artin quotient-prime setting, prove it is nonzero on at least one generic branch, and prove quotient-character twist equivariance (or an equivalent twist-stability statement for its support/kernel).

If those inputs come from a relative patched `R=T` construction over the cyclic defect factor, this v0.11 theorem automatically upgrades one supported branch to all `p` characteristic-zero quotient-character branches.

## Files

- `base/Strong_Artin_Lean_v0.10.0_Checked_Modular.zip` — exact previous checkpoint.
- `src/CyclicDefectAlgebra.lean` — local algebra, special/generic fibers, twist automorphism.
- `src/CyclicSupportStable.lean` — finite cyclic support theorem.
- `src/CyclicBranchSupportStable.lean` — support theorem on actual branch homomorphisms.
- `src/CyclicQuotientSupportStable.lean` — ideal/quotient support propagation.
- `src/CyclicEquivariantQuotientStable.lean` — patching-facing equivariant-surjection theorem.
- `verify.py` — fresh replay verifier against the preserved portable kit.
- `verification/` — release and fresh replay logs.
- `PROOF_LEDGER.md`, `FAILURE_LEDGER.md`, `RESEARCH_BOUNDARY.md` — exact status and next target.
- `SHA256SUMS.txt` — payload hashes.

## Replay

From the extracted checkpoint:

```bash
python3 verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier checks the Lean version, exact mathlib revision, prohibited proof escapes, and recompiles all five modules in dependency order with warnings as errors.
