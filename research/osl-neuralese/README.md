# OSL and Neuralese — Consolidated Research Edition 1.0

**Komorebi P. · 6 October 2026 (local edition date)**  
Fresh checks ran on 7 October 2026 UTC. This is a manuscript-and-evidence freeze, not an OSL-Core runtime version bump or a universal learned-language result.

## Start here

- [OSL manuscript](OSL/manuscript/OSL_Final_Research_Edition.pdf) — 18 pages: operator semantics, provenance, admission, scoped independent checking, finite discovery, and semantic checkpoints.
- [Neuralese manuscript](Neuralese/manuscript/Neuralese_Final_Research_Edition.pdf) — 21 pages: learned latent operators, continuation semantics, quotient stability, observability, and the complete selected positive/negative evidence map.
- [Visual and verification guide](guide/OSL_Neuralese_Visual_Verification_Guide.pdf) — 8 pages.
- [Validation record](VALIDATION.md) and [source ledger](SOURCE_LEDGER.csv).
- [Original OSL v0.5 monograph](OSL/historical_monograph/operator_symbolic_ai_language_v0.5.pdf) — the preserved 88-page historical development, not rewritten as a new runtime specification.

The two new manuscripts are individually readable. LaTeX sources and required style/reference files are beside each PDF. The broad earlier OSL development remains intact, while the new edition supplies version reconciliation, current evidence, and a narrow executable interface.

## What is finalized

**OSL.** The current executable core remains Core 0.5, paired with its own grammar, examples, receipts, independent semantic components, and tests. Core 0.3/0.4, the Discovery Bridge, and experimental neural-language branches remain separately identifiable. No unrecovered Core 0.6 changes have been fabricated or promoted.

**Neuralese.** Twelve direct research branches plus the recurrent-depth laboratory are consolidated as a source-bound research account. Training-generated successes, numerical/semantic failures, invalid assay prerequisites, and stopped or unspent experiments retain distinct statuses. This collection does not claim to recover all related SRIC, RRCT, ARC, PRISM, or later unindexed vault work.

**New finite interface.** `interface/semantic_interface.py` constructs and checks an exact observable quotient of a fully declared finite machine. It binds semantic checkpoints to their source and scope. `interface/run_demo.py` uses the actual Core 0.5 runtime to admit valid finite evidence and retain unverified evidence in quarantine. No learned neural decoder is used by this demonstrator.

## Current-code verification

Install the tested current-check dependencies in a separate environment:

```text
python -m pip install -r requirements-current.txt
python verify_release.py
python run_current_checks.py
python interface/run_demo.py --output ../local_demo
```

`verify_release.py` checks the edition inventory, source archive hashes, recursive ZIP integrity and absence of standalone font files. A digest is not author authentication or a theorem about program behavior.

`run_current_checks.py` works in temporary copies and writes a report to an external temporary output directory, printed at completion. An explicit new directory may be supplied with `--output`. The runner does not mutate the sealed sources, train a model, download a checkpoint, or execute an unspent learned endpoint. Core 0.5's original directory name is restored in its temporary copy because its own manifest checks the root basename.

Completed fresh current checks: Core 0.5 unit suite **168 passed**; corpus **66/66**, **1,825 receipts**; three regenerated corpus artifacts byte-identical to the originals; Discovery Bridge **20 tests** and **3 generated programs**; new interface **15 tests** and **2 actual OSL paths**. These counts describe separate check groups and are not a count of independent scientific replications.

The current replay is under `validation/current_replay/`. Earlier invocation failures and their corrections remain in `OSL/validation/EXECUTION_NOTES.md`.

## Neural experiment precautions

The archives are deliberately not merged into one Python package. Their training contracts and dependency environments differ. Extract a selected archive into a fresh directory and first read its version-specific status/result files. `SOURCE_LEDGER.json` lists candidate reading paths and byte-identical selected report copies under `Neuralese/evidence_index/`.

**Do not launch all scripts as a blanket verification step.** In particular:

- Semantic Retraction v0.3 is **ARMED_UNSPENT_CAPACITY_GATED**. Its learned bank was not consumed. Checkpoint-free tests are not learned scores.
- Entry–Cone–Holonomy v0.3.2 retains a completed one-shot endpoint. This edition verified its saved evidence, not a repeated endpoint evaluation.
- Invariant Observable Kernel v0.6 stopped at calibration. Its untouched screen and pilot were not run.

The full Ambient Packets and Packet Closure verifier attempts did not complete within their execution windows. Their respective unit-test transcripts reached **59** and **505** passes, but neither is represented as a full package-verifier pass. Other completed checks have independent return-code records. See `Neuralese/validation/`.

## Rebuild the manuscripts

```text
python build_manuscripts.py --output ../rebuilt_papers
```

See [BUILD.md](BUILD.md). The builder does not reseal the edition or overwrite its PDFs. Font binaries are not included; the TeX environment supplies its installed fonts.

## Provenance and licensing

Fifteen recovered original archives are preserved byte-for-byte: two OSL archives, twelve direct Neuralese archives, and the recurrent-depth archive. The combined source payload is 85,794,776 bytes. Each original and every selected report copy is hash-bound in the ledger. The edition adds new manuscripts, finite-interface code, portable wrappers, and validation records; it does not modify upstream source or historical thresholds.

Original license notices remain attached to their components. No blanket relicensing has been applied, and missing component licenses are not interpreted as an open-source grant. The package is prepared for the owner's review and distribution decision, not automatically published to GitHub. See [LICENSE_AND_PROVENANCE.md](LICENSE_AND_PROVENANCE.md).

## Claim boundary

No Lean verification is claimed. No universal proof of the Python interpreter, production authorization boundary, general neural-language emergence, stable arbitrary-depth learned semantics, or machine consciousness follows from this edition. The positive claims are the explicit mathematical derivations, the scoped executable semantics, the reported finite learned results, and the fresh computations actually documented here.
