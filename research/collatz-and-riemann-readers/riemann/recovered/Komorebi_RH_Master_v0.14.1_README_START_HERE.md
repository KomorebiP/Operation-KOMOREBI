# Komorebi RH Master Archive — v0.14.1 count-corrected

**Archive date:** 2026-09-12  
**Author/release name:** Komorebi P.  
**Claim boundary:** The Riemann hypothesis is **not proved** in this archive.

This package consolidates the complete RH work currently available in the active
runtime: Lean source trees, original checkpoint ZIPs, Python computations,
Markdown reports, TeX manuscripts, PDFs, CSV/JSON data, verification manifests,
audit logs, visual assets, and continuation files.

## Open these first

1. `00_START_HERE/MASTER_SUMMARY.md`
2. `00_START_HERE/STATUS_MAP.csv`
3. `02_UNPACKED_SOURCE_TREES/Komorebi_RH_PrimeCubeParityBarrier_v0.14.0/CONTINUE_HERE.md`
4. `02_UNPACKED_SOURCE_TREES/Komorebi_RH_FinalGap_Attack_v0.13.0/FINAL_GAP_ATTACK_REPORT.md`
5. `02_UNPACKED_SOURCE_TREES/Komorebi_RH_Consolidated_Lean_v0.9.0/CLAIM_BOUNDARY.md`
6. `01_CORE_PAPERS_AND_SPECIAL_FUNCTIONS/Prime_Packet_RH_Heat_Kernel_Core.tex`
7. `01_CORE_PAPERS_AND_SPECIAL_FUNCTIONS/Prime_Packet_RH_Jordan_Flow_Core.tex`
8. `01_CORE_PAPERS_AND_SPECIAL_FUNCTIONS/Prime_Packet_RH_Hypercontractive_Deconvolution_Core.tex`
9. `01_CORE_PAPERS_AND_SPECIAL_FUNCTIONS/Prime_Packet_RH_Nonlinear_Renormalization_Core.tex`

## Directory map

- `00_START_HERE` — status map, master summary, inventory, continuation prompt.
- `01_CORE_PAPERS_AND_SPECIAL_FUNCTIONS` — core RH TeX/PDF manuscripts and the
  projector-generated special-functions source used in the Möbius-coherence route.
- `02_UNPACKED_SOURCE_TREES` — every unpacked RH source/research directory found.
- `03_ORIGINAL_CHECKPOINT_ARCHIVES` — original checkpoint ZIPs, preserved byte-for-byte.
- `04_TOP_LEVEL_AUDITS_AND_METADATA` — top-level logs, hashes, manifests, summaries,
  and standalone Lean files.
- `05_RECOVERED_RESEARCH_SOURCES` — recovered prime-toggle, masked-transport,
  and exploratory computation files.
- `06_VISUAL_ATLAS` — editable SVG figures, high-resolution PNGs, and the original atlas ZIP.
- `07_BUILD_AND_REPRODUCTION` — archive builder and dependency notes.
- `08_ALL_LEAN_EXPANDED_BY_CHECKPOINT` — all 377 cumulative Lean entries extracted from checkpoint ZIPs.
- `09_UNIQUE_LEAN_CONTENTS` — one visible file for each SHA-256-distinct Lean source content.

## Verification warning

Checkpoints have different certification states. In particular, v0.10 is marked
verification-failed/incomplete; v0.11 and v0.12 contain unverified Lean drafts.
The archive preserves those files for research continuity but does not promote them.
Consult each checkpoint's `CLAIM_BOUNDARY`, `STATUS_SUMMARY`, result file, audit,
and verification manifest.

## Excluded dependencies

The multi-gigabyte offline Lean/Mathlib cache parts were intentionally not embedded.
They are dependencies rather than RH source work. Project sources, pin information,
checkpoint archives, and the small Lean-kit start README are included.

## Lean source count correction

The prior archive summary's **54** count referred only to already-expanded outer
Lean files. This corrected archive exposes **377 cumulative checkpoint
entries** and **104 distinct Lean source contents**. See
`LEAN_SOURCE_COUNTS.md` and the two provenance CSV files.
