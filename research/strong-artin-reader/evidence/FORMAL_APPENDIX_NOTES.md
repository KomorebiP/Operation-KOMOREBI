# Formal appendix authoring and review notes

Date: 8 October 2026.

Authored file: `paper/formal_appendix.tex`.

Final source SHA256:
`fe5c7ef5adb27b4bbaa8f74b4444a401749f7e7583bae83f0af1776f21ea7f79`.

Length: 4,686 whitespace separated source words. Nine substantive subsections
develop the mathematical interfaces without a global automorphy conclusion.

## Source grounding

The appendix was written from the recovered project source, not from search
snippets or an assumed abstract of the project. Main reading paths were:

- `lean/history/v0.18/src/FiniteCyclicH1Model.lean`
- `lean/history/v0.18/src/FiniteCyclicFrobeniusH1.lean`
- `lean/history/v0.24/src/SyzygyCompatibleTarget.lean`
- `lean/history/v0.24/src/SyzygyBoundaryExamples.lean`
- `lean/history/v0.25/src/GradedCompatibleHensel.lean`
- `lean/history/v0.25/src/PolynomialMovingSyzygyHensel.lean`
- `lean/history/v0.26/src/RepresentationObstructionChoice.lean`
- `lean/history/v0.29/dependencies/SquareZeroRepresentationDefect.lean`
- `lean/history/v0.29/dependencies/RepresentationDefectTwoCocycle.lean`
- `lean/history/v0.29/dependencies/RepresentationH2LiftingCriterion.lean`
- `lean/history/v0.29/src/ContinuousH1GluingObstruction.lean`
- `lean/history/v0.29/src/LocalGaugeExactSequence.lean`
- `lean/history/v0.36/src/FiniteBranchCompactness.lean`
- `lean/history/v0.36/src/SimultaneousGaugeBranch.lean`
- `lean/history/v0.38/PROOF.md`
- `lean/history/v0.38/RESEARCH_BOUNDARY.md`
- `lean/history/v0.38/SELF_REVIEW.md`
- `lean/history/v0.38/src/NCPowerEstimates.lean`
- `lean/history/v0.38/src/MatrixInverseCertificate.lean`
- `lean/history/v0.38/src/EffectiveMatrixControls.lean`
- `lean/history/v0.38/checks/exact_matrix.py`
- `evidence/LEAN_COVERAGE.md`
- `evidence/independent_run/results.json`

## Mathematical content and explicit boundaries

1. Cyclic first cohomology is derived as `ker N / im(T-I)`. The simplified
   whole coefficient quotient requires `N=0`. Coprime averaging is proved
   using `(T-I) sum j T^j = e-N`, including the necessity of dividing by `e`.
   The adjoint action of `diag(1,-1)` on `M2(F3)` gives H1 dimension zero for
   C2 and dimension two for C6.
2. A square zero ring extension uses its actual kernel as the coefficient
   module. Unit lift conjugation defines the action. Associativity derives a
   genuine inhomogeneous two cocycle, and section changes add a coboundary.
   The exact lift iff obstruction zero criterion is proved, without asserting
   obstruction vanishing. The C3 generator 4 modulo 9 has no order three lift
   modulo 27. Its explicit carry cocycle has no primitive.
3. Continuous primitives and restrictions are retained for the continuous
   lifting problem. After absolute cancellation, local matching up to
   independently chosen local conjugators is measured by an H1 restriction
   cokernel. No localization surjectivity is inferred.
4. Algebraic dual separation identifies the linear image with the target
   annihilating all syzygies. A worked plane image distinguishes the original
   correction system from a surjective augmented one. Moving relations,
   residual exactness and faithful leading layers are kept explicit for the
   nonlinear iteration. The Z/8 quadratic remainder and Z/4 nonsplit
   compatible submodule demonstrate failed stronger interfaces.
5. The ordered matrix power derivative and both remainder recursions are
   derived. The full uniform ultrametric Lipschitz remainder estimate is
   proved without degree or dimension factors. Ordered cubic words illustrate
   why scalar differentiation cannot replace the matrix operator.
6. An exact additive two sided inverse gives an iff description of the power
   ball image, with uniqueness. Both inverse identities have explicit roles.
   A matrix unit certificate for `Q=p^(-s)B`, integral `B`, makes `m>s`
   sufficient for a finite congruence criterion modulo `p^(m+s)`. The root is
   integral. The unit conclusion retains positive degree and unit target.
7. The unipotent 2 by 2 square example has `s=2`, greater than `v2(2)=1`.
   Its derivative is singular modulo 2 but invertible over Q2. An actual
   noncommuting root and a rejected target are calculated. The diagonal
   center `(1,-1)` is a genuinely singular contrast.
8. Finite branch compactness is stated for a tower of finite solution sets
   indexed by all natural number levels. Joint all depth nonemptiness gives
   a coherent tower. Separate solutions to each local requirement do not
   establish joint nonemptiness. A shallow C3 scalar branch stops at the next
   coefficient level. No uniform finite horizon is inferred for the general
   singular or simultaneous problem.
9. Historical Lean receipts, authenticated source recovery and this edition's
   blocked fresh replay are distinguished in the manuscript itself. No
   historical result is described as newly compiled.

## Exact checks performed for the appendix

An in memory Python check on the final source passed:

- Balanced LaTeX environment counts.
- Unique labels and all appendix `eqref` targets defined locally.
- No semicolons or TODO, FIXME or TBD placeholders in the appendix.
- Both products `BJ` and `JB` equal `4 I4` for the displayed unipotent
  derivative and integral coefficient matrix.
- Positive target coefficient vector equals `(0,0,32,0)`.
- Rejected target coefficient vector equals `(0,16,0,0)`.
- All nine entries of the explicit C3 normalized defect agree with the carry
  cocycle array `[[0,0,0],[0,0,9],[0,9,9]]` modulo 27.
- All 27 two cocycle identities for that array pass modulo 27.
- All nine normalized possible one cochains into the actual three element
  kernel fail to have the displayed cocycle as their coboundary.

These checks are bounded exact arithmetic and source syntax checks. They do
not certify arbitrary prose arguments or replace Lean. The independent
controls in `evidence/independent_run/` have their own separate execution
record and scope.

## Independent mathematical review

The independent reviewer reconstructed the first draft and found two wording
improvements: make `K>=0` explicit, and specify all natural number levels
instead of describing a “finite tower” in a way that could mean finite
height. Both were implemented.

The reviewer then rechecked the final additions and reported mathematical
PASS at the final SHA256 above. This includes the carry cocycle nonprimitive
argument, syzygy plane example in every characteristic, normalized error
independence, ordered cubic expansion and fixed point digit estimate.

## Conservative mathematical proofreading

Mode: self review of the complete new appendix using the math proofreading
skill. The shared preamble and main author's notation were read first.

- Routine checks: prose, theorem and proof structure, delimiters, labels,
  notation and locally resolved equation references.
- Mathematical token changes during conservative proofreading: none.
- Mathematical audit changes: explicit nonnegative inverse bound hypothesis.
  The finite tower wording was clarified without changing the intended
  theorem.
- Unresolved mathematical findings in this appendix: none reported by the
  independent reviewer. The arithmetic attachment and global existence
  boundary is deliberately unresolved and stated as such.
- PDF compilation and visual QA: owned by the root build workflow, not claimed
  as performed by this appendix subtask.

## Failed operations and their resolutions

1. An initial filesystem read used `lean/v0.38/PROOF.md` and
   `paper/main.tex`. Those paths did not exist at that point. The recovered
   proof is actually under `lean/history/v0.38/PROOF.md`, and the main paper
   was still being written. The reading paths were corrected immediately.
2. One multi hunk patch failed because its context did not exactly match the
   current source. The failed patch changed no file. It was reapplied with
   exact contexts and all resulting additions were independently reviewed.
3. The edition's portable Lean kit retrieval returned HTTP 403, as recorded
   by the Lean subtask. No fresh compiler calls were possible. Historical
   successful receipt authentication and fresh bounded arithmetic controls
   remain separate from a new Lean replay.

No mathematical test failed on the final appendix. No universal obstruction
vanishing, automorphic carrier construction, new Strong Artin case or global
automorphy proof is claimed.
