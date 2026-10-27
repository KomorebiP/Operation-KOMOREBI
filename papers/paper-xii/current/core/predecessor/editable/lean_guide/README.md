# Paper XII: Final Lean Guide

Komorebi P. — 2026-10-06

Read `Paper_XII_Lean_Guide_Final.pdf` for a standalone account of the completed tensor and global base-change constructions, ordinary and derived support, intrinsic Fitting ideals, packets, occupancy, adic class completion and conditional automorphic realization. The guide supplies exact mathematical hypotheses, a full 96-module catalog and a revised/original claim crosswalk. The production source is complete and unchanged.

## Evidence boundary

The preserved September 12, 2026 kernel records report all 96 production modules built, 1,229 public named declarations axiom-audited, and three invalid controls rejected. Independent finalization checks reconcile the actual source hashes, declaration set, 113 direct internal import edges and all 291 distinct targets in the 49 revised claim records. The 829 public theorem declarations divide into 748 own and 81 reused from Paper X. Two reuse files under the PaperXII directory retain Paper X namespaces; classification by directory alone would give the wrong originality counts. One private helper is outside the public count.

No fresh Lean compilation was available during this finalization. The finalization source/provenance audits and new PDF builds are separate from inherited successful compiler records. The revised contract remains 49 complete; original wording remains 41 complete, seven partial and one unchecked. The original unchecked statement is 6.12; 10.5 is original-partial. Eight inherited amendments remain distinct from final editorial clarification of local point hypotheses, the upper Fitting-index boundary, Frobenius agreement and arithmetic conventions.

Core `FinalClaimsConsumer.lean` has three supplementary interface tests. The native v0.17.1 `ManuscriptContractReplay.lean` has a separate three tests; its report and source are retained under `native_contract_evidence`. Neither consumer increases the production census or numbered claim census.

## Included files

- `formal_release/lean/`: all 96 production source modules, including Paper X reuse.
- `formal_release/checks/`: exact manifest, cumulative verifier, supplemental verifier/consumer and three invalid controls.
- `formal_release/logs/`: inherited compiler, axiom, consumer and control logs.
- `formal_release/*.json`: inherited coverage, claim roadmap, verification and preservation records. Required predecessor inventories remain in `formal_release/upstream/`.
- `data/`: full hashes, source catalog, qualified declaration CSV/JSON, direct import CSV/JSON, claim crosswalk CSV/JSON, final environment and source census audits.
- `excerpts/`: 24 complete byte-identical core source modules with all ambient hypotheses, plus display copies. `INDEX.json` records full hashes and the eleven typography substitutions used only in the PDF.
- `fonts/`: bundled relative font files and license notices.
- `native_contract_evidence/`: separately preserved native cumulative/contract records, exact contract source, log and mathematical review.
- `build.py`: fresh-directory portable document builder.
- `make_audit.py`: source-census/data generator used by finalization; it expects the adjacent authoritative source snapshot and is not needed to rebuild the supplied guide PDF.

**Markdown (.md) files are included**, including this README, `SCOPE_AND_AUDIT.md` and the preserved release notes. They are ordinary plain-text documents readable without TeX or Lean. Exact sources and complete logs are supplied outside the PDF so readers can inspect full proof context.

## Build the guide PDF

Prerequisites: Python 3.10+, TeX Live with XeLaTeX, fontspec, unicode-math, fvextra, microtype, booktabs, longtable, fancyhdr and hyperref, plus Poppler `pdfinfo`, `pdftotext` and `pdffonts`. All selected text, math and code fonts use bundled relative paths. The finalization engine was XeTeX 0.999995 / TeX Live 2023 Debian; `build.py` reports its actual engine version.

```bash
python3 build.py --output-dir /absolute/path/to/fresh-output
```

The destination must be empty. The builder stages its relative inputs there, fixes the date, epoch and PDF trailer identifier, runs three passes and checks glyphs, references, overfull boxes, text anchors and font embedding. `BUILD_AUDIT.json` records PDF/text/source hashes and page count. Exact byte equality is verified by building in isolated fresh directories under the same engine and dependencies; portability does not promise byte-identical PDFs across unrelated TeX versions.

## Replay the production Lean proofs

Use a **writable extracted copy**, because replay cleans `build/`, `logs/` and regenerates the current reports. Preserve the inherited logs/reports before replay.

The separate Linux/WSL portable runtime must supply `toolchain/bin/lean` and a `workspace/` containing the pinned dependency source and matching cached objects. This package does not supply the runtime or dependency cache. Native Windows behavior is not claimed.

- Lean: `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Compiler SHA-256: `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`.
- Mathlib commit: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- One thread, warnings as errors, 180-second default per-process timeout.
- Allowed transitive axioms: `propext`, `Classical.choice`, `Quot.sound`.

Check the exact compiler hash/commit and all dependency HEADs against the runtime's dependency pin records before replay. The inherited verifier checks a version substring plus Mathlib HEAD and manifest, so a reader should perform the stronger exact preflight separately. The inherited scripts set `MALLOC_ARENA_MAX=2` and `-j1` but do **not** enforce a resource limit themselves; enforce the reported 4 GiB address-space limit in the caller on Linux/WSL:

```bash
cd formal_release
sha256sum /path/to/Komorebi_Portable_Lean_4.34.0-rc2/toolchain/bin/lean
ulimit -v 4194304
bash Run-Reverified.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The wrapper cleans and compiles every registered source in dependency order, axiom-audits named declarations, rejects the three invalid controls, and runs the three core supplementary tests against the exact successful fresh objects. Cached pinned Mathlib is not rebuilt. No timeout or failed elaboration is counted as success. A completed result must have `status: PASS`; `RUNNING` is an intermediate resumable state.

The arithmetic inputs listed in the guide remain external. Proof replay does not establish representability of arbitrary local conditions, residual occupancy, applicability of arithmetic patching/classicality/attachment theorems, universal companions or unrestricted reciprocity.
