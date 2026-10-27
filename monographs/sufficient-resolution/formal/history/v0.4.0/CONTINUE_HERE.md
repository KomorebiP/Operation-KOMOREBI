# Continuation — Sufficient Resolution v0.4.0

Read README.md, BLOCK_04_THEOREMS.md, PROGRESS.md and AUDIT.json completely.
Replay scripts/verify.py with the pinned portable runtime before extending.
Do not treat historical logs as new verification, and do not change prior sources
merely to increase the theorem count.

## Current state

272 theorem/lemma declarations in 22 modules; 357 explicitly named declarations.
The 16 v0.3.0 proof sources are byte-identical. Counts belong to this standalone
program, not the twelve-paper corpus.

The exact core, discrete memory, finite closure test, finite observation horizon,
actual minimal observable model and finite exact certificates remain intact.

Block 04 adds exact defect telescoping and whole-map norm certificates:

    δ_i = q T_i − U_i q
    E_w = q T_w − U_w q
    E_(i::w) = E_w T_i + U_w δ_i
    ||E_w|| ≤ ε H_n(a,b)
    ||O T_w − V U_w q|| ≤ η a^n + ||V|| ε H_n(a,b)

H_0=0; H_(n+1)=a H_n+b^n. Both a=b and zero-rate cases are covered.
If ||T_i||≤1 and ||U_i||≤b<1, the output bound is uniform:
η+||V||ε/(1−b). Arbitrary reduced initialization adds
||V|| b^n ||qx−z||. Operations need not commute; the alphabet need not be finite.

These are norms of complete continuous linear maps. Do not replace them by sample
residuals or individual spectral radii. No finite dimension or completeness is
needed for the new all-word bounds.

Two-stage modeling transports both errors. Split re-encoding with JS=id changes
norm constants but preserves represented outputs. Scalar systems attain the
convolution bound; T=1+ε,U=1 proves unbounded error for every ε>0 in the absence of
growth restrictions.

## Next target

Continuous-time finite-dimensional memory bridge. Derive the hidden equation
z(t)=exp(tD)z0+integral exp((t-s)D)G y(s) ds from full linear dynamics, then derive
the visible Volterra equation and the memory kernel B exp(tD)G. Prove the proper
closure equivalences, retaining prepared initial states versus arbitrary hidden
states. Do not assume the desired memory identity as an input theorem.

Alternative later target: Hilbert-space globalization and conditioning, starting
from the already constructed linear obstruction quotient.

## Modules

The canonical dependency order is the MODULES list in scripts/verify.py and the
imports in Komorebi.lean. Six new modules are ApproximateAlgebra, ApproximateBounds,
ScalarBudgets, StableApproximation, ApproximateComposition and ApproximateExamples.

## Reproduction

    python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
    python3 scripts/validate_manifest.py verification/local-replay/computation-manifest.json --root .

The multi-gigabyte runtime is not duplicated inside this archive. Linux x86_64
portable Lean 4.34.0-rc2 and pinned Mathlib artifacts are required.

## One-line restore prompt

Open this ZIP, read CONTINUE_HERE.md and PROGRESS.md, replay the pinned verifier,
then prove the continuous-time hidden-state memory bridge from the full dynamics,
preserving all existing proof sources, initialization distinctions and claim boundaries.
