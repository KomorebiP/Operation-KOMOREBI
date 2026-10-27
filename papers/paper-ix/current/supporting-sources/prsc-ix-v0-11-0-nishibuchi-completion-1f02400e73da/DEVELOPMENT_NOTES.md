# Development and verification notes

## Third block: weighted dyadic reconstruction (v0.3.0)

The input is the exact v0.2.0 archive recorded in `provenance/third_source.json`. All 13 original Lean modules, the corrected source PDF, and both earlier mathematical supplements were preserved. The portable archive was restored locally. Seven part hashes and the assembled hash matched; the unchanged 13-module second-block verifier also passed a new clean baseline run before this development.

Four new modules complete the recorded scopes of 5.1–5.4. The source is strengthened from integrality to unit status. The manuscript's ordinary beta coefficients and even row indexing are maintained. Explicit normalization bridges connect rational coefficients to actual `ℤ_[2]` elements. No mathematical theorem is assumed as a custom axiom, no admitted proof is permitted, and the error divisibility is not formulated over a field.

Of the **15 captured development checks, eight failed and seven passed**. Every checked source snapshot and compiler diagnostic is retained in `verification/third_development/`. Problems included a subring membership goal needing explicit unfolding, natural/rational valuation casts, finite-sum indexing, formal-series homomorphism normal forms, inverse-coefficient recurrence rewriting, and the cast of the normalized rational error into the completed field. The final proofs repair these engineering issues. The statements were not weakened to assume the reconstruction or congruence conclusion.

A fresh 17-module cumulative build passed with warnings treated as errors, 219 theorem reports, 53 definition reports, all nine dependency pins, and eight deliberately invalid proof controls. The controls include three new errors: omitting the scale `2^(2*m)`, confusing ordinary with exponential beta coefficients, and asserting an additional false precision bound. A failed draft or rejected negative proof is never treated as a partial proof of its intended statement.

The new exact-rational Python mirror uses independent factorial-series inversion, not project Lean extraction. It checks 49 coefficient-integrality/source-unit cases, 97 complete formal-series coefficients, 49 Euler rows and 2,548 truncation depths through degree 96. Of these errors, 1,176 are nonzero and 1,372 are exactly zero. The finite valuation helper rejects zero; exact zero is recorded explicitly rather than assigned finite valuation zero. Forty-eight Bernoulli-formula comparisons are finite checks only. Both older independent Python mirrors were rerun into separately named third-block reports without replacing their historical evidence.

The earlier infrastructure tests were adapted to the larger inventory and their original v0.2.0 copies saved under `provenance/second_block/`. Sixteen new tests bring the total to 49. The old metadata and verifier source are also retained. The five original negative controls remain, with three added. The release's raw evidence distinguishes local Lean proof checking, mirror tests, source preservation and dependency pin checks.

The original historical numerical suite was not rerun. The unnumbered Bernoulli identity, analytic convergence, general 7.5 finite-difference theorem, three classical inputs and two conjectures are not promoted to newly proved claims. Mathlib's compiled cache remains a stated dependency. No new SVD, physics, prime-gap or continuum claim is made.

---

## Earlier preserved notes

# Second-block development and trust boundaries

Author: Komorebi P.

## Actual run sequence

1. The first-block sources were recovered unchanged and checked in a clean directory. This eight-module baseline passed and is retained under `verification/baseline_recheck`.
2. Fifteen captured new-module development invocations produced eight failed and seven successful checks. Failed draft sources (`.lean.txt`), commands, hashes and compiler output remain under `verification/second_development`. The failures involved unavailable names, expression normalization, incomplete proof goals and warnings. They are not proof successes.
3. A preliminary clean cumulative second-block run passed with 162 theorem declarations. Its exact inventory and coverage snapshots are retained under `verification/second_final`. It preceded the explicit row-action theorem connecting the matrix entries to Euler reconstruction.
4. The final source includes that row-action theorem. A separate clean run under `verification/second_release` accepted all 13 modules, 163 theorem declarations, 37 definitions, nine dependency pins and five expected-rejection controls. Only this final 163-theorem run is the authoritative second-block result.
5. All 33 Python unit tests passed after the final inventory update. Independent exact regressions cover 234 reconstruction rows and 2340 truncation depths, alongside both generating-function identities and signed-zigzag coefficients. These are finite mirrors, not executions extracted from Lean.

An initial request for an interactive container session was unsupported. Noninteractive runtime assembly and extraction succeeded. All seven part hashes and the combined archive hash matched, as recorded in `provenance/second_runtime_recovery.log`.

The first two PDF drafts had an overfull module-name paragraph. It was repaired before the final PDF build. The final six-page PDF was rendered and every page visually inspected. Formatting failures are not mathematical proof failures.

## Preserved and changed material

All eight upstream active proof sources, the original corrected manuscript PDF and the first-block supplement PDF/TeX are preserved byte for byte. Their checksums are recorded. Original metadata, README, verifier, launcher and unit-test file are archived in `provenance/first_block`. The active verifier and tests have been extended for the new modules, coverage and controls. Earlier first-block failures are retained as historical evidence and are not new second-block failures.

## Limits

Formal series do not certify analytic convergence. Coefficient-defined zigzag numbers are connected to the actual formal secant-plus-tangent series, not to a new enumerative interpretation. The new integer congruence does not establish the later global finite-difference theorem. Mathlib's cache was reused, not rebuilt. Earlier papers, native Windows, and the original historical numerical package were not tested. No formal proof of prose-to-Lean semantic equivalence is claimed.


## Fourth block

Ten targeted development checks were recorded before the cumulative rebuild, including six unsuccessful drafts. Failures were ordinary elaboration, finite-sum function normalization, optional-value coercion, a missing decidable equality, unused simplification arguments, one incorrectly inferred sample-index type, and a tactic-layout error. All are retained under `verification/fourth_development/`. None is counted as a successful proof. The final four sources compile with warnings as errors, with no admitted proof or added axiom.

Runtime recovery first attempted a container streaming command, which the environment did not support. A noninteractive assembly and extraction succeeded and verified every part hash and the combined archive hash. This tool-interface failure did not alter Lean trust settings.

The standard Mathlib forward-difference results are reused and explicitly acknowledged. This block does not claim independent new proofs of all imported facts. We made the manuscript's finite-sample scope and valuation-at-zero convention explicit rather than silently choosing the easier interpretation.

The new exact-regression CLI was aligned with the earlier mirrors before packaging: it prints by default and only writes a report with an explicit `--output` argument. Thus the normal launcher does not overwrite its frozen regression evidence. This changes no Lean proof or mathematical regression function.


## Fifth block (v0.5.0)

The unchanged fourth-block sources first passed a complete baseline build.
The seven new modules then required 18 recorded development checks: 7 passed and
11 failed before the later clean release build. Errors included coercions, changed
lemma interfaces, finite mod-four case proofs and excessive simplification of
recursive example definitions. The last example proofs instead use established
recurrence equations. No theorem is accepted on the basis of a failed run.

Development-check times are observation elapsed times, not isolated compiler
benchmarks. All source snapshots and compiler diagnostics are retained separately
from the active formalization directory. The complete successful fifth-block build
started with an empty output directory and checked 333 theorems and 77 definitions.

A first document build had seven pages because a final paragraph spilled to an
extra page. The build gate rejected that layout. The prose was compacted and the
subsequent six-page build rendered for review. The initial failure is retained in
verification/fifth_pdf_initial_failure.log.

The first container.exec invocation failed with ClientError, so file operations
and subprocesses used the working Python runtime. Runtime archive recovery
completed with all seven part checks and the combined SHA-256 match. The system
Python interpreter was used for subsequent verification processes to avoid
unrelated virtual-environment startup hooks.

The independent finite regression results are replayed after fresh extraction,
excluding only elapsed time. They are not Lean extraction, nor evidence that
the four still-pending manuscript results have been proved.


## Sixth block: companion jumps and Fibonacci packets

The next block adds three proof modules, 49 theorem declarations and seven definitions. It closes manuscript items 9.1 and 9.2 only. Both 7.5 and 8.5 remain pending. The exact corrected input manuscript is unchanged.

Four Lean development checks failed: check_001 (associativity and recursive simplification), check_003 and check_004 (Fibonacci successor normalization, polynomial coefficient simplification, and unused tactics), and check_006 (the tested coordinate of a true counterexample was equal even though the other coordinate differed). Each was repaired without weakening the intended result. Successful follow-up checks and their exact source snapshots are retained.

The first infrastructure-test run failed two stale baseline count assertions. Their expected current totals were corrected, and all 131 tests passed. Earlier block-specific tests now read their archived block snapshots. No existing mathematical regression was removed.

The first supplement build produced seven pages because a short evidence section spilled to an otherwise nearly empty page. That repeated section was removed from page one; detailed evidence remains on page six. The accepted six-page PDF compiled without warnings and all six rendered pages were visually reviewed. The original failing source and log are retained.

The matrix recurrence uses the actual characteristic polynomial and the pinned Mathlib Cayley-Hamilton proof. Fibonacci is actual Nat.fib and Lucas is independently recursively defined. The two-by-two trace identity follows from C^2=C+I, not from an assumed spectral formula. No additional axiom, admitted proof or native proof-evaluation shortcut is used.


## Seventh block: direct period, global boundary preserved

The baseline 31-module project was independently replayed before the new development and passed its build and axiom audit. The new proof takes a shorter finite-field route to the standard-window period, bypassing rather than assuming Theorem 7.5. The retrieved 18-page global supporting document is a prose proof, not an imported Lean axiom or completed formalization. It is preserved under provenance/global_argument_source.

20 recorded development checks include 11 failed drafts and 9 successes. Errors concerned finite-sum lemma names, coercions, simplification, characteristic-p numeral normalization, omitted typeclass instances, and proof composition. Sources and compiler logs are retained in seventh_development. All active modules later passed the clean cumulative build. No admitted proof, custom axiom or native proof-evaluation shortcut was introduced.

The first full unit-test invocation failed two stale current-release assertions (coverage totals and upstream module count). Both expectations were updated to the observed new register; the failed log is retained. Historic sixth-block census assertions now read their frozen release snapshot. The 162 tests then passed; no mathematical regression test was deleted.

The first runtime/container calls returned ClientError until an explicit /tmp working directory was used. One portable archive chunk had an incomplete mounted copy and was recovered through Files. All seven archive-part checks and the combined hash passed during successful assembly/extraction. An interactive execution request was unsupported; noninteractive checks worked. These were environment/tool failures, not Lean proof failures.

The six-page PDF compiled without layout warnings and all six pages were rendered and inspected. Review corrected a historical reference (the reduced inverse was constructed in the fifth block) and a summation-index label. All original manuscript and supplement assets remain byte-identical.

The full global estimate, particularly the actual flat integral lift and singular-residue control, remains pending. The new all-positive-order standard-window estimate contains only one power of p. The Dwork-flatness and factorial-loss lemmas are explicitly conditional, with no claim that their global antecedents have been proved.


## Eighth block: all-order closure and the full higher-power standard window

This continuation began from the saved v0.7.0 archive. The previous unverified v0.8 draft was not recovered as a usable saved artifact; no claim is made that its failed proof body was repaired byte for byte. The preserved baseline passed all 38 modules and its axiom audit before the new development.

Eighteen new proof-development checks were recorded: nine failed drafts and nine successes. Failures involved coefficient coercions, typeclass inference, finite-sum endpoint rewrites, power-series inversion interfaces, commutator algebra, and exact example simplification. Every one of the nine active new modules then passed its individual compilation. Sources and diagnostics are in verification/eighth_development. A nineteenth record is a deliberately invalid negative-control probe, marked separately and not counted as a failed mathematical development attempt.

The first cumulative eighth-block run compiled all 47 modules and passed all 633 axiom audits but did NOT pass the release gate: the newly added singular-pivot negative control failed in a rewrite prelude, rather than reaching the intended false goal. The verifier correctly refused to count this as successful negative testing. Its failed report is retained in verification/eighth_final, and the verifier script used for that attempt is preserved as provenance/eighth_verifier_before_negative_fix.py. The control was rewritten using the actual PadicInt.norm_p identity so that it reaches an unsolved False goal. Rejection acceptance criteria were not weakened; the corrected script was rerun from an empty build directory in verification/eighth_final_corrected. The 47 proof sources were not changed by this infrastructure repair.

The current census tests were updated to 47 modules, 526 theorems, 107 definitions, and 38 unchanged upstream proof files. The historical seventh-block census tests read the frozen seventh-block snapshot, preserving their historical assertions. The new eighth-block test suite adds 27 checks, for 189 total. No earlier mathematical regression test was deleted. A deterministic standard-library Fraction mirror tests the explicit rational coefficients, reciprocal defects, normalized product formula, commutator and step identities; it is not Lean extraction or a substitute for the universal proofs.

The supplement has six pages. Its final LaTeX build passed without layout warnings and all six pages were rendered and visually inspected. The manuscript-proved coverage count remains 23/24; the new unconditional higher-power result is a subcase of the remaining item 7.5, not a replacement for the original all-residue claim. The nonsingular Euler-pivot argument is explicitly restricted to p not dividing the pivot parameter.

The kit was recovered and its seven archive parts plus assembled SHA-256 checked. The Lean toolchain is 4.34.0-rc2 and Mathlib's pinned compiled cache is reused rather than reconstructed. Final accepted and failed run statuses, the exact archive checks, and the independent fresh-extraction replay are recorded separately in the delivered evidence.


## v0.9.0: actual singular Amice estimate

The previous cyclic-ring research files are preserved byte-identically and now enter the cumulative build and transitive-axiom audit. New source modules connect the integral estimate to actual logarithmic sections and original ratios, construct the normalized singular denominator, and establish weighted inverse/differential closure. All attempted source snapshots and diagnostics are in verification/ninth_development. Probe files and failed drafts are inactive.

The initial portable extraction was interrupted by an outer tool timeout; a retry completed with all seven part hashes and the combined hash verified. The first PDF layout had two overfull lines; both were repaired before final rendering. Four old cumulative-count assertions failed against the extended inventory. Their original files and failed run are preserved; historic checks were redirected to the frozen eighth-block census and current checks updated to the new actual census. No mathematical Lean source or proof target was weakened to handle those infrastructure failures.

The full global finite-difference theorem is not promoted: only the weighted singular-ratio estimate is new.


## v0.10.0: completion of the original all-residue statement

This continuation recovers both the live-checkpoint archive and the actual v0.9.0 singular-Amice release. The latter's 57 active proof files are byte-identical and are genuinely rebuilt in this run; they are not discarded because a prior conversation message reverted to the older v0.8 status.

The repaired ThetaWeighted source now compiles. The subsequent transfer, original-ratio support, Euler inverse, coefficientwise Picard propagation, actual Riccati identity, all-ratio induction and coefficient assembly discharge the remaining hypotheses for Theorem 7.5. The capstone has only arithmetic parameter hypotheses and retains the correct factorial loss.

There are 61 captured local development checks in this continuation, with 49 exit-zero records and twelve failed drafts before repair. All failed records belong to new proof-development modules, not failed negative controls. Their snapshots and diagnostics are retained. Failures concerned simplification, missing or inappropriate lemma interfaces, coercions, operator identities and elaboration. No theorem conclusion was weakened to accept them. A first portable extraction hit the outer tool timeout; resumed extraction completed. An interactive container session was unsupported; the actual checks use noninteractive subprocesses.

Historic tests that assert an older pending status now read their exact preserved old coverage/verifier snapshot. Current tests require all three unconditional final targets and explicitly reject promotion using only the conditional Dwork criterion. Current inventory assertions match 70 modules, 753 theorems and 148 definitions. The 26 new tests bring the unit total to 235. No earlier mathematical test is removed.

The first supplement draft had seven pages with a short final-page spill. It was edited to six pages, rebuilt without layout warnings, rendered and visually reviewed. This was a document layout issue, not a mathematical change. The earlier overbroad normalized claim remains refuted by the retained counterexample. The two native conjectures remain unproved.
