from pathlib import Path
import json
ROOT=Path('/workspace/scratch/ea498747acd5/work/Komorebi_LSM_Lean_0.16.0')
c=json.loads((ROOT/'RELEASE_COUNTS.json').read_text()); cp=json.loads((ROOT/'CURRENT_CHECKPOINT.json').read_text())
new=cp['accepted_new_propositions']; remaining=cp['remaining_ids']; partial=cp['partial_ids']
summary=f"{c['complete_propositions']}/87 complete formal mappings, {len(partial)} partial, and {len(remaining)} unformalized."
new_names=', '.join('P'+str(i) for i in new)
first=min(remaining) if remaining else None
prefix=0
while prefix+1 in cp['complete_ids']: prefix+=1
(ROOT/'README.md').write_text(f'''# Large Signal Model formal companion

{summary}

The monograph contains 87 propositions with written proofs. This companion checks the mapped formal statements in Lean. Every proposition P1 through P{prefix} has a complete formal mapping. The full 87-proposition formalization remains open.

This checkpoint adds complete mappings for {new_names}. `COVERAGE.md` states the exact scope of every mapping, and `ROADMAP_1.0.md` lists the outstanding work. A register entry or finite example is not a kernel proof.

## Verify with the portable runtime

Restore the matching portable Lean kit and pass its root folder to the checker. The supported runtime is Lean 4.34.0-rc2 with mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The checker validates those pins, removes project build objects, compiles every proof module with warnings treated as errors, audits every named declaration, replays each module in the kernel and checks the false-claim controls.

```bash
python3 scripts/verify_hashes.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out .verification-run
```

Run the inventory check before generating new reports or build files. The upstream library is pinned and imported rather than rebuilt or exhaustively replayed.

On Windows, use WSL2 and `Check.ps1`, passing the Linux paths of this project and restored kit. `PORTABLE_LEAN.md` explains the runtime layout and startup recovery.

## Read the result

Start with `LEAN_GUIDE.md`, then the mapped proposition in `COVERAGE.md`. `AUDIT.md` records review boundaries and `PROGRESS_LEDGER.md` preserves the restart state. The original manuscript and source register remain unchanged under `source/`. The corrected editable publication body is supplied separately with the monograph.

The reference laboratory includes exact rational examples, certificates and scientific figures. Its finite runs support reproducibility and boundary checks, while the Lean files prove their stated universal claims. Production PR-LASM software is a separate artifact.
''')
prior=(ROOT/'history/PREDECESSOR_0.15.0_LEAN_GUIDE.md').read_text()
tail=prior[prior.index('## Spectral construction and decoder'):]
(ROOT/'LEAN_GUIDE.md').write_text(f'''# Guide to the formal companion

{summary} P1 through P{prefix} are mapped completely.

The source correspondence is a reviewed dictionary. Lean checks formal propositions and dependencies. It does not read the English manuscript or infer that measured data satisfy a declared observation protocol.

## Current proof paths

- P46 constructs the exact rational three-coordinate model, proves density of its forward rotation orbit, identifies its canonical all-test cone with the Lorentz cone and proves invariant-cone uniqueness. The no-finite-generator result covers redundant normalized synthesis maps. Reachability and observability establish predictive dimension three.
- P47 derives the Lorentz base norm from its positive-decomposition infimum. It proves the actual regular polygon inradius, finite positive lift and full-span synthesis, the cosine and integer-ceiling sufficient bounds, and the common-policy observation-law TV budget. The diamond allows attenuation at most 5/7 and gives an entirely rational certificate at 2/3. That changed model has a different observation law.
- P49 connects observable reconstruction, actual nonnegative coefficient witnesses and covered initial states to all-horizon stochastic validity. Robust uncertainty coverage is supplied on an explicit measurable event. The same cone gives the common-policy law budget, positive-event conditioning, exact atlas transport and complete signed-packet synthesis. Individual packets need separate positivity.

The preceding checkpoint's guide is preserved under `history/`. It explains the conditional expectation, grammar accounting, whole-record Bayesian refinement, missing intervention, reset concentration, observable completion, sequential confidence and covariance proof paths. All current scopes and endpoints are listed in `COVERAGE.md`.

## Boundaries retained by the proofs

A finite table does not certify global rank or missing intervention coverage. Matrix inversion does not prove fitted-model positivity. Conditioning retains its positive evidence requirements. Complete signed synthesis is distinct from a probability mixture. Statistical coverage is supplied by the declared observation protocol. Finite positive generators are a sufficient certificate language; P46 does not prohibit curved or quadratic certificates.

No active proof uses placeholders, new project axioms, native_decide or unsafe execution. All explicitly named declarations are audited against the standard dependencies propext, Classical.choice and Quot.sound. Module kernel replay checks the compiled environment beyond the source-index count.

'''+tail)
(ROOT/'AUDIT.md').write_text(f'''# Verification and correspondence audit

{summary} The full formalization goal remains open.

Every one of the predecessor's 109 proof modules is retained byte for byte. The added modules and reviewed mappings are recorded in `CURRENT_CHECKPOINT.json`. Original theory and register hashes are unchanged. The corrected publication body retains the five previously recorded assumption clarifications.

## Mathematical review

The coordinator and separate agents reviewed the actual raw proof sources against the registered statements. These are internal reviews within one model/team lineage. They are distinct from independent external refereeing and from compiler acceptance.

P46's collected theorem assumes no rank or desired cone-equality conclusion. Density, geometry, finite-generator obstruction and rank are proved for the actual rational operators. P47 discharges the polygon inradius and exact base-norm obligations before deriving its finite lift and observation-law budget. P49 derives validity from literal nonnegative matrices and a normalized prior, retains whole-set robust witnesses and initial coverage, and treats statistical confidence as a supplied measurable event. Exact atlas transport retains the same coefficient witnesses; packet positivity remains separate.

Per-claim review records give source hashes, hypotheses and limits. English correspondence remains a reviewed step distinct from kernel acceptance.

## Executed evidence

`verification/current/report.json` is the fresh cumulative source-bound verifier record. It records each compilation, the named-declaration axiom audit, every module kernel replay, executable rational examples and all negative controls. `verification/current/metadata.json` records consistency checks, not additional mathematical theorems. The delivered archive has a separate integrity and source-binding receipt, including fresh extraction and metadata checks; that procedure does not perform another Lean compilation or replay.

The portable runtime passed its 16 supplied tests. The unchanged reference laboratory has a retained source-bound PASS for all 29 scripts. Those finite checks do not replace the universal Lean statements. Development failures and superseded checks are retained separately from the accepted cumulative report.

## Trust boundary

The pinned upstream Lean and Mathlib environment is imported. The project does not claim to rebuild or replay all of Mathlib. Allowed named-declaration dependencies are propext, Classical.choice and Quot.sound. Negative controls must fail for mathematical reasons rather than absent imports or unknown identifiers. Source hashes bind receipts to actual inputs and do not attest to real-world observations or host integrity.

Every remaining manuscript proposition retains its written proof and exact register span. Unformalized does not mean refuted, and a checked supporting theorem does not certify the entire remaining program.
''')
(ROOT/'CONTINUE_HERE.md').write_text(f'''# Restart checkpoint

Checkpoint LSM-0.16.0 descends from the exact delivered archive SHA-256 `{cp['parent_archive_sha256']}`. Source hashes and accepted proposition IDs are in `CURRENT_CHECKPOINT.json`.

{summary} Every proposition P1 through P{prefix} is mapped completely. Complete additions: {new_names}. Partial mappings: {', '.join('P'+str(i) for i in partial) or 'none'}.

The original goal remains open. The monograph is a complete written treatment; remaining formal obligations are listed exhaustively in `ROADMAP_1.0.json`.

## Next chronological obligation

P{first} is the first proposition without a formal mapping. Read its exact statement and proof span in `source/PROOF_REGISTER_1.0.0.json` and the surrounding definitions in `source/FOUNDATIONS_1.0.0.md`.

For P50, prove the actual injective symmetric-matrix embedding certificate: closed, pointed, generating cone, positive trace on its nonzero elements and compact trace-one base. Derive invariance from the weighted congruence identities, all-word probability validity from exact mass conservation and initial coverage, and exact coordinate transport. A finite numerical PSD example does not close those universal obligations. The inequality between ambient trace norm and the cone base norm has its separate subspace caveat.

P66 remains partial. Coverage records retain its exact unsupported sample-space and conditional-expectation/index-transfer regimes. P68 does not supply those missing concentration antecedents.

Keep the source/register frozen, append a progress checkpoint, preserve failed routes and diagnostics, update correspondence only after raw-proof review, and run the source-bound verifier and archive integrity checks.
''')
(ROOT/'PROGRESS.md').write_text(f'''# Current progress

{summary}

Complete additions: {new_names}. Every proposition P1 through P{prefix} is mapped completely. Remaining obligations are not reclassified as proved by the monograph or reference runs.

`PROGRESS_LEDGER.md` retains ancestry, evidence boundaries, unresolved obligations and the next restart point. Prior checkpoint narratives are preserved under `history/`.
''')
(ROOT/'PUBLICATION_STATUS.md').write_text('''# Publication status

The complete written monograph and formal companion have separate acceptance records. Formal coverage remains explicit: complete, partial or unformalized. The entire 87-proposition formalization is still open.

The original XeLaTeX authoring files were unavailable in the source archives. The publication retains the original complete PDF, an editable corrected mathematical body and a reproducible surgical PDF update script. It preserves all 174 pages, scientific figures, register, glossary, references and navigation. Markdown is not represented as the missing XeLaTeX source.

License terms for the predecessor theory, code and dependencies are retained. Bundled P052 fonts retain their license and font exception. No external repository was published by this task.
''')
prior_ledger=(ROOT/'history/PREDECESSOR_0.15.0_PROGRESS_LEDGER.md').read_text().rstrip()
(ROOT/'PROGRESS_LEDGER.md').write_text(prior_ledger+f'''

## Checkpoint LSM-0.16.0

- Parent delivered archive SHA-256: `{cp['parent_archive_sha256']}`.
- Parent: 48 complete mappings, one partial (P66), 38 unformalized; 109 proof modules, 1,639 named declarations, 1,272 named theorems, 94 rejection controls.
- Goal reached: {cp['goal_reached']}.
- Current state: {summary}
- Complete additions: {new_names}.
- Current inventory: {c['proof_modules']} proof modules, {c['named_declarations']:,} named declarations, {c['named_theorems']:,} named theorems and {c['negative_controls']} rejection controls.
- All inherited proof and rejection-control files remain byte-identical. Source hashes are in the checkpoint and lineage records.
- Raw-source coordinator and separate-agent internal reviews are retained with per-file hashes. They are not independent external certification.
- Accepted execution: `verification/current/report.json` and `verification/current/metadata.json`. Historical/development receipts are not substituted for this run.
- The archive's integrity and source-binding receipt is separate from source compilation and kernel replay. Its extraction checks do not claim another Lean run.
- The unchanged reference laboratory retains all 29 source-bound script passes. The portable runtime retains its 16-test check.
- The full 174-page monograph is synchronized to accepted scope and execution. Original source, corrected editable body, reproducible PDF patches, bookmarks and unchanged-page identity checks are retained.

## Restart after this checkpoint

The original goal remains open. Next chronological unformalized target: P{first}. P66 remains partial. The exhaustive remaining IDs and exact obligations are in `ROADMAP_1.0.json` and `COVERAGE.json`.

No numerical example, written proof, failed search or source hash closes an unformalized implication. Continue from `CONTINUE_HERE.md` and append the next checkpoint without rewriting this retained history.
''')
print(summary)
