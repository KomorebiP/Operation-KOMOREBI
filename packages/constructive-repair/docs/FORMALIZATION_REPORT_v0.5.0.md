# Constructive Repair v0.5.0 — proof-carrying branch search

**Komorebi P. | 19 October 2026**

## 1. Completed result

The standalone rational-menu producer now uses branch-and-bound and returns a finite proof tree. The Lean checker certifies that every candidate selection represented by that tree is accounted for. It does not enumerate the powerset. In the all-subsets mode neither the input nor its echo contains a table of all subsets.

The combined release has **51 compiled and individually replayed proof modules, with all 526 named theorem dependency lists audited**. All 37 v0.4.0 proof modules are byte-for-byte unchanged. The increment is six general theorems and 142 concrete declarations, not 148 independent mathematical discoveries. The underlying branch-and-bound and linear-algebra principles are classical.

The final authoritative record is `evidence/verification/current/verification.json`, finished at 2026-10-19T18:18:59Z. Earlier completed or interrupted attempts are retained and explicitly superseded.

## 2. Mathematical contract

The input fixes rational matrices D, E, R, a nonnegative natural weight on each candidate column, and one admissibility rule. The rule is either all subsets (`admissible_masks: null`) or exactly a finite explicit list of subsets. The empty list admits none and is distinguished from the all-subsets rule.

For a selected set S, the original equation remains

    D U + masked(E,S) W = -R.

Selected columns are charged even when their particular coefficient row is zero. Neither the certificate nor the search may replace D, E, R, the weights, or the admissibility rule.

A search interval (A,B) represents every T with A ⊆ T ⊆ B. The checker derives the endpoints recursively rather than accepting arbitrary endpoints from a producer. Four tree nodes are permitted:

1. **Bound.** At a fixed optimality threshold c*, establish c* ≤ cost(A). Nonnegative weights imply c* ≤ cost(T) for every T in the interval. This node is forbidden in infeasibility mode.
2. **Separator.** Check YD=0, Y masked(E,B)=0 and YR≠0. The existing downward separator theorem excludes every T⊆B.
3. **Inadmissible.** For an explicit original list, check that no listed selection lies in the interval. This scans that list with `List.all`, not the powerset. The node is unavailable in all-subsets mode.
4. **Split.** Choose an unresolved j∈B\A and supply both children, (A,B\{j}) and (A∪{j},B). Every possible T follows one of those children.

Structural induction proves soundness for every T in the interval. At the root (∅, all candidates), a supplied admissible exact repair plus an accepted threshold tree certifies minimum cost. An accepted infeasibility tree proves there is no repair in the declared admissible family. It does not exclude a new direction or a different arithmetic host.

## 3. Six new general Lean declarations

All are in `lean/KomorebiRepair/BranchCertificate.lean`, namespace `KomorebiRepair.RationalCertificates`.

| Declaration | Content |
|---|---|
| `intervalExcluded_sound` | An excluded original admissibility list has no admitted selection in the interval. |
| `additiveCost_mono` | Adding candidates cannot reduce nonnegative additive cost. |
| `boundCheck_mono` | A checked lower bound passes to a greater cost. |
| `checkBranch_sound` | The entire finite tree proves the required bound or infeasibility for every selection in its interval. |
| `checkTreeOptimal_sound` | An accepted original repair and root tree imply global minimum cost within the menu. |
| `checkTreeNoRepair_sound` | An accepted root rejection tree excludes every admitted selection. |

Supporting types and Boolean definitions do not assume feasibility or correctness. Their semantic input remains the previous original-matrix repair equation. The 142 new concrete declarations include literal decoding, accepted certificates, correction equations, minimum-cost applications, and ten corruption rejections. There are 24 new exported problems: 18 optimal menus and six no-admissible-menu outcomes.

## 4. Executable producer and input binding

`python/branch_menu.py` calls the previous exact Fraction linear solver, retains separating rows, searches intervals, tracks an incumbent, and checks every resulting certificate again. It can prune by all-available-direction infeasibility, original-table exclusion, or incumbent cost. It never treats resource exhaustion as infeasibility.

The end-to-end command is:

    python scripts/certify_branch.py examples/branch_corpus/Branch018_input.json \
      --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
      --output /tmp/komorebi-branch

The directory must not already exist. The command produces local evidence only. A `--certificate` argument checks externally supplied data instead of running search. Original inputs and witness sources are emitted separately. Lean echoes the actual matrices, weights and optional original table. That echo is compared with the external input without evaluating every subset's admissibility and cost.

Status values are `KERNEL_CHECKED_BRANCH_OPTIMAL_MENU`, `KERNEL_CHECKED_BRANCH_NO_ADMISSIBLE_MENU`, and `UNRESOLVED`. A Python-valid certificate is not called kernel checked. Invalid data, an invalid certificate, or exhausted budgets stay unresolved.

Rational cells are exact normalized decimal-string numerator/positive-denominator pairs. Inputs reject floats, booleans masquerading as integers, negative costs, duplicate keys, unexpected fields and unsafe names. Resource limits are 24 candidates, 32-by-32 matrices, 4,096 explicitly admitted selections, and 8,191 certificate-tree nodes.

## 5. Exact tests and compact examples

The final deterministic suite has **204** problems. Of these, **199** small problems are cross-checked both against the unchanged exhaustive v0.4.0 producer and against SymPy's exact rational ranks. This gives 3,173 individual subset feasibility comparisons and 199 prior-producer outcome/cost comparisons. The remaining five are structured 24-candidate examples. They are not exhaustively enumerated by the external oracle; their exported certificates are checked by Lean.

The test suite was adjusted during the audit: one small case was replaced by a 24-candidate nonhereditary table regression, and an extra large empty-table case was added. The final numbers above supersede the earlier 200-small-case development count.

### A five-node optimality tree

Branch018 has D(u)=(u,0,0), residual R=(0,1,1), first two directions (0,1,0) and (0,0,1) with costs two and three, and 22 additional directions on the original correction axis. All 2^24=16,777,216 subsets are admitted.

The producer selects {0,1} at cost five after **five visited tree nodes and six distinct linear solves**. Its tree is:

    split candidate 0
      excluded: separator (0,1,0)
      included: split candidate 1
        excluded: separator (0,0,1)
        included: cost lower bound 5

The proof covers all selections, but does not execute 16,777,216 tests. This intentionally structured example demonstrates compact certification, not a general runtime speedup theorem.

### A one-node rejection

Branch019 has 24 candidate directions on the original first-coordinate correction axis and residual (0,1). The row (0,1) excludes the full upper menu. One tree node and one linear solve certify infeasibility of all 16,777,216 selections.

The other large examples cover zero weights, an original table admitting only the pair {0,1}, and an empty table. The empty table gives vacuous admissible-family rejection, not evidence of a newly discovered arithmetic obstruction.

### Other coverage

Fixtures include fractions, zero-dimensional targets and domains, zero candidates, empty residual families, cost/cardinality disagreement, nonhereditary admissibility, zero-cost candidates, multiple residuals, and a changing incumbent. Ten paired controls deliberately break certificate structure, coefficients or scope.

## 6. Fresh executed verification

| Check | Result |
|---|---:|
| Combined proof modules rebuilt from source | 51/51 |
| Named theorem axiom lists audited | 526/526 |
| Individual same-kernel module replays | 51/51 |
| Original v0.4.0 modules byte-for-byte unchanged | 37/37 |
| New exported original inputs and constraints echoed | 24/24 |
| New paired corruption controls | 10/10 |
| Previous paired corruption controls rerun | 14/14 |
| Separate forbidden-axiom policy control | 1/1 |
| New Python unit tests | 50/50 |
| New exact certificate cases rechecked | 204/204 |
| Small problems against independent ranks | 199/199 |
| Individual subset-rank comparisons | 3,173/3,173 |
| Small problems against the prior exhaustive producer | 199/199 |
| Prior rational/menu unit tests rerun | 84/84 |
| Original unit tests rerun | 20/20 |
| Original audit records reproduced | 3,307 |

The final verification record has 141 uniquely labelled commands and 229 passed checks. Expected nonzero compiler exits are the deliberately invalid rejection files; each is checked for the intended type-mismatch diagnostic. A missing instance or syntax error does not count as a mathematical rejection.

All theorem axiom sets are contained in `{propext, Classical.choice, Quot.sound}`. There is no accepted `sorryAx`, added assumption axiom or native-decision axiom. Concrete reductions use `decide +kernel`.

The positive and negative 24-candidate CLI workflows were freshly executed after the final evaluator correction. Both compiled their imported certificate sources and actual input, audited the resulting theorems, replayed the seven required modules, and matched the original-input echo. A zero-node-budget run returned UNRESOLVED with no compiler invocation. See `evidence/branch_cli_large_optimal`, `evidence/branch_cli_large_negative` and `evidence/branch_cli_budget`.

## 7. Failures discovered and repaired

### Lean API name

The first draft used `Bool.and_eq_true.mp`, which was not available. It was replaced with the actual `Bool.and_eq_true_iff.mp`; the failed source and compiler log are retained by the development compiler harness.

### Verification log collisions

The inherited harness labelled compilation logs by basename. Different namespaces containing `Inputs00` or `Certificates00` could overwrite a log or check entry. Every module was being invoked, but the evidence was not one-to-one. The harness now uses full relative module names, rejects duplicate command labels, and refuses to overwrite an existing verification-output record. The earlier completed run is explicitly superseded under `v0.5.0_attempt01_duplicate_compile_labels`.

### Implicit powerset enumeration

Inspection of the inferred decidability implementation revealed that the original finite-table expression had selected `Fintype.decidableForallFintype (Finset (Fin q))`. Its truth condition was correct, but evaluation could still enumerate all subsets. This contradicted the intended computational advantage.

The implementation now calls `xs.all` explicitly on the original table and proves soundness with `List.all_eq_true`. The inferred evaluator is printed into evidence, and the final release verifier checks for `List.all` and rejects `Fintype.decidableForall`. Two 24-candidate explicit-table fixtures exercise this path. The interrupted audit and former source are preserved under `v0.5.0_attempt02_implicit_powerset_detector` and `evidence/development/`.

No mathematical assumption was weakened to resolve these issues. The final complete verification was rerun after all three corrections.

## 8. Monograph and reproducibility

The monograph is now **68 pages**, with the new proof-tree chapter and an additional declaration, case and verification appendix. The existing ten chapters and earlier release appendices are retained. The final LaTeX build has no overfull boxes, unresolved references, missing characters or rerun-needed warning. All 68 pages were rendered, inspected in contact sheets, and new dense proof/table pages were inspected individually. Page-bound geometry checks found no out-of-page text spans.

The ZIP includes sources and verification evidence, not the compiler, Mathlib cache, compiled object files, or font files. The original v0.4.0 ZIP is retained unchanged in `inherited/`. Final ZIP extraction, manifest and command replay checks are recorded separately in the release-check JSON accompanying the handoff.

## 9. Limits and next restart point

The certificate checker is sound; the entire Python producer is not formally proved correct or terminating. Search, certificate size and finite admissibility lists may still be exponential. No polynomial-time guarantee or minimal proof-tree claim is made.

The external JSON parser, source emitter, hashes and filesystem are tested, not fully formalized. Typed rational decoding and mathematical soundness are proved. Formal conclusions apply to the literal typed input compiled by Lean, with independent emission and the exact echo testing its correspondence to the original input.

Replay is through Lean's own kernel against the pinned imported environment. It is not a second independently implemented checker and does not re-prove all of Mathlib from source.

This remains a standalone experimental extension. It has not been integrated with the authoritative Komorebi Python library or Paper III Lean tree. No unrestricted nonlinear or integral repair, native arithmetic host construction, universal Komorebi Space realization, or change to Conjecture 66 is claimed.

The next restart point is `scripts/certify_branch.py`, `python/branch_menu.py`, `lean/KomorebiRepair/BranchCertificate.lean` and the final PASS record. A useful next step is the previously deferred adapter to the actual library API, or a domain-native constrained example with its own semantic preservation proof. Keep that obligation distinct from the now working exact rational-menu certificate path.
