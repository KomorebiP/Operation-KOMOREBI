# Machine-Native Reasoning: Reviewed Mathematical Core

Komorebi P.

This package contains the cumulative formal companion to the 27 selected results
in Reviewed Core v0.2. Read `release/ADMISSION_RECORD.json` and
`release/ACCEPTED_PROGRESS_LEDGER.md` for the actual accepted status. A theorem-map
entry alone is not a verification receipt. The source book and accepted earlier
proofs remain preserved.

The new formal target is Core 3.2, the exact memory required to retain correction
under partition evidence. If r cell–target pairs are attainable, the correction
signatures correspond exactly to all subsets of those pairs. The resulting
state space has 2^r elements. Exactly r fixed binary bits suffice, and no exact
fixed-width memory on all candidate subsets can use fewer.

## Read and inspect

- `reader/Machine_Native_Reasoning_Reviewed_Core.pdf` is the refreshed core reader,
  with editable sources and its own publication checks alongside it.
- `source/core_v0.2.tex` and its PDF preserve the unchanged source statements.
- `THEOREM_MAP.json` connects all selected source statements to explicit endpoints.
- `docs/CORE32_PROOF_GUIDE.md` explains the final target and its boundaries.
- `release/REPORT.md` records the completed verification and delivery result.
- `release/BOOK_RECOVERY.md`, when supplied, identifies the separately missing
  expanded monograph and the authenticated reader provided instead.

The 27-result correspondence is a selected mathematical core. It does not certify
every specialist chapter of the larger Machine-Native Reasoning monograph, an
implemented intelligent system, or trained-model capabilities. The separate
Large Signal Model release has its own scope and evidence.

## Reproduce the formal verification

Use the saved portable Lean 4.34.0-rc2 distribution and pinned dependencies.
Restore the five compact runtime parts with `tools/restore_runtime.py`, following
`release/RUNTIME_REPRODUCTION.md`. The runtime remains external to this package.

```sh
export KOMOREBI_LEAN_RUNTIME=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
python3 tools/verify_package.py
python3 scripts/supervise.py --runtime "$KOMOREBI_LEAN_RUNTIME" --out evidence/my_replay --whole-timeout 1800
```

If the compiler reports `failed to locate application`, use the distribution's
preserved compatibility adapter:

```sh
LD_PRELOAD="$KOMOREBI_LEAN_RUNTIME/compat/app_path.so" python3 scripts/supervise.py --runtime "$KOMOREBI_LEAN_RUNTIME" --out evidence/my_replay_with_adapter --whole-timeout 1800
```

Choose a new evidence directory. The verifier cold-builds all production modules,
checks the source-facing interfaces, audits transitive axioms, replays substantive
modules through Lean's kernel, runs the rejection controls and checks the actual
imported dependency artifacts. Each compiler invocation uses one worker, warnings
as errors, a 4096 MiB internal limit and a 45-second wall limit. Dependency caches
are authenticated and reused, not rebuilt. This is the same Lean kernel, not an
independent proof checker.

```sh
python3 scripts/core32_exact.py --out /tmp/core32_exact.json
```

The finite enumerator derives signatures directly from event-filtered target
sets and compares them with occupancy. Its tested range and exact counts are
recorded in its output. Finite checks do not establish the universal theorem.

## Preservation and rights

The accepted Core25 source archive is the exact predecessor. All 75 substantive
production modules and five source-book files are pinned in `PREDECESSOR.json`.
Earlier partial historical recovery remains documented. New source and objects
must pass two sequential cold gates and a frozen-source comparison before the
release records admit the final selected result.

Original software and machine-readable contributions use MIT. Original writing
uses CC BY 4.0, with external notices and exceptions preserved. See `licenses/`.
No compiler, standalone fonts or third-party research papers are bundled.
