# Verification — v0.11.0

The cumulative source project has passed a clean build with the pinned Lean compiler. The full audit requests all 831 indexed named theorems and separately audits all 399 indexed constructions. All requests completed with only the permitted standard axioms. Module-order and root-import coverage include all 76 proof modules.

## Current evidence

- `audit/current_v0110/VERIFICATION.json`: complete clean build, pin checks, theorem audit and three negative controls.
- `audit/constructions_v0110/CONSTRUCTION_AUDIT.json`: all indexed non-theorem declarations.
- `audit/BASELINE_PRESERVATION_v0110.json`: direct byte comparison against all 70 v0.10.0 proof-module sources.
- `audit/current_v0110/NONABELIAN_FINITE.json`: independent exact S3 enumeration.
- `audit/computation-manifest.json`: scope, software, inputs, output hashes and non-claims for the finite audit.
- `audit/DEVELOPMENT_FAILURES_v0110.json`: the three corrected development compile failures.
- `audit/ENVIRONMENT_v0110.json`: memory-pressure mitigation without interrupting Lean.

Fresh archive replay evidence is delivered separately. The companion delivery receipt reports whether the exact delivered archive passed that independent extraction and rebuild. The archive's own files are not changed to insert later replay results.

## Reproduce

```bash
python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --audit-dir audit/my_replay --timeout 180
python3 scripts/audit_constructions.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --audit-dir audit/my_constructions
python3 checks/computation/nonabelian_cocycles_exact.py --output audit/my_finite.json
python3 scripts/check_hashes.py
python3 scripts/validate_manifest.py audit/computation-manifest.json --root .
```

Use new audit paths to preserve archived evidence. The runtime/cache is not included.

## Trust and meaning

Permitted axioms: `propext`, `Classical.choice`, `Quot.sound`. The positive library has no `sorry`, `admit`, custom `axiom`, `unsafe`, `native_decide`, or `implemented_by` declarations. Negative controls intentionally include an invalid claim, an admitted proof and an injected axiom; those are not imported into the positive library.

The compiler/kernel and imported cached dependencies remain trusted and were not independently rebuilt. The source indexer and lexical scanner are not independent Lean parsers. A successful kernel check verifies the formal statements under their declared hypotheses; it does not establish novelty or identify the construction with every intended mathematical realization.

The new nonabelian relative obstruction is a pointed orbit class. The groupoid of cocycles retains automorphisms, while the twisted extension fibers remain explicitly constructed section sets. General site descent, stacks, arbitrary category-valued sections, topological gauge estimates and arithmetic existence are not claimed.
