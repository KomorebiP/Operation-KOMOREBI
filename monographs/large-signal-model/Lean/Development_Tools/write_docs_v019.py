"""Write current human-readable formal-companion documentation from exact metadata.
Execution acceptance is taken from the separate source-bound report, never inferred.
"""
from pathlib import Path
import argparse,json
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
args=ap.parse_args();root=args.root.resolve()
def read(name):return json.loads((root/name).read_text())
def write(name,text):(root/name).write_text(text.strip()+"\n")
counts=read('RELEASE_COUNTS.json');coverage=read('COVERAGE.json');progress=read('PROGRESS.json')
complete=progress['completed'];partial=progress['partial'];unformal=progress['unformalized']
finished=len(complete)==87 and not partial and not unformal
release=counts['release'];checkpoint=progress['checkpoint']
lineage=read('SOURCE_LINEAGE.json')
np=len(lineage['inherited_proof_files']);nc=len(lineage['inherited_control_files']);nr=len(lineage.get('inherited_control_repairs',{}))
inheritance=(f'All {np} inherited mathematical source files remain byte for byte identical to the checked parent. Of its {nc} inherited rejection controls, {nc-nr} remain byte for byte identical and {nr} have documented test repairs removing unrelated elaboration or linter errors. Their false assertions are retained. Exact original and repaired control bytes, reasons and clean intended-rejection receipts are preserved in `history/control_repairs/` and bound by `SOURCE_LINEAGE.json`.') if nr else 'Inherited mathematical source and controls are preserved byte for byte against the checked parent.'
report='verification/current/report.json'
summary=f"{len(complete)}/87 complete proposition mappings, {len(partial)} partial and {len(unformal)} unformalized."
next_text=('All registered proposition mappings are complete. No remaining proposition obligation is recorded.' if finished else 'The next chronological unfinished proposition is P'+str(min(partial+unformal))+'. See ROADMAP_1.0.md for the exact remaining scope.')
execution="A source checkpoint and an execution receipt are separate records. The current cumulative report is `"+report+"`. A successful mathematical scope review does not by itself certify compilation."
write('README.md',f"""# Large Signal Model formal companion

{summary}

This project formalizes the 87 propositions registered in the Large Signal Model monograph. Its statements cover realization and predictive closure, positive probability domains, observable reconstruction, adaptive record laws, conditional concentration, curved certificates and structured learning from dependent observations. Complete means that the registered statement has an explicit Lean correspondence under its stated hypotheses. It does not mean that empirical model assumptions were verified by data.

There are {counts['proof_modules']} mathematical modules, {counts['named_declarations']} explicitly named declarations and {counts['named_theorems']} named theorems. The theorem total includes {counts['example_theorems']} worked-example theorems. Compiler-generated declarations are outside the named-source count. The {counts['negative_controls']} rejection controls exercise invalid boundary claims and are excluded from the proof import graph.

## Read and check

1. Read `LEAN_GUIDE.md` for the main theorem families and retained assumptions.
2. Read `COVERAGE.md` for the complete proposition correspondence. `COVERAGE.json` binds each target to its exact source hash.
3. Inspect `{report}` for the clean cumulative compile, axiom audit, kernel replay and rejection results. `CURRENT_STATUS.json` records delivery acceptance.
4. Restore the pinned portable Lean kit, then run `python3 scripts/verify.py --kit /absolute/path/to/kit --out verification/current`. The project uses the exact compiler and dependency revisions in `lean-toolchain` and `lake-manifest.json`. Exact certificate checks can take several minutes. The default per-stage limit is 900 seconds and can be set with `--timeout`.
5. Run `python3 scripts/check_metadata.py` to check register linkage, source inventories, inherited records and parser failure controls. `python3 scripts/test_source_scan.py` checks the comment-aware Lean lexical guard separately, and `python3 scripts/test_negative_control_classifier.py` checks control-diagnostic classification against captured failure cases.

{execution}

{next_text}

The frozen original manuscript and proof register are in `source/`. `source/FOUNDATIONS_REVIEWED.md` is the exact later mathematical body used by the current correspondence reviews, with its own preserved source hash. This archive is the Lean companion. The finalized monograph has its own publication artifact and its own visual review. Technical release metadata is retained for reproducibility.
""")
write('AUDIT.md',f"""# Verification scope

{summary}

The cumulative verification contract is a clean warnings-as-errors compilation of every mathematical module, an audit of every explicitly named declaration, individual kernel replay through the pinned Lean checker, and rejection of each invalid control for a mathematical diagnostic. A control must return the ordinary compiler diagnostic exit code 1 with exactly one intended mathematical diagnostic. Missing imports, unknown identifiers, qualified instance-synthesis failures, unrelated linter or helper errors, and resource failures do not count as successful rejection. The classifier is tested against the three actual superseded mixed diagnostics and their clean repaired receipts.

Only `propext`, `Classical.choice` and `Quot.sound` are permitted axiom dependencies. An axiom-free declaration is also accepted. Missing, extra, duplicate, truncated or unapproved axiom records fail the audit. Source inspection also rejects placeholders, added axioms and unchecked proof bypasses in active mathematical source.

The counts are {counts['proof_modules']} proof modules, {counts['named_declarations']} explicitly named declarations, {counts['named_theorems']} named theorems and {counts['negative_controls']} rejection controls. These are inventory counts, not measures of novelty or proof difficulty.

Raw correspondence reviews are retained in `verification/current_scope/`. They are internal same-team checks and are not represented as external independent review. They compare actual theorem hypotheses and conclusions with the frozen manuscript statements. Kernel checking validates the encoded claims; source correspondence establishes which manuscript statements those claims cover.

{execution}

{inheritance} The preserved predecessor source snapshot retains the identity chain. Historical receipts remain historical and do not substitute for current execution.
""")
write('LEAN_GUIDE.md',f"""# Reader's guide to the Lean companion

{summary}

Start from `KomorebiLSM.lean`, which imports every mathematical module in dependency order. Individual modules use small explicit theorem interfaces. The indexed names, source lines and source hashes for all 87 registered propositions are listed in `COVERAGE.json`.

## The mathematical route

The first part constructs realizations, predictive completions and observable behavior spaces. It distinguishes an exact population realization from finite sampled data and derives minimality, uniqueness and coordinate transport under explicit rank and spanning assumptions.

The probability part constructs positive cones, finite lifts and density instruments. It derives nonnegative normalized record laws and posterior updates on positive-evidence histories. Mass preservation and cone preservation are separate obligations. Robust certificates cover an entire declared uncertainty family, with genuine full-domain bounds.

The learning part links observable tables to state and operator reconstruction. Noise, coverage, conditioning and domain assumptions remain visible in the theorem signatures. Finite tables do not silently establish a global rank bound, an unknown cone or missing interventions.

The dependent-data results use actual filtrations and conditional expectations. The predictable residual certificate covers arbitrary measurable probability spaces, exact interval widths including zero width, and prospectively registered countable budgets. Covered adaptive actions target encountered contexts using recorded positive propensities. Observation-law comparison uses actual causal kernels and expected-under-P local costs.

The curved certificate results preserve orientation as well as squared Lorentz inequalities. Strict rational Bernstein searches retain degree and strict-margin hypotheses. A feasible certificate proves validity of its declared family; it does not manufacture statistical coverage for an unmodified generating process.

The regression result constructs the real Gaussian mixture and its all-time crossing event, then derives the exact determinant-dependent ridge ellipsoid. Predictable regressors, the actual conditional noise bound and the true-parameter norm bound remain hypotheses. No excitation or hidden-state discovery is inferred.

The final structured-learning results propagate rowwise moment confidence through an actual inverse moment map. Worked curved-state and rational rectangle examples keep observation-law error, certificate validity, same-trajectory coverage and selected-stage validity connected through explicit interfaces.

## Important interfaces

| Topic | Entry point |
|---|---|
| Proposition correspondence | `COVERAGE.md`, `COVERAGE.json` |
| Actual conditional residuals | `PredictableResidualP66.lean` |
| Covered adaptive actions | `CoveredActionBoundaries.lean` |
| Causal observation-law comparison | `ObservationLawComparison.lean` |
| Oriented robust margins | `RobustOrientedMargin.lean` |
| Conditional ridge regression | `RegressionConfidence.lean` |
| Observable moment confidence | `ObservableMomentConfidence.lean` |
| Current verification | `{report}` |

Only interfaces present in the current root import graph are mathematical source. Files under `verification/` are evidence and tooling unless imported explicitly by the checker. Invalid examples under `negative_controls/` must fail and are never imported by the mathematical root.

The current inventory contains {counts['named_theorems']} named theorems, including {counts['example_theorems']} worked-example results. Read each theorem's actual hypotheses before applying it. The frozen monograph and source register remain the reference for registered proposition scope.
""")
write('CONTINUE_HERE.md',f"""# Restart checkpoint

Checkpoint `{checkpoint}` has {summary.lower()}

{next_text}

The exact counts and accepted mappings are in `RELEASE_COUNTS.json`, `CURRENT_CHECKPOINT.json` and `COVERAGE.json`. Current source correspondence reviews are in `verification/current_scope/`. The cumulative compiler, axiom and kernel receipt is `{report}`. The overall delivery decision is in `CURRENT_STATUS.json`.

Preserve inherited proof source, retain failed diagnostics, and append the next checkpoint to `PROGRESS_LEDGER.md`. A subsequent change to any mathematical source requires new source-bound checking for the changed dependency closure and a corresponding coverage review. Do not reuse an old PASS for changed bytes.
""")
write('PROGRESS.md',f"""# Formalization progress

{summary}

{next_text}

The current source checkpoint is `{checkpoint}`. The inventory contains {counts['proof_modules']} modules, {counts['named_declarations']} explicitly named declarations, {counts['named_theorems']} named theorems and {counts['negative_controls']} rejection controls. Complete mappings are not weighted by effort or difficulty.

The added correspondence closes the arbitrary-space predictable concentration, covered-action evidence, causal observation-law comparison, oriented geometry, strict rational certificates, robust repair, vector regression, observable moment learning and structured dependent-data examples where recorded as complete in `COVERAGE.json`.

{execution}

The predecessor metadata, mathematical source snapshot, reviews and diagnostic receipts remain in `history/` and `verification/`. The current records do not overwrite the meaning of earlier checkpoints.
""")
ledger=root/'PROGRESS_LEDGER.md';old=ledger.read_text() if ledger.exists() else '# Progress ledger\n'
marker='## '+checkpoint
if marker in old and nr:
 a=old.index(marker);old=old[:a]+old[a:].replace('The checked parent mathematical sources and controls are retained byte for byte.',inheritance)
 ledger.write_text(old)
if marker not in old:
 ledger.write_text(old.rstrip()+f"\n\n{marker}\n\n{summary}\n\n{inheritance} Current mapping reviews bind the new endpoint signatures and hypotheses to the original register. Fresh cumulative execution is recorded separately in `{report}`. {next_text}\n")
write('PUBLICATION_STATUS.md',f"""# Publication status

{summary}

This artifact is the Lean formal companion and its verification evidence. The complete written monograph has a separate publication artifact and separate visual acceptance records. No PDF appendix is rewritten by this Lean-only delivery.

{execution}

The theorem correspondence retains the original mathematical statements and explicit model assumptions. It does not establish empirical success of a trained Large Signal Model or a solution to discovering an unknown hidden state from unrestricted data.

License terms for the predecessor theory, code and pinned dependencies are retained. No external repository is published by this packaging step.
""")
print(f'Wrote current documentation for {checkpoint}: {summary}')
