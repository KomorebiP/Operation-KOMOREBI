# Integration worker record

## Preparation

- Read the predecessor assembler, clean replay, incremental replay and terminal postflight. The new block uses a genuinely clean project build rather than inherited project objects.
- Constructed an immutable source assembler, complete graph inventory, exact compiler/control command records, full project axiom audit and type export for every new declaration.
- Python source syntax and CLI entrypoints passed preparation checks.
- Exact exporter compatibility smoke passed on one inherited module: seven declarations, permitted axioms only, all types nonempty and untruncated. This was a helper compatibility check, not a new theorem verification.

## Independent review corrections

The separate verifier reviewer identified provenance weaknesses before the final run. These were corrected before the helper revisions were accepted:

1. Added SHA-256 endpoint inventories for toolchain bin/lib files and all external compiled cache files, with symlink target strings, plus terminal dependency revision/cleanliness checks. This detects persistent runtime input changes while keeping initial external cache authenticity an explicit trust boundary.
2. Bound the terminal validator to its independently reviewed source hash and bound the copied Lean exporter explicitly to the reviewed helper revision.
3. Replaced ordinary Python helper imports with direct source compilation/loading to avoid timestamp-valid cached bytecode superseding the recorded helper source.
4. Rechecked logs, declaration catalogues, axiom report, runtime manifest, adapter and assembly at the terminal postflight boundary.

The accepted reviewed helper manifest is `reviews/reviewed_helpers.json` relative to the block root. The first frozen source assembly is `assemblies/wr03_wr05_01`. It contains 151 targets, 148 production modules and 30 controls.

## Final run and diagnostic note

The first clean attempt is `runs/clean_budget_01`. Its per-command receipt and immutable logs are the authoritative execution record. All 151 project targets compiled successfully before the full axiom/type export began.

While checking whether the long-running exporter was active, a separate `ps -C lean -o pid,etime,pcpu,rss,args` command failed with `fatal library error, lookup self`. No compiler command failed at this point. Read-only Python inspection of `/proc` successfully confirmed that the exporter process was present, using approximately 3.0 GiB of resident memory. This diagnostic failure did not alter the replay, scripts, source, objects or logs.

Final acceptance is determined by the terminal run receipt and postflight, not this narrative progress note.

## Audit completion and coordination event

The full exporter completed successfully in 385.582 seconds, with 4,935 audited project declarations and 63 declarations from the four new modules. All new types were nonempty and untruncated. The axiom union contains only `Classical.choice`, `Quot.sound`, and `propext`. The full report is approximately 172.18 MB because fully explicit type printing was also applied to the inherited type selection. This is a performance consideration for a future reviewed verifier revision, not an audit failure.

While the audit was still believed active from the previous buffered observation, the coordinator requested a clean interruption and a reviewed printing optimization. A signal attempt returned `ProcessLookupError` and affected no process. The next output showed that the exporter had already passed and controls were executing. The coordinator immediately retained the original attempt. No helper, source, control, assembly or evidence bytes were edited as part of the proposed optimization, and no second assembly/run was started. The original `clean_budget_01` run continued normally.

## Terminal acceptance

The original clean replay and independently reviewed terminal validator both returned PASS. All 219 required commands have exact recorded arguments and retained logs. All 151 project targets compiled from empty project objects. The full audit covered 4,935 declarations, including 63 new declarations with full types, and all 30 controls returned their intended outcomes. Source, helper, object and trusted runtime/cache endpoint identities were preserved.

The replay lasted 1,096.327 seconds, including 530.727 seconds compiling project targets and 385.582 seconds exporting/auditing declarations. Exact receipt, postflight and inventory hashes are recorded in `ACCEPTANCE_SUMMARY.json`. The initial external cache contents, compiler/kernel, system libraries and Python runtime remain trust assumptions. No native Windows replay or independent external package rebuild is claimed.

A separate final reviewer accepted the terminal receipt, all source/object/log bindings, and the 22 intended rejection logs. Its final report is `../reviews/VERIFIER_REVIEW.md`. The original reviewed helper manifest remained unchanged.
