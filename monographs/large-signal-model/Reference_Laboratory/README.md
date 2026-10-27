# Komorebi Large Signal Model — Foundations 1.0.0

**Frozen finite theory release. 87 propositions with written proofs. Production PR-LASM remains 2.3.0.**

## Start here

Read `theory/READING_GUIDE.pdf` for the connected argument and `theory/VISUAL_ATLAS.pdf` for thirteen preserved Python-generated illustrations. The full `theory/FOUNDATIONS.pdf` retains every statement, proof, definition and reference from the mathematical body of 0.9.0. `theory/PROOF_REGISTER.pdf` and `PROOF_REGISTER.json` map the 87 results to assumptions, principal dependencies and restricted reference implementations.

`ASSUMPTIONS_AND_DEPENDENCIES.md` and `SCENARIO_REGISTER.json` distinguish seven sectors. A shared notation is not a shared statistical guarantee. `RELEASE_CONTRACT.json` fixes the scope and identities. `RELEASE_AUDIT.md` records execution and limits.

## What version 1.0 freezes

Exact realization, packet transfer, predictive closure, memory, finite observable identification, controlled probability instruments, continuous observation semantics, finite domain witnesses, approximation and repair, and a restricted dependent-data learning sector. No new numbered theorem or production integration is added. The meaning of a certificate, the comparison norm, the observation measure, the policy and the horizon remain explicit assumptions.

All 87 statement-and-proof passages are unchanged from 0.9.0. The entire mathematical body from Section 1 onward is unchanged, including upstream definitions and references. The earlier P72 dimension correction is retained. Nineteen mathematics/checker modules, five fixed example-input files and seven stored certificate files retain their predecessor identities. Final replay verifies the certificates again after generation.

The visual atlas collects existing figures. It does not add an experiment or treat a finite curve as a general proof.

## Reference replay

Use a fresh extraction and the tested Python 3.13.5 environment. With NumPy and SymPy already installed:

```text
python run_reference_checks.py --verify-hashes
```

To install the tested core dependencies in a separate environment, dependency installation may require network access:

```text
python -m pip install -r requirements-reference.txt
```

The replay itself does not request the network. It executes 29 programs: eight mathematical suites, sixteen examples/generators, the inherited audit suite, two structural source/register checks, the final release regression suite, and the immediate-predecessor freeze check. The mathematical suites retain 756 records. The audit suites contain 29 inherited and 28 new release-engineering records, counted separately.

For bounded execution, use one session through these successive batches:

```text
python run_reference_checks.py --verify-hashes --batch-start 0 --batch-count 6 --session review
python run_reference_checks.py --batch-start 6 --batch-count 8 --session review
python run_reference_checks.py --batch-start 14 --batch-count 4 --session review
python run_reference_checks.py --batch-start 18 --batch-count 6 --session review
python run_reference_checks.py --batch-start 24 --batch-count 5 --session review
```

Only all 29 successful records constitute a complete PASS. Changing source, fixed inputs or the recorded environment requires a new session. The checkpoints are local reproducibility records, not tamper-resistant attestations. Reports and some certificates regenerate during replay. Verify distribution hashes first; use a fresh extraction for another pristine inventory check.

## Rebuild the documents

Optional dependencies are separate from the reference calculation dependencies:

```text
python -m pip install -r requirements-rebuild.txt
python theory/build_register.py
python theory/build_pdf.py all
python checks/audit_documents.py
```

Install Pandoc, pdfLaTeX and Poppler (`pdffonts`) separately. The optional rebuild list includes SciPy, used by an inherited figure generator, and PyMuPDF, used for document audits. Existing figure assets are included, so rebuilding the four PDFs does not require regenerating the figures.

The PDF audit now uses explicit exceptions rather than assertions for its quality gates, so those gates remain active under optimized Python. Windows and PowerShell execution have not been tested in this environment. `Run_Checks.ps1` is a supplied wrapper, not a claim of a Windows run.

## Interpretation and publication boundary

A written proof is not a proof-kernel result. A successful finite check is not a general theorem verifier. A probability-valid model need not be accurate. A statistical confidence statement is conditional on the supplied model and observation assumptions, not empirically validated by one seeded path. No new Lean verification or independent external review is claimed.

General unknown-dictionary discovery, unrestricted hidden-state learning and sensor uncertainty remain research outside this frozen finite scope. No pretrained checkpoint, new production version, public repository publication or license change is included. See `LICENSE_STATUS.md` and `CITATION.md`. The archive is a local theory release, not a claim of open-source licensing or public availability elsewhere.
