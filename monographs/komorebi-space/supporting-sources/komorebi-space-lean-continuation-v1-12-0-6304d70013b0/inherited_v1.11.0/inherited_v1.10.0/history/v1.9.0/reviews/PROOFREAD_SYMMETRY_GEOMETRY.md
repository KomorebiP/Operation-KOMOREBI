# Proofreading: symmetry, identified boundaries, phase, and geometry

Mode: conservative EDIT mode under `proofread-math`. The two mathematical scope
issues below received a separate local read-only `proof-audit` pass. This was a
self-review of the supplied manuscript and corresponding archived Lean statements,
not a claim of an independent full mathematical audit of these chapters.

## Full reading coverage

Every line, statement, proof, display, table, and caption in the following files
was read. The preamble, definitions in adjacent portions of these assigned
chapters, concordance entries KS45–KS47, and the two relevant archived source
modules were also inspected.

| File | Lines read | Approximate whitespace-separated words | Result |
|---|---:|---:|---|
| `source/chapters/04_symmetry.tex` | 1–456 | 4,383 | No objective proofreading correction required. |
| `source/chapters/04a_boundary_lab.tex` | 1–70 | 896 | No objective proofreading correction required. |
| `source/chapters/04b_phase.tex` | 1–107 | 859 | Added one missing sentence-ending period. |
| `source/chapters/05_geometry.tex` | 1–641 | 5,308 | Two source-confirmed hypothesis corrections applied after explicit coordinating-agent review. |

Total coverage is 1,274 lines and approximately 11,446 words. Coverage was not
limited to search hits or selected proof blocks.

## Applied routine edit

`04b_phase.tex`, line 75: added a sentence-ending period after
`=x_2y_1-y_2x_1` in the displayed definition of `\kappa`. The display completes the
preceding sentence, and the following sentence begins “This is a directly
observable obstruction certificate”. The edited sentence and display were reread
in context.

Mathematical-token changes: **three reviewed local corrections** in
`05_geometry.tex`. These were initially flagged without editing. After source
comparison and explicit coordinating-agent authorization, the missing hypotheses
were restored:

1. Line 299: added `where \(n\ge1\)` to the scalar-chain setup. This restores the
   positive-length condition required by the claimed residual norm equality.
2. Line 308: changed “A route length bound of \(n\) fails.” to “For \(n\ge2\), a
   route length bound of \(n\) fails.” This makes the strict-failure range explicit.
3. Line 326: explicitly declared **both** `D:E→R` and `C:E→Y` to be continuous
   linear maps into Banach spaces. The roles of local and overlap defects are
   unchanged.

The phase-display period is punctuation, not a mathematical-token change. No
formal source or proof argument was altered. Each changed paragraph was reread in
context. Before/after source text is retained in the companion checks JSON.

## SG-01: positive chain length omitted from KS45 prose

Normalized claim: for the scalar chain with `n+1` vertices, frames `e_i(z)=2^i z`,
candidate `x_i=8·2^i−1`, and root-preserving repair `y_i=7·2^i`, the manuscript says
`‖dx‖∞=1` and `‖x−Px‖∞=2^n−1`, then says the route-length bound `n` fails. The
setup does not restrict `n` to positive values.

Primary verdict: **correct only after a stated restriction**.

Exact locations: `05_geometry.tex`, lines 299–308, subsection “Flatness does not
remove amplification”, source identifier KS45.

Dependency graph:

1. The chain has `n` edges and retains both directed orientations.
2. Every existing forward residual is `1/2`, and every reverse residual is `−1`.
3. At least one edge is necessary to conclude that the maximum residual norm is
   exactly one.
4. The repair discrepancy is `2^n−1` for every natural `n`.
5. Strict failure of the length bound requires `2^n−1>n`, which holds for `n≥2`.

| Obligation | Status | Evidence |
|---|---|---|
| Residual signs on each existing directed edge | Passed | Direct substitution and archived `candidate_forward_defect` / `candidate_backward_defect`. |
| Residual norm equals one for every natural `n` | Failed | `n=0` has no edges and residual norm zero, consistent with the chapter's explicit empty-edge convention. |
| Error formula for all natural `n` | Passed locally | At `n=0` both sides are zero; archived `candidate_error_norm` has no positivity hypothesis. |
| Length bound fails without restricting `n` | Failed as an unrestricted reading | At `n=1`, both sides equal one. The figure caption already states the correct `n≥2` threshold. |
| Formal source has the necessary range restriction | Passed | `AmplifiedExamples.lean:106,139` requires `(hn : 0 < n)`. |

Decisive counterexample: `n=0` gives a singleton vertex set, an empty edge set,
`x_0=y_0=7`, and zero residual. The printed equality `‖dx‖∞=1` is therefore false
at this explicitly permitted boundary case. No numerical approximation is involved.

Strongest safe statement: the residual equality holds for `n≥1`; the error formula
holds for every natural `n`; failure of the route-length bound holds for `n≥2`.
Cheapest correction is to state `n≥1` at setup and `n≥2` at the strict-failure
sentence. This is a hypothesis/range change, so it was first reported to the coordinating
agent. The source-confirmed correction was then explicitly authorized and applied.

Source inspected:
`work/Komorebi_Space_Monograph_v1.7.0/formal/KomorebiSpace/AmplifiedExamples.lean`.
No Lean build was rerun for this editorial task.

## SG-02: the quantitative-descent setup omits the operator class

Normalized claim: in the setup for KS46–KS47, `E` is a real Hilbert space, `R,Y`
are Banach targets, and maps `D:E→R`, `C:E→Y` measure local and overlap defects.
The subsequent argument treats their kernels as closed linear subspaces and
uses bounded linear restrictions and operator norms. The new chapter setup does
not explicitly say that both maps are continuous linear.

Primary verdict: **incomplete, with the smallest missing implication**.

Exact location: `05_geometry.tex`, line 326, with dependencies in KS46's first
paragraph and the following quantitative estimates.

Dependency graph:

1. Bounded linear `D` implies that `ker D` is a closed Hilbert subspace.
2. Bounded linear `C` restricts to a bounded linear operator on `ker D`.
3. Its kernel is closed, so both orthogonal projections exist as stated.
4. These projection properties prove KS46 and feed the KS47 closed-range argument.

The missing named input is the continuous-linearity of both `D` and `C`. It is
suggested by the surrounding operator language, but not stated in this local
setup. The preceding chapter's `D` does not specify a newly introduced `C`.

| Obligation | Status | Evidence |
|---|---|---|
| Both maps are continuous linear in the printed local setup | Conditional | Intended by the proof, not explicitly stated at line 326. |
| Closed linear kernels follow for arbitrary defect maps | Failed | For example, `D(x)=x²−1` on `ℝ` has zero set `{−1,1}`, which is not a linear subspace. |
| Accepted formal source restricts both maps appropriately | Passed | `QuantitativeDescent.lean:25` declares `D : E →L[ℝ] R` and `C : E →L[ℝ] Y`. |
| The printed proof works after restoring that input | Passed locally | Its kernel, restriction, orthogonality, and continuity uses match the archived declaration types. |

Strongest safe statement: the stated conclusions apply to continuous linear
local and overlap defect maps. The cheapest correction is to state that operator
class explicitly in the setup. This adds a mathematical hypothesis and was
first reported to the coordinating agent, then explicitly authorized and applied.

Source inspected:
`work/Komorebi_Space_Monograph_v1.7.0/formal/KomorebiSpace/QuantitativeDescent.lean`,
including declarations at lines 25, 61, 121, and the quantitative bounds.

## Validation and limits

A local source check resolved every reference and citation key in the assigned
files against the available monograph source, and found no mismatched LaTeX
`begin` / `end` environments. The check counts and before/after SHA-256 hashes are
in `PROOFREAD_SYMMETRY_GEOMETRY_CHECKS.json`.

Source hashes for the targeted hypothesis comparison:

- `AmplifiedExamples.lean`: `e95779e1b481e79e479e6bb7b7a3ec4a7ee632c5b96248233504d935515c60c7`.
- `QuantitativeDescent.lean`: `0a35307bbdb5fdc380bb1f8420774efd66a58f494ce74d881fed64e052c0c24d`.

The two identified local scope issues are now resolved by the applied corrections.
No unresolved objective proofreading issue remains in the assigned scope. The audit
verdicts above describe the pre-correction text and preserve the reason for each
mathematical change.

No build command was invented or run. Full document compilation and page rendering
belong to the coordinating agent's synchronized publication build. Visual QA has
not yet been performed in this pass. External citations were checked for local
key consistency only; their substantive theorem support was not re-audited.
