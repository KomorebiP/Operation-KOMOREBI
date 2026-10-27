# P46 rational rotation model: scoped source review

Base checkpoint: LSM-0.15.0. Parent delivered archive SHA-256:
`85b8a25021b665da32f7328ced65d797b2a383464f01a3a2962f0b1bd8214b05`.

Audited source: `KomorebiLSM/RotationModel.lean`, SHA-256
`3795b6684f81ec22edbc962230adab3a70f98af9e5cdb9304e1b6e7ead3f9de1`.
The raw manuscript target is Proposition 46 in the frozen Foundations, with mass
coordinate t, initial state (1,1,0), the rational 3/5,4/5 rotation, and two probe
operators having effects (t+x)/2 and (t-x)/2.

## Scoped verdict

Proved as written for the constructed-model validity sector. This does not by
itself close all of P46: density, canonical-cone equality, cone uniqueness and
the finite-generator obstruction remain separate source obligations. Reachable
and observable dimension are proved in the separately owned RotationRank module.

## Dependency derivation

1. Every branch is explicitly the real cast of a rational matrix.
2. The rotate operator preserves t and x²+y² exactly.
3. Membership in the Lorentz cone implies |x|≤t. Each probe effect is therefore
   nonnegative and each image is that effect times the retained initial point.
4. The cone is preserved by nonnegative scaling and by each branch. Induction
   gives cone preservation for every chronological word.
5. Actual branch masses sum to the incoming mass for both actions. Consequently
   every normalized cone state defines a genuine causal law. The inherited
   causal-law theorem bounds all its future probabilities between zero and one.
6. Positive branch normalization stays in the normalized cone, and each positive
   probe posterior is exactly the retained initial point.

No rank, spectral, density or desired probability-validity conclusion is supplied
as an assumption to these endpoints. Validity is not derived from entrywise
matrix positivity: the rotation matrix has entry -4/5.

## Boundary review

- The zero vector belongs to the cone and the impossible rotate outcome has the
  zero operator.
- All-word statements include the empty word.
- Normalized-state probability bounds explicitly require mass one.
- A posterior is interpreted only on branches with positive likelihood.
- The probe reset identities also hold algebraically outside the cone whenever
  the displayed probe effect is positive; this stronger scope does not replace
  the cone validity theorem.

## Validation

The result receipt records a fresh warnings-as-errors compilation, axiom audit
of all 55 named declarations, kernel replay of the module, and the mathematical
rejection of an entrywise-positivity strengthening. Only propext,
Classical.choice and Quot.sound occur in named-declaration dependency audits.
Imported upstream Lean and Mathlib are pinned, rather than exhaustively replayed.

The development failures were routine tactic/API issues: finite vector access
simplification, a redundant tactic-focus warning, a generic matrix rewrite that
was too aggressive as a simp rule, a normalization name ambiguity, and explicit
cancellation of the positive branch-effect denominator. They were resolved with
coordinate lemmas, targeted rewriting and the actual nonzero effect. No
mathematical claim was weakened to resolve those diagnostics.

Review provenance: author self-review. The coordinator's independent internal
source review and cumulative delivered-source checks are separate steps.
