# Actual ordinary class characters at the Mellin endpoint

This lane attaches the predecessor real-axis integral argument to actual ideal
sums. Let `K` be a number field of degree `d` and let `w` be complex weights on
its ordinary ideal class group. The function used throughout is

\[
S_w(X)=\sum_{0\ne I\subseteq\mathcal O_K,\;NI\le X}w([I]).
\]

It is the finite sum over actual nonzero integral ideals defined in
`IdealClassCharacterSum.lean`, not a supplied function with similar labels.

## Mathematical attachment

1. Integral ideal norms prove the exact identity
   `classCount K C X = classCount K C (Int.floor X : ℝ)` for every real `X`.
   Thus each actual class count is measurable on the whole real line, including
   negative thresholds. The finite class decomposition proves measurability of
   `S_w`.
2. For `∑ C, w C = 0`, the theorem in `IdealClassCharacterBound.lean` supplies
   `‖S_w(X)‖ ≤ M X^(1−1/d)` for every `X ≥ 1`. Neither this bound nor
   measurability remains an input to the new logarithmic-moment result.
3. Since `1−1/d < 1`, the predecessor power-bound theorem yields
   \[
   \int_1^\infty (1+\log x)\,\|x^{-2}S_w(x)\|\,dx<\infty.
   \]
   This includes degree one, where the exponent is zero.
4. The new definition is the actual Bochner integral
   \[
   M_w(h)=(1+h)\int_1^\infty x^{-2-h}S_w(x)\,dx.
   \]
   For every `h ≥ 0`, Lean proves
   \[
   \|M_w(h)-M_w(0)\|
   \le h\int_1^\infty(1+\log x)\|x^{-2}S_w(x)\|\,dx.
   \]
   In particular the right endpoint error is `O(h)`.
5. Nontrivial ordinary class characters have zero sum, so the actual-character
   logarithmic moment and endpoint theorem require only the number field and
   nontriviality of the character.

## Remaining arithmetic inputs

`classCharacter_pole_criterion` uses a finite family of actual nontrivial
ordinary class characters. Given two nonzero simple-pole residues and the
eventual identity

\[
Z(h)=\bigl(p(h)\prod_i M_{\chi_i}(h)\bigr)^e,
\]

it proves `e = 1` and `M_{χ_i}(0) ≠ 0` for every factor. The growth and endpoint
regularity inputs have been removed, but the residues and this arithmetic
product identity are still assumptions. The theorem does not identify the
Mellin integral with an Euler product, construct the required extension, or
prove Frobenius occurrence. Ordinary class characters alone do not supply
additional norm-residue or ray-class conditions.

## Files and verification

The dependency order for this lane is:

1. `IdealCharacterMellinMeasurable.lean`
2. `IdealCharacterMellin.lean`, after `IdealClassCharacterBound.lean`
3. `IdealCharacterMellinPole.lean`

Final compiler status, source and proof-object hashes are recorded in
`privatechecks/class_mellin_verification.json`.

All three modules passed the strict compiler. They add nine theorem declarations
and one definition. The separate named-declaration axiom check passed all ten
declarations using only `propext`, `Classical.choice`, and `Quot.sound`.

Compiler attempts retained in `privatechecks/class_mellin*_attempt*.log`
include resolved namespace, subtype-equivalence, and measurable-cast API
errors. These were elaboration failures; no mathematical hypothesis was added
to repair them. A failed attempt is not counted as verification evidence.
