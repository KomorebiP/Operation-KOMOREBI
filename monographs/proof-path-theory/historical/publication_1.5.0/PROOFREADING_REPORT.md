# Proof Path Theory — monograph and proofreading report
## Edition 1.3.0 · 19 October 2026

**Source:** the supplied complete v1.2.0 package and its 46-page manuscript.
**Output:** a 50-page monograph with the complete theory, 14 figures, editable
LaTeX, Python source, tests, formal source, and an explicit verification history.

## 1. Presentation and reading order

The article layout has been replaced by the Komorebi monograph design: a cream
and teal cover, quiet running headers, serif mathematical text, sans-serif
headings, roman front matter, and separately numbered main text. The abstract
has become a prose preface. A reading guide distinguishes written mathematics,
finite computations, and inherited formal evidence.

Five parts now carry the argument. The ambient field and failed-route discussion
follow the field definition. Komorebi Space, local models, gluing, and information
counts precede the compression and memory theory. Revision and review form their
own part. Worked examples and implementation follow the mathematics rather than
interrupting the bridge construction.

The closing material includes a notation-and-hypotheses appendix, the 33 stable
result identifiers, reproduction instructions, and a complete importable JSON
record. The conclusion and appendices begin on dedicated pages. Section numbers
have changed, but stable result IDs have not. `editorial/section_crosswalk.json`
and `editorial/result_crosswalk.csv` map earlier references to the monograph.

All 14 mathematical figures are retained. Two figure titles were corrected: the
architecture is no longer labeled version 1.0, and the dependency-change figure
says that descendants require review rather than that they become false. The
refinement plot is now attached to an explicit worked calculation, avoiding an
isolated figure page. Unnecessary prose semicolons and awkward compounds have
been removed without altering code identifiers or mathematical terminology.

## 2. Mathematical corrections

### Uniform task sufficiency

The old definition could be read as allowing a decoder for a single already-known
archive. That would make sufficiency trivial: a constant decoder could simply
return the answer. The corrected definition fixes an archive domain, an encoding
scheme on that domain, and **one decoder per task that works for every archive**.
Decoders are defined on attained encodings. Computability and efficiency remain
additional requirements, not consequences of this set-theoretic definition.

The minimal-compression counterexample now uses the explicit family
`(C0, x, y)` with independent binary side records. It proves distinct least
retention masks for the two coordinate tasks under a fixed mandatory certificate.
It does not incorrectly rule out lossless recoding. The all-predicate/injective
encoding theorem remains separate and retains its existing formal interface.

### Certificate cores and the admitted-leaf boundary

Backward dependency expansion must stop at an admitted premise, axiom, or
external result. A recorded derivation of that admitted statement is not an
additional obligation of the chosen certificate. The corrected AND-DAG definition
uses precisely that boundary and treats zero-premise certified justifications as
rules rather than silently converting them into external assumptions.

The unique-core result is now stated as a **least pair of selected nodes and
selected justifications under componentwise inclusion**. Minimizing only nodes
can leave unused justifications in a record. Minimizing only justifications can
leave extra nodes. Neither single-coordinate criterion by itself makes the whole
record unique. The written proof now establishes inclusion of the complete core
pair in every certificate. The indexed linear-extraction bound explicitly counts
required premises and visited premise incidences.

### Representation and transport contracts

The certified category is constructed as a path category, with any additional
path identification required to respect composition. An abstract functor does
not establish the intended truth of arbitrary target labels. That requires the
separate semantic-soundness assumptions.

A representation portfolio is a tagged tuple, not an untagged union. Projection
onto a retained coordinate then gives the required decoder without losing which
encoding supplied which value. Proof compilers are maps on archive families,
not arrows whose domain is one isolated archive.

### Graph, numerical, and probabilistic hypotheses

Weighted domination counts only targets initially reachable from the declared
starts, avoiding vacuous domination of an unreachable target. Submodular coverage
keeps the bridge graph fixed while varying the retained starting set. Deleting
unretained intermediate vertices would be a different optimization problem.

The greedy bound states its positive integer budget range. Zero and saturated
budgets are separate cases, and arbitrary-cost ratio heuristics do not inherit
the cardinality theorem automatically. The additive loss model uses numerical
weights rather than arbitrary ordinal rankings. Zero-total normalization is
specified.

The correlated-review model states unbiased errors, positive common variance,
and the admissible correlation range. Effective reviewer count is a positive
real variance-equivalent quantity, not a claim about a literal fractional number
of people. Covariance-aware weighting still does not remove an unmodeled common
bias.

The randomized-label discussion now specifies a finite sample, complete random
assignment with nonempty groups, fixed potential responses, consistency, and no
interference. The expected difference in group means equals the sample average
effect. Population generalization requires additional sampling assumptions. This
is a conditional mathematical argument, not an empirical study of reviewers.

### Revision, refinement, and provenance

Append-only persistence now preserves admitted-leaf status, evidence,
interpretation, and hypotheses as well as stored nodes and rules. The affected
descendant set identifies where review is required, not where falsehood follows.

Refinement uses a non-strict recovery order and a declared unresolved-work score.
A small score does not mean a proof is approximately valid. The depth argument
avoids dividing by zero weights and treats the all-zero objective explicitly.
Stopping ratios require positive incremental cost and do not generally give a
global optimum. The phrase proof cube does not assert an undeclared cubical
complex.

Digest stability distinguishes identical serialized bytes from merely similar
records. Different inputs give different digests only when a collision does not
occur. No unconditional hash-security theorem is asserted.

### Source, examples, and formal boundaries

The finite observation theorem explicitly names a finite field and a
finite-dimensional vector space. Its cardinalities remain distinct from the
written uniform-entropy interpretation. The appendix JSON now contains both
referenced nodes and labels its illustrative rule as a model assumption.

The all-patch equivalence is not presented as proof that arbitrary proper-patch
data extend. Whole-support gluing supplies that separate extension result under
its coverage and matching hypotheses. A declared-field countermodel is not a
counterexample to an arbitrary mathematical interpretation of its node labels.

## 3. Software corrections and reproduced failures

Two changes in `certificate.py` were needed to match the revised mathematical
contract.

1. `is_and_dag` now follows only the relevant backward expansion and stops at
   admitted leaves. Against the original v1.2.0 source, the new leaf-boundary
   regression fails. Against v1.3.0 it passes.
2. `minimum_certificate` no longer discards a branch using a fixed `1e-12`
   tolerance. It compares sums as exact rational values of the stored binary
   floating-point costs. This also prevents a large shared base cost from
   rounding away a smaller genuine difference between alternative routes.
   Four tiny-cost and large-base regressions fail against the original source
   and pass after the correction.

These are genuine implementation fixes, not just different tolerances in the
tests. Public cost summaries remain floating-point values. The solver does not
recover a user's intended decimal before conversion or remove its exponential
search complexity. Its explicit search-state limit remains in place.

The complete suite now has **111 passing tests**, including 15 additional cases
for the corrected contracts. The original failure diagnoses, final passing test
log, and source diff are included. They are labeled as different runs rather than
silently turning an earlier failure into a pass.

## 4. Verification performed for this edition

| Check | Outcome |
| --- | --- |
| Original finite suite before edits | 96 passed |
| Expanded finite suite | 111 passed, no failures or skips |
| Exact certificate/brute-force comparisons | 18 passed |
| Greedy coverage instances | 100 passed |
| Retention-algebra identities | 1,024 passed |
| Covariance-formula checks | 114 passed |
| Exhaustive binary realization systems | 5,039 passed |
| Binary feasibility split | 4,359 feasible, 680 infeasible |
| Existing native export, checked through current importer | 5 roots, 195 nodes |
| Stable result identifiers | All 33 retained |
| Formal source/configuration files compared | 17 unchanged |
| Inherited Lean evidence files compared | 35 unchanged |
| Monograph | 50 pages and 14 figures |

The final dated machine-readable report also records the clean PDF compilation,
preflight, package-build and isolated-install results, source identity checks,
and file hashes. Rendered pages were inspected for clipped text, broken formulas,
figure placement, and table layout. The PDF is not claimed to be a tagged
accessibility or PDF/UA-certified document.

## 5. What this review does not claim

No new Lean compiler or kernel replay was run in this editorial environment.
The eight production modules, the prior 42-theorem/78-declaration inventory, and
the v1.2.0 compiler evidence are preserved unchanged. Hash comparison establishes
identity with the supplied files, not a new formal proof.

The whole manuscript is not Lean-formalized. The two Python fixes and all
implementation behavior are not universally verified by Lean. The native
exporter was executed in the preceding release, while this review checks the
existing export through the current importer. It does not re-export declarations
or reconstruct lost discovery history.

This is an editorial and mathematical proofreading pass with executable checks,
not independent peer review, a comprehensive historical-priority survey, or an
empirical validation of the social models. The redistribution license remains
an author decision. These boundaries are stated in the monograph and the package
instead of being hidden in the delivery message.
