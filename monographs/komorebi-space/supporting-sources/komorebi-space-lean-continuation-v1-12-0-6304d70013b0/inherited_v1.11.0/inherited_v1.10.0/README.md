# Komorebi Space — full monograph and budget formalization v1.10.0

This release completes the formal counterparts of WR03, WR04, and WR05: the attained budget profile, the sharp dual maximum, and the common-space robustness bound. It adds 39 explicit theorems across four modules, with 43 named public declarations including definitions and an instance. Every principal clause of the three theorem groups has been independently compared with its exact Lean type.

The complete formal WR groups are now WR01–WR07, WR13, and WR14: nine of sixteen. WR09 and WR16 retain partial pointwise coverage. WR08, WR10–WR12, and WR15 retain written proofs without a complete formal counterpart. This is completion of classical Hilbert-space arguments in the project's formal framework, not a claim that those classical results are new mathematics.

The full monograph incorporates the new coverage and a recorded prose correction: the nearest reachable image is the projection, and the optimal residual is the datum minus that projection. The theorem statements are unchanged. Printed-proof auditing, formal theorem correspondence, compiler acceptance, and publication proofreading are recorded separately.

## Start here

| File or directory | Purpose |
| --- | --- |
| `publication/Komorebi_Space_Monograph_v1.10.0.pdf` | Current complete monograph |
| `PROGRESS_LEDGER.md` and `.json` | Accepted checkpoint, results, mistakes corrected, and remaining work |
| `VERIFICATION_SUMMARY.json` | Exact accepted run identities, counts, and evidence hashes |
| `PUBLICATION_VERIFICATION.json` | Current PDF, source hashes, and visual verification |
| `source/` | Complete current LaTeX and mathematical figure sources |
| `formal/` | Complete accepted cumulative source/control snapshot |
| `budget_v1.10.0/records/EVENTS.jsonl` | Append-only research event record |
| `budget_v1.10.0/reviews/` | Independent printed-proof, exact-type, verifier, and package reviews |
| `budget_v1.10.0/development/` | Numbered successful and failed attempts, source snapshots, diagnostics, and clause maps |
| `budget_v1.10.0/integration/` | Clean replay source assembly, scripts, command logs, axiom/type exports, runtime file hashes, and terminal receipts |
| `budget_v1.10.0/NEXT_RESEARCH_BLOCK.md` | Exact WR08 restart scope and subsequent gaps |
| `history/v1.9.0/` | Previous manuscript, formal snapshot, scripts, publication reviews, and release records |
| `continuation/`, `inherited_v1.7.0/`, `history/v1.8.0/` | Preserved earlier sources and evidence |

## Rebuild the monograph

From the extracted package root, with Python 3 and the LaTeX packages named in `source/preamble.tex`:

```bash
python3 scripts/check_manuscript.py
python3 scripts/build_monograph.py local_rebuild
```

Use a new build label. The script performs three pdfLaTeX passes and records source hashes and diagnostics. The result is `publication/Komorebi_Space_Monograph.pdf`. PDF metadata can vary between builds. All figures are TikZ diagrams or plots of explicit mathematical formulas; no generated artwork is used.

## Replay the formal project

The Linux portable Lean 4.34.0-rc2 runtime is supplied separately. Point `RUNTIME_DIR` to its extracted directory, retaining the pinned external package cache and compatibility adapter. The following paths apply to this extracted handoff, rather than to the original development workspace:

```bash
RUNTIME_DIR=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2

python3 budget_v1.10.0/integration/scripts/assemble.py \
  --base continuation/integration/runs/wr01_wr02_overlay_01 \
  --published history/v1.9.0/formal \
  --overlay budget_v1.10.0/formal \
  --label local_budget_assembly

python3 budget_v1.10.0/integration/scripts/verify.py \
  --assembly budget_v1.10.0/integration/assemblies/local_budget_assembly \
  --runtime "$RUNTIME_DIR" \
  --path-adapter "$RUNTIME_DIR/compat/app_path.so" \
  --label local_budget_replay

python3 budget_v1.10.0/integration/postflight/validate.py \
  --assembly budget_v1.10.0/integration/assemblies/local_budget_assembly \
  --run budget_v1.10.0/integration/runs/local_budget_replay \
  --reviewed-helpers budget_v1.10.0/reviews/reviewed_helpers.json
```

Fresh labels are required; attempts cannot overwrite prior evidence. The source assembly verifies the inherited formal receipt and every inherited source byte, then adds the frozen budget modules and controls. The verifier starts with an empty project object directory and compiles all 151 project targets with warnings as errors and automatic implicit variables disabled. It also runs all 30 control files and audits the project declarations and their axiom dependencies. Exact counts and timings from the accepted run are in `VERIFICATION_SUMMARY.json`.

Compiled objects and the runtime itself are omitted from this handoff. The original terminal postflight records the original run; to repeat its disk-identity checks elsewhere, first run the source replay above and validate that new run. Historical absolute paths in old receipts are provenance, not installation requirements.

## Evidence limits

The formal trust base includes Lean's compiler/kernel, `propext`, `Classical.choice`, `Quot.sound`, and the pinned external compiled dependencies. This release recompiles all project sources; it does not rebuild all dependencies from source or perform an independent kernel check. Runtime and external-cache files are hashed before and after replay, and their source revisions and tracked clean state are checked at both ends. Endpoint equality cannot rule out a transient change restored between checks.

The new theorem and printed-proof audits cover WR03–WR05 and their stated dependencies. They do not certify every illustrative sentence, numerical program, or application in the monograph. Historical visual and Lean guides remain identified as historical editions. `SHA256SUMS.txt` hashes every package payload file except itself; the packaging checks also compare preserved predecessor files directly with the hash-pinned v1.9.0 archive.
