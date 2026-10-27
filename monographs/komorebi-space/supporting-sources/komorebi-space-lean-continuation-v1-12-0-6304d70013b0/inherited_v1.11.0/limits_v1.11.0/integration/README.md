# Cumulative Lean continuation verification

This directory supplies an additive source assembler, a clean cumulative Lean replay, and an independently reviewed terminal integrity validator. A successful replay establishes that the formal statements compile and have the permitted axiom dependencies. Separate mathematical review must establish that the exported statements match the WR08, WR09, and WR16 contracts.

The fixed accepted parent is `budget_v1.10.0/integration/runs/clean_budget_01`: receipt SHA-256 `42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376`, postflight SHA-256 `b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2`. Its 148 production modules, three roots, 30 control specifications, and 4,935 audited declaration identities are retained.

## Gates

The assembler checks the complete parent source snapshot and axiom report against the accepted receipt and postflight. It copies the inherited control manifest directly, preserving all rejection markers. It adds new modules and `tests/limits` controls, appends imports to the combined root, and updates only the required audit inventories and exporter. The allowed inherited modifications are enumerated explicitly. Other inherited source and control bytes must remain unchanged. Destinations are never overwritten.

The production source scanner and complete import graph checks are unchanged from v1.10.0. They reject prohibited proof shortcuts, local policy weakening, missing local imports, cycles, and modules unreachable from the combined root. The replay begins with an empty project object directory and compiles every production module and root in topological order with `-j1 -DwarningAsError=true -DautoImplicit=false`. Only pinned external caches are reused. Source, helpers, project objects, compiler, adapter, external runtime caches, dependency revisions, and dependency source cleanliness are checked at the recorded endpoints.

Every project declaration receives the complete axiom audit. The allowed union remains `propext`, `Classical.choice`, and `Quot.sound`. Every declaration in a new module—including definitions and generated helpers—has its full type exported with explicit arguments, universes, proof terms, and fully qualified names. A missing or ellipsis-truncated new type fails. Inherited declaration names, modules, kinds, safety flags, and axiom sets must exactly match the 4,935 accepted parent identities.

The exporter improvement concerns presentation only: new declarations use the full printer options; selected inherited declarations use readable printer options. Previously, full printing was also applied to inherited types, including large expanded proof arguments. The complete axiom audit is unchanged, and new types retain the full printer. Each row records `type_mode` as `full`, `readable`, or `omitted`. The parent full-type report remains accepted historical evidence and is not modified.

Every inherited and new control executes. Positive controls must exit successfully. Rejection controls must return status 1, contain every declared intended marker, and avoid infrastructure, missing-symbol, missing-object, typeclass-synthesis, timeout, memory, or recursion/heartbeat errors. The exact command arguments, order, logs, exit statuses, and hashes are recorded.

The terminal validator does not import the replay helpers. It requires an independent helper-review manifest, reconstructs the expected command inventory and arguments, rechecks all artifacts, and independently reconstructs the inherited declaration catalogue from the fixed-hash parent report. It also verifies that the combined root changed only by the prescribed import suffix.

## Commands after source and helper review

Run from `/workspace/scratch/5d9f7f8127b0`:

```bash
python limits_v1.11.0/integration/scripts/assemble.py --base budget_v1.10.0/integration/runs/clean_budget_01 --overlay limits_v1.11.0/formal --label wr08_wr09_wr16_01
python limits_v1.11.0/integration/scripts/verify.py --assembly limits_v1.11.0/integration/assemblies/wr08_wr09_wr16_01 --runtime runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2 --path-adapter runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so --label clean_limits_01
python limits_v1.11.0/integration/postflight/validate.py --run limits_v1.11.0/integration/runs/clean_limits_01 --assembly limits_v1.11.0/integration/assemblies/wr08_wr09_wr16_01 --reviewed-helpers limits_v1.11.0/reviews/reviewed_helpers.json
```

The default timeout is 300 seconds per ordinary command and 1,800 seconds for the cumulative declaration exporter. A failed or interrupted attempt remains intact; a new attempt needs a new label. The terminal postflight file is likewise never overwritten.

The new control manifest lives at `formal/tests/control_manifest.json`. Entries contain `path`, `kind`, and `required_markers`; `path` is exactly `positive/Name.lean`, `negative/Name.lean`, or `policy/Name.lean`. Additional `purpose` text is descriptive. The manifest must cover every new `.lean` control exactly once, and there must be positive and negative controls.

## Trust and limits

The Lean compiler/kernel and external precompiled dependency caches remain trusted. External source revisions and runtime/cache bytes are pinned and checked, but dependencies are not rebuilt. Hashes checked at endpoints cannot detect a transient modification restored before a check. Compiler acceptance does not establish the adequacy of theorem hypotheses or their match to the monograph; that is the separate mathematical audit. Development exporter probes reuse accepted parent objects and are explicitly not clean cumulative replays.
