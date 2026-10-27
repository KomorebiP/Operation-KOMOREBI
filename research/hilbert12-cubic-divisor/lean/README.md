# H12 formal companion

The canonical tree contains one byte-authenticated selected copy of each mathematical module (42 modules, 453 distinct theorem declarations). The v0.14 current block is a subset of 25 theorem declarations: 11 new and 14 unchanged inherited. Counts are not added across repeated archive versions. Compiler acceptance certifies the exact types and their explicit hypotheses; it does not prove the original gamma/class-field equality.

Use `H12_Cubic_Divisor_Lean_Guide.pdf` for the scope and declaration guide. `DECLARATION_INVENTORY.json` contains names, signatures, source lines, origins/hashes, and fresh compiler-expanded theorem types. `SOURCE_MODULE_MAP.json` maps every selected module and all its historical occurrences. `CLAIM_COVERAGE.json` records the component-level relationship to the traditional manuscript.

Pinned compiler: Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Pinned Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The current block uses bundled Std only.

```bash
python3 verify.py --lean /path/to/pinned/bin/lean --scope current
lake update
lake exe cache get
python3 verify.py --lean /path/to/pinned/bin/lean \
  --mathlib .lake/packages/mathlib --scope all \
  --memory-mib 3072 --timeout 300 --audit-strategy auto
```

The verifier builds fresh project objects in a temporary directory, compiles sequentially with one worker and warnings as errors, checks admissions/custom axioms, hashes inputs before and after, prints exact theorem types and transitive axioms, and verifies positive/false arithmetic controls. Full replay uses per-module axiom auditors to avoid one large all-import process. The auto strategy chooses the exact-source-prefix auditor for H12PhaseRegulator and import-based auditors elsewhere. It records each process's exact argv, wall/CPU bounds, actual CPU time, and kernel-reported peak resident memory via POSIX wait4. The heap threshold is distinct from an OS address-space limit. The producing environment's executable-self-location adapter is explained under verification/runtime; normal installations do not need it.

Initial memory-limited attempts and any timeout/retry are retained separately, not erased or silently called successful. The final replay ledger selects only complete compiler-and-axiom evidence with matching source hashes. The single all-import auditor/combined import did not complete at the tested 3072 MiB cap; this is separate from the successful module-scoped evidence. Runtime and Mathlib caches are not included in the publication package.

Four payloads named in a foundation v0.2 historical replay receipt were not preserved, so those old output claims are unverified. Original archive/source authentication and the independent fresh checks are separate evidence.

The recorded final ledger combines the full module-scoped attempt with two focused, disjoint retries. Reproduce the focused retries separately if needed:

```bash
python3 verify.py --lean /path/to/pinned/bin/lean --mathlib .lake/packages/mathlib \
  --scope all --only H12CMNormCertificate --memory-mib 3072 --timeout 300 \
  --audit-strategy module --log-dir verification/retry_cmn_300sec
python3 verify.py --lean /path/to/pinned/bin/lean --mathlib .lake/packages/mathlib \
  --scope all --only H12PhaseRegulator --memory-mib 3072 --timeout 300 \
  --audit-strategy source --log-dir verification/retry_phase_source_prefix
```

`FINAL_REPLAY_AUDIT.json` is the exact union ledger for the recorded executions. The portable auto orchestration is a convenience for replaying the same established per-module commands; no fresh run of that entire auto orchestration is claimed.
