# Reviewed essay: editorial and technical report

**Scope:** current essay and its own reproducible package.  
**Checkpoint:** editorial-02, 23 October 2026.

## Result

The reviewed manuscript is 28 pages with 7,611 main-text words, nine chapters, a
conclusion, a preface, three diagrams, source notes, and references. It retains the
approved professional monograph design. The first full essay had 27 pages and 7,056
main-text words. The added length is primarily a constructive mathematical bridge,
not another catalogue of projects or declarations of significance.

## Mathematical and editorial changes

1. **Continuation has its own criterion.** Question sufficiency is distinguished
   from dynamical sufficiency. A represented evolution exists when the represented
   successor is constant on the original representation's fibers. The all-time
   consequence is proved by induction. Restricted initial conditions are explicitly
   distinguished from a claim about every state.
2. **The return example now has a constructive ending.** Eliminating the hidden
   coordinate produces an exact history-dependent recurrence. The induction is
   written in the essay. A nonzero initial hidden state contributes a separate term.
   Agreement after a single step is explained as a consequence of the chosen initial
   state, not evidence of general closure. This gives one continuous example of the
   methodology from conjecture through failure, reconstruction, proof, and reuse.
3. **Hypotheses are not axiom audits.** The checking chapter distinguishes ordinary
   logical premises from global axiom dependencies. A theorem with an impossible
   hypothesis can pass an axiom-policy check while lacking a meaningful application.
4. **Preservation becomes a concrete handoff.** The later discussion explains what
   the record of the operator problem should retain, and what new questions that
   record makes available. This joins mathematical memory to the earlier example.
5. **The proposed evaluation is more discriminating.** A matched workflow comparison,
   changed-task transfer, resource accounting, blinded review where feasible, failed
   attempts, and dependency-record ablation are specified. No results are invented.
6. **Prose and layout were refined.** Repeated qualifications were condensed without
   weakening their scope. Two nearly empty spillover pages were removed. The reader
   remains an essay, not an audit checklist.

The elementary identities are not claimed as new mathematical discoveries. The new
exposition and finite tests do not make a historical-priority claim about them.

## A real inherited defect and its correction

The prior `verify_manifest.py` accepted an empty manifest and printed PASS for zero
files. The behavior was reproduced in an isolated fixture with exit code 0. The exact
receipt is `review_baseline_finding.json`.

The original package had a nonempty 31-file manifest whose entries were checked.
The defect therefore does not erase that actual digest comparison. It does mean the
validator did not establish completeness of an arbitrary submitted inventory.

The replacement requires a nonempty complete inventory and rejects missing, added,
changed, duplicate, and unsafe-path entries. Seventeen actual CLI controls test
acceptance and intended rejection, including an empty manifest under optimized
Python. These controls do not constitute comprehensive security certification,
cryptographic authentication, or mathematical proof.

## Navigation and production corrections

The baseline had anchors pointing to the preceding page or wrong section. The preface,
conclusion, source section, references, and affected subsection boundaries were
reanchored. The final PDF has 27 bookmarks, all matched to their intended destination
page titles, and no invalid internal destination found by the structural audit.

During editing, a guarded patch stopped because an exact LaTeX anchor differed from
the expected spelling. It made no partial source write and was corrected. An initial
inline reproduction runner had a Python syntax error before execution and was
replaced by the delivered `reproduce.py`. A rendering wrapper and an initial clean
rebuild invocation exceeded their command time limits. Neither was counted as a pass.
Separate rendering and a rerun with an adequate synchronous command limit completed.
The final clean-rebuild receipt records the successful run. These production failures
are not mathematical rejection controls.

## Current executed checks

| Check | Result | Meaning |
|---|---:|---|
| Exact-check groups | 40/40 | Finite implementation and arithmetic checks |
| Recorded finite cases | 665 | Suite instances/scenarios, not new theorems |
| Manifest CLI controls | 17/17 | Complete-inventory acceptance and targeted rejection |
| PDF pages | 28 | Built and rendered |
| Bookmark targets | 27 | Matched against intended page titles |
| Final log scan | PASS | No selected box, warning, or missing-character reports |
| Structural page audit | PASS | No reported bounds, unresolved-reference, or link defect |
| Source-only rebuild | PASS | All 28 pages match in text and 72-dpi same-renderer pixels |
| Rebuild records | PASS | Calculation, control, and bookmark records match |

The visual review used 145-dpi page renders and full-size checks of the central new
mathematics and figure pages. The PDF includes embedded typesetting fonts but no
raw font binaries are distributed. The source-only reproduction uses the same
installed Python/TeX environment. It is not a fresh OS image or an independent checker.
Byte-for-byte PDF identity is not asserted.

## Evidence boundaries

The factorization, memory, tower, stability, and symbolic identities have written
arguments with explicit settings. Finite tests do not replace universal deductions.
The source register identifies the companion project editions and publicly consulted
documentation. The companion Lean project claims remain source-reported history.
There was no fresh Lean compilation, whole-corpus replay, independent external review,
or empirical comparison of research methods in this handoff.

The manifest validates delivered bytes relative to its inventory. If both payload and
manifest are maliciously replaced, this mechanism does not authenticate either. The
frozen delivery is verified separately after packaging so that no report inside the
manifest attempts to hash itself or predict its own final archive bytes.
