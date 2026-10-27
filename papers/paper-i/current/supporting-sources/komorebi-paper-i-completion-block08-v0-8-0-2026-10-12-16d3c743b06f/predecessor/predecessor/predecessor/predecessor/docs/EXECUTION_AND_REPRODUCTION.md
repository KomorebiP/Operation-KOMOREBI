# Execution and reproduction

The accepted execution has two fresh stages. The baseline stage runs the complete unchanged Block 03 verifier, including its own predecessor audit. The extension stage requires that completed baseline receipt, authenticates the runtime and baseline source/object hashes, and builds all five new modules into a second empty directory. Both stages are required for Block 04 acceptance.

The new final stage never imports saved predecessor project objects. Development checks did use saved prior objects to avoid rebuilding an already verified baseline after each proof edit. Development evidence is explicitly separated from final acceptance.

Use `bash scripts/run_block04.sh RUNTIME NEW_OUTPUT` for the combined reproduction recipe. The output directory must not exist. Its missing-argument and existing-output refusal guards were actually tested. For this handoff, the two constituent mathematical stages were executed separately. The combined launcher is syntax-checked rather than claimed as a third full audit run.

The portable runtime and authenticated upstream cache are not included. The archive identity is recorded in evidence/RUNTIME_RECOVERY.json, and detailed pinned runtime-file bindings are retained in the predecessor. Do not run lake update. The final verifiers and bundle checker use Python's standard library.

`scripts/dev_check.py` is the preserved session-specific development helper. It references the development environment capture in the original working container. It is not the reproduction entry point and no environment dump is included in this release. Reproduction uses the portable-runtime environment through the verified audit scripts instead.

The same-kernel replay wrapper selects exact module names and runs serially. It does not invoke the command-line checker's broad prefix mode, rebuild every Mathlib object, or use a separately implemented kernel. Compiler-owned declaration enumeration includes private and generated names.

Failed development snapshots, interrupted receipts and tooling incidents are retained. Deliberately invalid tests have expected nonzero exits and are separate from production source. A report is accepted only when all required positive and negative checks match their expected outcomes and source/object hashes remain unchanged.

The release date uses America/Chicago. Execution receipts use UTC, so the last audit stage may carry an 11 October 2026 UTC timestamp while the local release date remains 10 October 2026.
