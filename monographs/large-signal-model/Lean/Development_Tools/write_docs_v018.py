from pathlib import Path
import json

root=Path('/workspace/scratch/ea498747acd5/work/Komorebi_LSM_Lean_0.18.0')
c=json.loads((root/'RELEASE_COUNTS.json').read_text())
cp=json.loads((root/'CURRENT_CHECKPOINT.json').read_text())
cfg=json.loads(Path('/workspace/scratch/ea498747acd5/maintenance/accepted_claims_v018.json').read_text())
assert c['release']=='0.18.0' and cp['accepted_new_propositions']==list(range(58,66))
summary=f"{c['complete_propositions']}/87 complete formal mappings, {c['partial_propositions']} partial, and {c['unformalized_propositions']} unformalized."
new=', '.join('P'+str(n) for n in cp['accepted_new_propositions'])
scopes='\n'.join(f"- P{n}: {x['scope']}" for n,x in cfg['claims'].items())
(root/'README.md').write_text(f'''# Large Signal Model formal companion

{summary}

Every proposition P1 through P65, together with P68, has a complete formal mapping. P66 remains partial. The full 87-proposition goal remains open. The monograph contains written proofs for all 87 propositions; the Lean companion checks the explicitly mapped formal statements.

This checkpoint adds {new}. `COVERAGE.md` gives the exact scope and `ROADMAP_1.0.md` lists every outstanding obligation. Register entries and finite examples do not substitute for kernel proofs.

## Verification

Use the portable Lean 4.34.0-rc2 runtime with mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The checker validates the pins, removes project build objects, compiles every module with warnings as errors, audits every named declaration, replays each module in the kernel and checks the mathematical rejection controls.

```bash
python3 scripts/verify_hashes.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out .verification-run
```

Run the inventory check before generating new reports or build files. The upstream library is imported at the pinned revision; it is not exhaustively rebuilt or replayed. Windows users can use WSL2 and `Check.ps1` with Linux project and kit paths. See `PORTABLE_LEAN.md`.

Start with `LEAN_GUIDE.md`, `AUDIT.md` and the desired entry in `COVERAGE.md`. `PROGRESS_LEDGER.md` preserves ancestry and restart state. Original theory and register files remain frozen under `source/`; the corrected editable publication body accompanies the monograph. The reference laboratory retains exact rational examples and scientific figures with explicit finite-test limits. Production PR-LASM is a separate artifact.
''')
oldguide=(root/'history/PREDECESSOR_0.17.0_LEAN_GUIDE.md').read_text()
tail=oldguide[oldguide.index('## Spectral construction and decoder'):]
(root/'LEAN_GUIDE.md').write_text(f'''# Guide to the formal companion

{summary} P1-P65 and P68 are mapped completely.

Manuscript correspondence is a reviewed dictionary. Lean checks formal propositions and dependencies; it does not read the English manuscript or establish that observed data satisfy a declared protocol.

## New proof paths

{scopes}

The preceding guide is preserved under `history/`. It records the earlier conditional-expectation, grammar, whole-record Bayesian refinement, intervention, reset concentration, observable completion, curved rotation and continuous certificate constructions. Every current mapped scope and endpoint remains in `COVERAGE.md`.

## Retained boundaries

Supplied dimension, degree, coverage and domain assumptions remain visible. Matrix inversion does not prove fitted positivity. Conditioning requires positive evidence. Complete signed synthesis is distinct from assigning each packet a probability law. Bin-history policies retain exact coarsening; within-cell-reactive policies require a separate comparison. Coefficient estimates and model corrections retain their own error budgets.

Internal source review, source identity, compiler acceptance, kernel replay and archive integrity are different checks. No external independent certification is claimed. Active proofs have no placeholders or new project axioms; named dependencies are audited against propext, Classical.choice and Quot.sound. Module replay also checks the generated environment beyond the named source inventory.

'''+tail)
(root/'AUDIT.md').write_text(f'''# Verification and correspondence audit

{summary} The full formalization goal remains open.

All 133 predecessor proof modules and all 118 predecessor rejection controls retain their exact bytes. New accepted modules and source hashes appear in `CURRENT_CHECKPOINT.json`; ancestry is bound to the exact delivered predecessor archive. Original theory and register hashes remain unchanged.

## Mathematical correspondence

The coordinator and separate agents reviewed actual raw sources against registered statements. These reviews share a model/team lineage and are not external independent refereeing. Per-claim records retain source hashes, hypotheses, claim boundaries and the extent of execution performed by each reviewer.

{scopes}

The optional conditional-event helper for P59 has its weaker eventwise scope recorded. It is not accepted as the sharper adjacent conditional-law assertion. P63 discovery remains conditional and sufficient. P64 does not require a finite true degree. P65 keeps bias, coefficient error and correction error distinct.

## Executed evidence

`verification/current/report.json` records the fresh cumulative source-bound compilation, complete named axiom audit, every module kernel replay, exact examples and negative controls. `verification/current/metadata.json` records consistency checks rather than more theorems. A separate delivered-archive receipt checks complete byte inventory, CRC, fresh extraction, manifest and metadata; those procedures do not claim a second Lean run.

The portable runtime passed its 16 supplied tests. The unchanged reference laboratory retains a source-bound PASS for all 29 scripts; those runs were not freshly repeated for this checkpoint. Development failures and superseded checks remain separate from the accepted cumulative run.

## Trust boundary

Pinned Lean and Mathlib are imported. The project does not rebuild or replay all upstream libraries. Named logical dependencies are propext, Classical.choice and Quot.sound. Negative controls must fail for mathematical reasons, without missing imports or unknown identifiers. Hashes establish identity, not mathematical truth, host integrity or empirical coverage.

Every unfinished proposition retains its written proof and register span. A supporting theorem, finite experiment or failed search does not close an unformalized implication.
''')
(root/'CONTINUE_HERE.md').write_text(f'''# Restart checkpoint

Checkpoint LSM-0.18.0 descends from delivered archive SHA-256 `{cp['parent_archive_sha256']}`. Accepted source hashes and proposition IDs are in `CURRENT_CHECKPOINT.json`.

{summary} Complete additions: {new}. P1-P65 and P68 are complete; P66 remains partial. The exact remaining obligations are in `COVERAGE.json` and `ROADMAP_1.0.json`.

## Next work

Close full P66 before treating its restricted theorem as the full arbitrary-sample-space, interval-width, countable-test statement. Existing restricted results remain valid. A direct conditional-expectation proof can avoid the standard-Borel hypothesis of Mathlib's conditional subgaussian interface; actual conditional exponential inequalities and filtration iteration must be proved, not supplied as fields.

P67 is the first chronologically unformalized proposition. Its inverse-propensity identity must follow from an actual randomized action/observation experiment, with recorded predictable probabilities and positive coverage. P69 needs actual full causal-kernel history laws and expected-under-P conditional TV costs. The subsequent geometry, robust repair, regression and structured learning obligations remain listed exhaustively.

Preserve inherited sources, retain failed routes and diagnostics, append the next ledger checkpoint, update correspondence only after raw-source review, and complete the fresh source-bound verification and delivery integrity checks.
''')
(root/'PROGRESS.md').write_text(f'''# Current progress

{summary}

Complete additions: {new}. P1-P65 and P68 are mapped completely. The original goal remains open; neither the monograph nor reference runs reclassify remaining formal obligations as proved.

`PROGRESS_LEDGER.md` preserves ancestry, execution boundaries and the next restart state. Prior checkpoint narratives remain under `history/`.
''')
prior=(root/'history/PREDECESSOR_0.17.0_PROGRESS_LEDGER.md').read_text().rstrip()
(root/'PROGRESS_LEDGER.md').write_text(prior+f'''

## Checkpoint LSM-0.18.0

- Parent delivered archive SHA-256: `{cp['parent_archive_sha256']}`.
- Parent: 58 complete, one partial (P66), 28 unformalized; 133 proof modules, 2,299 named declarations, 1,753 named theorems and 118 rejection controls.
- Goal reached: {cp['goal_reached']}.
- Current state: {summary}
- Complete additions: {new}.
- Inventory: {c['proof_modules']} proof modules, {c['named_declarations']:,} named declarations, {c['named_theorems']:,} named theorems and {c['negative_controls']} rejection controls.
- All inherited proof and control files remain byte-identical. Raw-source internal reviews have per-file hashes and explicit provenance.
- Accepted cumulative execution is recorded only by `verification/current/report.json` and `verification/current/metadata.json`; individual development checks are separate.
- Archive integrity and extracted metadata checks do not claim a second Lean compilation or replay.
- The unchanged reference laboratory retains its 29 source-bound script passes, and the portable runtime its 16-test pass.
- The 174-page monograph is synchronized to the accepted scope and execution. Original source, corrected editable body, reproducible PDF edits, bookmarks and unchanged-page identity checks remain included.

## Restart after this checkpoint

The original goal remains open. P66 is partial; P67 is the first chronological unformalized target. Read `CONTINUE_HERE.md` and the exact coverage/roadmap records. Preserve this ancestry when appending the next checkpoint.
''')
print(summary)
