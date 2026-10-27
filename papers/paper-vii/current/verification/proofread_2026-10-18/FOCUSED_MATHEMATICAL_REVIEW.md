# Paper VII: focused review of the corrected mathematical wording

Date: 18 October 2026.

Scope: the specific meaning and hypothesis issues found during the complete proofreading pass. This report does not replace the manuscript's proofs or the inherited Lean kernel record. The raw source revision is the October 9 monograph carried in the October 11 delivery snapshot. File hashes and exact before/after passages are recorded in `EDITORIAL_EDITS.json` and the reviewer reports.

## 1. Several seeds and the nonempty row condition

**Normalized claim.** For coefficient matrices with a positive row dimension, the family generates the full coefficient space exactly when its vertically stacked matrix has full column rank. The associated dimension bound uses the same hypothesis.

**Verdict: correct only after a stated restriction.** The positive row condition must be carried explicitly into this subsection.

Sources: traditional `parts/03_supplement_03.tex`, subsection “Several seeds: both necessity and construction”; Lean guide `chapters/seed_packets.tex`, subsection “Several seeds: stack them and prove a minimum”; active `SeedOrbit.lean`, declarations `generates_iff_rank`, `seed_count_lower`, and `exists_generating_seeds_iff`.

The dependency chain is: actual left-multiplication generation, stacked-action identity, full-column-rank criterion, and a dimension cancellation using a nonempty row index. The formal statements explicitly contain `[Nonempty d]`. The preceding traditional paragraph also states that this hypothesis is essential.

The smallest relevant boundary check is row dimension zero and multiplicity one. The ambient coefficient space then contains only its zero element, so generation is automatic. The stacked matrix has rank zero, which is not the multiplicity one. This refutes an unrestricted version of the equivalence.

The corrected traditional subsection says “Continue under the positive-row hypothesis above.” The guide says “Continue with a nonempty row index type.” No displayed formula, proof body, or Lean declaration changes. The zero target and empty block conventions remain intact.

Obligations: the missing assumption and corresponding formal hypotheses were checked; the existing proof was preserved; a fresh Lean compilation was unavailable. No open proofreading obligation remains here.

## 2. What the approximate Knill–Laflamme defect controls

**Normalized claim.** The norm defect bounds the difference between each error overlap and its selected scalar code form. It does not by itself bound the nonorthogonality of the original error images.

**Verdict for the unrestricted nonorthogonality reading: refuted, with the smallest valid counterexample.** The displayed overlap inequality remains unchanged and its immediate interpretation has been corrected.

Source: traditional `parts/02_strengthened.tex`, proposition “Meaning of the approximate defect” and its proof.

Take a nonzero one-dimensional code and two identical normalized errors, each equal to the identity divided by the square root of two. Their squared norms sum to the identity. Every compressed cross product is one half of the code projection, so the defect is zero. Both error images are nevertheless the same nonzero subspace. Thus zero defect does not force the original images to be orthogonal.

The valid dependency chain is the definition of the operator-norm defect, compression to code vectors, and the unit-vector bound for the resulting inner product. The corrected sentence reads: “Thus the defect controls the deviation of error overlaps from their scalar code form.” It neither changes the inequality nor asserts an additional syndrome estimate. The separate exact Gram diagonalization and orthogonal-syndrome construction are unaffected.

Obligations: the original interpretation was tested on an admissible normalized family; the corrected interpretation was matched to the displayed inequality; downstream exact syndrome statements were left intact. No new theorem is introduced.

## 3. Fixed-time heat convergence

**Normalized claim.** Trace-norm convergence of both heat operators and first heat-moment operators, together with a nonzero limiting heat trace, gives convergence of the heat-moment ratios at the specified time.

**Verdict: correct only after a stated restriction.** At this generality the conclusion is explicitly about the heat-moment ratio. A two-sided logarithmic derivative is not supplied by fixed-time assumptions alone.

Source: traditional `parts/02_strengthened.tex`, theorem “Heat trace convergence from trace norm” and its existing one-paragraph proof.

The dependency chain is continuity of the trace in trace norm, convergence of numerator and denominator, and continuity of division at a nonzero denominator. This is exactly the argument already given by the proof. The revised conclusion adds “defined by the heat-moment ratio.”

The distinction matters for unbounded generators at the edge of trace-class times. For example, on a sequence Hilbert space take diagonal eigenvalues `log(n) + 3 log(log(n))` for integers at least three. At time one the heat trace and first heat moment are finite, by the convergent logarithmic series with denominator `n log(n)^3` and `n log(n)^2`. At any smaller positive time the heat trace diverges. A two-sided derivative of a finite heat trace therefore is not automatically defined at that boundary. This is an analytic boundary example, not a numerical experiment.

The manuscript's displayed heat convergence statements and proof are unchanged. No uniform time-window conclusion or new regularity assumption is introduced. No open proofreading obligation remains for the explicitly stated ratio conclusion.

## 4. Which quantity is independent of the input

**Normalized claim.** The unnormalized error-family criterion fixes the code and error family, then chooses a nonnegative scale valid for every supported input operator.

**Verdict: correct only after a stated restriction.** Independence is from the supported input operator, not from the already fixed code.

Source: Lean guide `chapters/channels_recovery.tex`, final paragraph preceding the unnormalized-family excerpt; active `ErrorSpanRecovery.lean`, definition `ErrorFamilyCorrectable` and the subsequent criterion.

The decisive check is quantifier order: the code and errors are parameters before the existential scale, and the supported input is quantified afterward. The guide now says “a nonnegative scale independent of the supported input operator.” The formal predicate is unchanged.

One inherited Lean documentation comment uses the earlier phrase “code-independent.” It is retained with the historical source bytes and recorded here as a comment erratum. It does not alter the formal quantifiers or their proof.

## 5. Other local clarifications

The path-interference formula now explicitly chooses an arbitrary total order on the finite path set. This identifies each unordered cross term once without changing the sum or its real part.

The short-rotation theorem now identifies the size of a partition as its mesh, the largest subinterval length. This is the same quantity used by the existing telescoping estimate.

The Einstein infrared paragraph now states that its volume coefficient includes the sign and normalization displayed separately in Part I's cosmological term. Both action formulas are retained. This distinguishes the two local uses of the same symbol.

The low-mode guide now describes the quadratic upper bound for sine squared, matching the actual use of `Real.sin_sq_le_sq` in the source proof. The earlier description reversed the bound's direction; its displayed inequalities were correct and remain unchanged.

The reading guide defines `Fin n` using natural numbers below `n`, matching the actual type. The previous wording “integers smaller than” failed to state the nonnegative domain.

## 6. Forced mathematical-symbol typo in a diagram

The S3 isotypic-dimension plate used `2\otimes2=4` to label a scalar dimension. This is corrected to `2\cdot2=4` in the visual plate, the integrated traditional copy, and the generator. The nearby vector-space tensor product remains unchanged. This is the only changed mathematical symbol in the current figures.

## Review provenance and preservation

The traditional, visual, and Lean-guide reviewers inspected the source and reported findings before root applied edits. They then reviewed the changed passages against the baseline. These are coordinated reviews, not a claim of statistical independence between models.

Post-edit comparison confirms that all 107 traditional proof environments and all extracted inline/displayed mathematical expressions in the nine traditional parts remain byte-identical. All 25 active Lean modules remain byte-identical. The hypothesis reminders and corrected interpretations are explicitly listed rather than hidden under a claim of complete source-byte preservation.

The mathematical review above uses the supplied definitions, source predicates, elementary boundary examples, and the manuscript's existing arguments. No new external citation, numerical theorem certificate, or kernel execution is asserted.
