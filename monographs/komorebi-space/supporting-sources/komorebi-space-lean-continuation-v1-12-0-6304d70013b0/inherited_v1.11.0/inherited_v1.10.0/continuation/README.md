# Komorebi Space · Formal continuation v1.8.0

WR01–WR02 and the protected-kernel bridge are now formalized and verified. The complete inherited reader set is included, along with the updated continuation guide, sources, raw evidence, and progress ledger.

- `formal/`: complete final source snapshot, with one combined entrypoint `KomorebiSpaceCombined.lean`.
- `inherited_v1.7.0/`: unchanged 161-page monograph, 43-page visual guide, 36-page Lean guide, historical source and evidence.
- `continuation/publication/Continuation_Guide.pdf`: new reader guide and detailed alternate projection proofs.
- `continuation/FORMAL_COVERAGE.json`: exact public theorem types for each newly covered clause.
- `continuation/integration/runs/`: accepted compiler, axiom, control, and terminal integrity evidence. Compiled object caches are omitted from the delivery.
- `PROGRESS_LEDGER.md`: current completion boundary and exact next block.

The remaining WR formalization is eight written-only groups and the two partial limit conclusions. The full final library contains 144 production modules and 4,872 audited declarations. Generated and auxiliary declarations are included in that count.

## Reproduce with the pinned portable runtime

The runtime is supplied separately. It contains Lean 4.34.0-rc2 and the nine pinned dependencies. On the tested Linux runtime, its documented self-path compatibility adapter is required. Set `KS_RUNTIME` to the runtime folder, then from this package root run:

```sh
python3 continuation/integration/scripts/verify.py --runtime "$KS_RUNTIME" --path-adapter "$KS_RUNTIME/compat/app_path.so" --label local_base
python3 continuation/integration/postflight/validate.py --base continuation/integration/runs/local_base
python3 continuation/integration/overlay/verify_overlay.py --base continuation/integration/runs/local_base --base-postflight continuation/integration/runs/local_base/postflight.json --overlay continuation/formal --runtime "$KS_RUNTIME" --path-adapter "$KS_RUNTIME/compat/app_path.so" --label local_wr
```

Each replay refuses to overwrite an existing label. Run the commands in order and stop if any exits nonzero. The second check is terminal evidence validation, not another Lean compilation. The final replay reuses only the newly validated base objects and conducts a fresh full-scope audit.

No independent kernel, full-source dependency rebuild, native Windows validation, or universal proof of the Python implementation is claimed. The older publication PDFs retain their historical evidence wording, so the new guide and ledger are authoritative for this continuation's formal status.
