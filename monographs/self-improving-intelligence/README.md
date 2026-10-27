# Self-Improving Intelligence
## Representation, Discovery, and Recursive Revision
**Komorebi P. · Operation Komorebi · First consolidated edition v1.0.0 · 8 October 2026**

The manuscript follows one finite chain: compile a diagnostic repair, improve its compiler, synthesize an internal compiler decision, then acquire a checked representation that reduces later rule-acquisition work. The final integration tracks whether the resulting certificates remain applicable after revision and separates semantic preservation from actual resource savings.

This is a theoretical publication package with executable mathematical reference constructions. It is not a deployed autonomous agent, a neural checkpoint, a claim of general intelligence, or a demonstration of indefinite recursive acceleration. Historical internal agent experiments are not presented as evidence of the integrated architecture.

## Read

- `Self_Improving_Intelligence_v1.0.0.pdf`: canonical 60-page manuscript, eight parts.
- `Self_Improving_Intelligence_v1.0.0.tex`: editable canonical source.
- `STATEMENT_INDEX.md` and `ASSUMPTION_REVIEW.md`: all 30 statement/proof pairs and their assumptions.
- `CLAIMS.md`: distinctions among conditional theorems, executed finite constructions, and open research.
- `RESOURCE_LEDGER.md`: preparation, inference, storage, checking, and price boundaries.
- `CERTIFICATE_LIFECYCLE.md`: dependency declarations, invalidation, rechecking, and negative controls.
- `SOURCE_MAP.md`: itemized accessible-depth reference review.
- `REVIEW_NOTES.md`: actual execution, proofreading, rendering, rebuilding, and limits.

## Verify the frozen snapshot first

From the package root:

```bash
python code/verify_release.py
```

This checks the included checksum inventory and the pinned execution inputs and outputs. It is an integrity check relative to that inventory, not origin authentication or mathematical truth. Rerunning programs replaces timed receipts and can consequently change the frozen snapshot. Preserve an untouched copy.

## Reproduce the mathematical constructions

Only the Python standard library is needed for the reference algorithms and exact suites. Integers, finite sets, and `fractions.Fraction` are used for correctness decisions.

```bash
python code/run_validation.py
python code/check_computation_record.py
```

The wrapper runs five suites, all demonstrations, predecessor preservation, and the source audit. It enforces a 90-second wall limit for the unchanged original suite and 45 seconds for each remaining command. A timeout is an incomplete execution, not an infeasibility or theorem result. Slower hardware can require explicitly revised limits.

The new lifecycle construction can be run separately:

```bash
python code/check_revision_models.py
python code/demo_revision.py
```

`revision_contract.py` supplies the finite dependency and resource framework. `demo_revision.py` applies it to the actual learned equation library, grammar quotient, synthesized capacity rule, repair-weight witness, and diagnostic controller. The dependency graph and primitive checkers are supplied, not learned.

## Rebuild the manuscript

A standard LaTeX installation with the packages listed in the source and `latexmk` is needed. No font files are distributed. The already supplied vector figures are sufficient.

```bash
bash build.sh
python code/audit_source.py
python code/preflight_pdf.py --renders /absolute/path/outside/package/renders
```

The preflight needs PyMuPDF and the `pdffonts` utility. It does not replace visual inspection. Matplotlib is required only to regenerate the eleven analytical figures:

```bash
python code/make_figures.py
python code/make_discovery_figures.py
python code/make_synthesis_figures.py
python code/make_meta_figures.py
```

On Windows, `latexmk` and the Python commands can be invoked from the package root. The Bash script was executed in the recorded Linux environment; Windows execution is not certified.

## Scope and reproducibility

The first edition contains 30 theorem/proposition statements with prose proofs, two definitions, eighteen formal counterexamples, eleven analytical figures, and twenty-three references. The exact suites contain 72 groups and 336,867 assertions. These counts are document and finite-program inventories, not independent proofs, scientific replications, or new-discovery counts.

A fresh source copy is rebuilt and compared page by page in `validation/fresh_rebuild.json`. `validation/execution_manifest.json` records actual commands, runtime limits, software versions, and hashes before and after the run. The inherited legacy-v1 computation record and its project-authored checker are not an independently authenticated auditing service. No Lean build, external attestation, Git revision, OS sandbox, independent memory cap, PDF/A or tagged-accessibility certificate is claimed.

Earlier material is retained under `lineage/`. Original conversation deliverables remain unchanged. The package includes no private conversation transcript, external-account integration, third-party full papers, or standalone font files. No new third-party license or journal acceptance is asserted by this edition.
