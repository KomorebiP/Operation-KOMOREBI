# Foundations 0.9.0 — scope, assumptions and reproducibility audit

**Komorebi Large Signal Model · Komorebi P. · 9 October 2026**

## Release result

This is a scope-frozen theory release candidate, not a new architecture block. It contains 87 numbered statements with written proofs, a 108-page cumulative volume, a nine-page unified reading guide and a 21-page proof/assumption/evidence register. General proof-kernel verification and independent external review were not performed. Production PR-LASM remains 2.3.0.

The manuscript's intermediate checkpoint passages have been replaced by current connections between sectors. Repeated and unnecessary forced page breaks were removed outside proposition/proof spans. Stable section and proposition numbers remain. The principal mathematical content is not replaced by a short summary; the full cumulative statements and proofs are retained.

## One mathematical boundary clarification

Proposition 72 now explicitly assumes at least one spatial coordinate, d >= 1. In a mass-only space, the mass-preserving constraint forces a perturbation to be zero, so a nonzero perturbation of any prescribed positive size cannot exist. The earlier text did not explicitly state this dimension restriction. Its worked examples have two spatial coordinates and are unaffected.

Exact source comparison verifies all 87 proposition numbers, 86 unchanged statement/proof spans, and only the stated insertion in P72. The preserved 0.8.0 cumulative source has SHA-256 `3072959c4c7bcba82be8591e0c431a1043ff66e01a359fa439c6e523705866b1`. The source diff includes editorial changes outside those spans. Preservation is not proof verification.

## Replay integrity correction

The old batch runner accepted a stored successful prefix by count and success flags, without binding continuation to unchanged source files, fixed inputs, script ordering or runtime environment. The audit reproduces this behavior with two harmless scripts in a temporary folder: change the first script after its successful batch and continue the second. The unchanged old runner reports success while retaining a stale first-script hash.

The new runner rejects changed source or fixed inputs, changed inventory/order, changed environment, wrong version/session, an inconsistent prefix and mismatched prior source hashes. It also checks the snapshot during execution. These controls improve local reproducibility. They are not cryptographic attestations against a party able to forge the checkpoint and source inventory. Nothing in this finding establishes that the historical 0.8.0 results were incorrect; the inherited examples were rerun successfully.

The snapshot includes active Python code, fixed example JSON inputs, dependency declarations, the manuscript/register/lineage records and the preserved source needed by the audit. Mutable generated reports are not treated as immutable inputs.

## Input-validation correction

The robust certificate parser previously raised ZeroDivisionError for rational strings with zero denominator. Those strings were rejected, not accepted as valid witnesses. It now rejects them with ValueError at the validation boundary. Existing certificates remain valid. Regression checks distinguish this error normalization from a mathematical soundness correction.

## Dependency and source-to-code map

The register covers every one of the 87 numbered results. Its 105 principal internal dependency edges are acyclic. P9's use of later-presented P12 is recorded rather than misclassified as a cycle. Standard background lemmas and classical antecedents remain in the manuscript; the JSON is a curated principal map, not an extracted formal proof term.

Forty entries link a named function/class, file hash and line range to a restricted implementation sector. The limitations are part of each link: bounded interval search is not general cone enumeration; a numerical geometry proposal is not a certificate; a scalar confidence routine is not a general hidden-state learner. All entries separately identify block-level finite suites without calling those suites formal theorem verifiers.

Seven scenario records distinguish supplied information, learned quantities, witnesses and unsupported conclusions. In particular, the dependent-data confidence rectangle of the fixed observable family is not transferred to the earlier deterministic repair. Reference measure, policy, domain and initial-state compatibility remain prerequisites for comparing bounds.

## Fresh local execution

The original eight suites and sixteen example/generator programs were rerun. They reproduce 756 finite check records. The new runner then completed all 27 programs: those 24 plus the audit regressions, source-lineage check and proof-register check. Actual commands, source hashes, exit codes and durations are retained in `verification/reference_replay.json` and its session checkpoint.

The new audit suite contains 29 records covering the P72 dimension boundary, exact rational parsing, accepted unchanged continuation, rejected stale/inconsistent continuation and reproduction of the legacy behavior. These 29 records are reported separately from the 756 inherited records. Source identity and register validation are separate structural checks, not additional general mathematical proofs.

The inherited 756 records comprise 703 exact rational/symbolic records including expected rejections, 41 numerical records, six seeded sampling records and six seeded-path diagnostics. Counts are not estimates of coverage, independent theorem proofs or historical novelty.

Seven inherited certificate files regenerated byte-identically to 0.8.0. Their independent replay is part of the examples. The finite positive-lift certificate is also retained under verification. No new mathematical certificate geometry or numerical accuracy claim is introduced by this audit.

## Visual and build inspection

All three current PDFs compile with zero overfull boxes, zero underfull boxes, zero undefined-reference and duplicate-destination messages, embedded fonts, no detected replacement glyphs and no detected text outside page boundaries. All pages were rendered for contact-sheet review, with additional full-size review of the P72 correction, the reading-guide comparison table and selected register entries. Structural checks and visual inspection are separate activities.

The first register layout stranded an evidence paragraph on an otherwise nearly blank page. Whole-entry layout corrected it. The cumulative contents initially spilled two lines onto a third page; adjusted contents spacing removed that overflow. Legacy forced breaks also left sparse transition pages; their removal did not alter any proposition/proof span. Documents were rebuilt and rerendered after these changes. No mathematical assertion was removed to make a check pass.

## Packaging and execution limits

The package is flattened rather than nesting the 40 MB predecessor ZIP again. It contains the full current source and reference laboratory, preserved predecessor prose and audit records, explicitly versioned historical companions, figures and certificates. The separately delivered 0.8.0 ZIP is identified by its hash. It is not required for current replay.

Hash verification covers every declared file and the complete pre-replay inventory. A final independent working-directory extraction and replay are reported in the separate extraction-verification artifact, avoiding a self-referential archive hash. Reports regenerate during execution; integrity checking must precede those writes.

Execution used Linux and Python 3.13.5 with the locally recorded dependency versions. The Windows wrapper was not executed. No sensor dataset, GPU, remote CI, production checkpoint, public publication or license change was involved. A fixed observable dictionary, exact accessible state, model class and observation protocol remain supplied assumptions of the statistical sector.

## Candidate status

The declared finite scope has a documented proof/assumption structure and reproduced reference evidence. This is not certification of every future extension or independent formal validation of all mathematics. General unknown dictionary discovery, unrestricted hidden-state learning and empirical sensor coverage remain research tasks outside the frozen release. They are not silently promoted to completed results or made unstated prerequisites for the finite theorems.
