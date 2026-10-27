# Komorebi Large Signal Model — Foundations 0.9.0

**Scope-frozen audit candidate. 87 written propositions. Production PR-LASM remains 2.3.0.**

## Read in this order

Start with `theory/READING_GUIDE.pdf` (9 pages). It connects the model's representation, transfer, closure, learning, probability and evidence requirements without adding another theorem block. The cumulative `theory/FOUNDATIONS.pdf` (108 pages) contains the complete statements and proofs. Use `theory/PROOF_REGISTER.pdf` (21 pages) or `PROOF_REGISTER.json` for assumptions, principal dependencies, source locations and restricted code links.

`ASSUMPTIONS_AND_DEPENDENCIES.md` and `SCENARIO_REGISTER.json` separate seven sectors. In particular, statistical coverage from the observable five-node example is not assigned to the unrelated deterministic repaired-operator example. `RELEASE_AUDIT.md` records the audit, corrections, tests and limitations.

## What changed

No new proposition was added. Proposition 72 now explicitly requires at least one spatial coordinate. The remaining 86 statement-and-proof passages are byte-identical to 0.8.0. All original cumulative prose is preserved under `provenance/0.8.0/FOUNDATIONS.md`, with a source diff and lineage hash.

The resumed replay now checks source and fixed-input identity, script ordering, the successful prefix, and the execution environment. A local temporary-folder regression reproduces the old stale-prefix gap and checks the repair. Zero-denominator rational strings now fail at the input-validation boundary rather than through division by zero; they were not previously accepted.

The active archive is flat. It carries the full current source, reference programs, data, certificates, figure assets and evidence. It does not recursively duplicate every predecessor ZIP. Historical companion PDFs are labeled by their actual version under `companions/`.

## Run from a fresh extraction

With the tested dependencies already installed:

```text
python run_reference_checks.py --verify-hashes
```

The runner executes eight inherited suites, sixteen inherited example/generator programs, and three new audit/checker programs. The eight suites contain 756 finite records. The new audit suite contains 29 separate records. The source and register verifiers are structural audits, not additional mathematical theorem tests.

For a bounded execution environment, use the same session name in these consecutive batches:

```text
python run_reference_checks.py --verify-hashes --batch-start 0 --batch-count 6 --session review
python run_reference_checks.py --batch-start 6 --batch-count 8 --session review
python run_reference_checks.py --batch-start 14 --batch-count 4 --session review
python run_reference_checks.py --batch-start 18 --batch-count 3 --session review
python run_reference_checks.py --batch-start 21 --batch-count 6 --session review
```

Only all 27 successful records constitute a complete PASS. Changing source, fixed inputs or the recorded execution environment between batches requires a new session. Checkpoint files are local reproducibility records, not tamper-resistant attestations or signatures.

Reports and some example outputs are regenerated during replay. The supplied checksum inventory therefore applies before the first mutating run. Use another fresh extraction to repeat the distribution integrity check. Python bytecode caches are ignored by the inventory verifier.

## Mathematical and implementation boundaries

Exact witness replay establishes identities and nonnegativity in the submitted model. It does not prove unknown physical assumptions, authenticate observations, discover an adequate dictionary, or turn a conditional confidence theorem into an empirical coverage estimate from one path.

The register's 105 principal internal edges form an acyclic map; this is not a complete formal proof graph. Its 40 code links explicitly distinguish restricted algorithms, numerical proposals, finite calculations and supplied certificate checkers. The original 756 records are finite checks, not 756 general proofs. No Lean kernel or independent external referee was used in this release.

No new production package, benchmark score, pretrained checkpoint, broad agent implementation, GPU run, remote CI run or repository publication is included. The remaining unrestricted discovery questions are research directions, not unstated conclusions of the finite scope.

## Rebuild the documents

The Python reference calculation environment is recorded in `requirements-tested.txt`. Building PDFs also requires installed Pandoc and pdfLaTeX; structural PDF checks require PyMuPDF and `pdffonts`.

```text
python theory/build_register.py
python checks/verify_proof_register.py
python theory/build_pdf.py all
python checks/audit_documents.py
```

Rebuilding changes generated artifacts and does not update a prior release's immutable checksum inventory. No network access is needed for replay or document generation when dependencies are already installed. Windows execution was not tested here; `Run_Checks.ps1` is a supplied wrapper.

## Attribution and publication

The cumulative manuscript retains the primary-source lineage for classical ingredients. Proposition counts are not novelty counts. `LICENSE_STATUS.md` preserves the existing licensing boundary; no new license grant or public publication is implied. No standalone font files or third-party book/article PDFs are redistributed.
