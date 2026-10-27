PAPER VIII — FINAL THREE-COMPANION EDITION
Komorebi P. | 2026-10-06
Packet Operator Algorithms, Exact Compilation, and GPU Realization

Read the three PDFs in papers/:
  Paper_VIII_Traditional_Final.pdf
  Paper_VIII_Visual_Guide_Final.pdf
  Paper_VIII_Lean_Guide_Final.pdf

The traditional paper integrates the complete strengthened manuscript and the
substantive mathematical contents of all six completion supplements. Active
statements include their accumulated hypotheses. Historical proof counts and
pending-status reports in preserved raw material describe their original dates.
The visual guide teaches the constructions with editable vector figures and
worked finite examples. The Lean guide explains actual source declarations,
proof steps, dependencies, and replay, with complete source and result catalogs.

Navigation and exact counts are in EDITION.json, COMPANION_MAP.json, and the
JSON crosswalks under editable/. CORRECTIONS_AND_SCOPE.txt and audit/ identify
the mathematical, empirical, and reference qualifications in this final copy.

The inherited v0.6.0 record covers all 56 registered manuscript-proved finite
items under their individual hypotheses. It records 392 theorem declarations
across 40 modules (373 Paper VIII and 19 reused foundation), plus 66 separately
audited constructions. Four classical inputs are tracked separately. General
SVD existence, a numerical QR/SVD algorithm, canonical singular-values API
identification, and verification of CUDA kernels are outside that formal scope.
The current edition does not claim a fresh Lean compiler run or GPU timing run.

Both supplied ZIPs and all 1,062 extracted source files are retained unchanged
under downloads/ and source/. The complete source includes historical failed
development attempts and diagnostics, kept separate from accepted evidence.
Fresh available checks, unavailable gates, their commands, arithmetic domains,
inputs, outputs, and tolerances are recorded under verification/. A passing
finite numerical example is not a universal proof or hardware measurement.

Rebuild with an installed TeX distribution and the Python dependencies described
in editable/*/README.md. From the extracted edition root:
  python3 scripts/build_pdfs.py --check-only --report /path/outside/edition/build.json
  python3 scripts/verify_integrity.py
The PDF builder works in temporary copies and checks the shipped output.
Lean replay needs the separately supplied pinned portable kit, Lean 4.34.0-rc2
and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06; neither is bundled.
Follow source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix/
original_snapshot/README.md for the original compiler procedure.

The manifest verifies file consistency, not independent authenticity. Write
replay outputs outside the edition so they do not alter its sealed file set.
Papers I–VII remain closed and unchanged. Papers IX–XII remain frozen.
