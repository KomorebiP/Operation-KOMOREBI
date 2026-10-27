# Paper IX final release 1.0.0

Komorebi P. | 20 October 2026

Euler Congruences: Completion, Factorial Strengthening, and Sharp Dyadic Geometry

Closed within the accepted publication scope. The October 10 mathematical sources are retained. The 22 unresolved historical references are now real recovered entries with authenticated identities. All 14 original historical vector figures and their source package are recovered and archived unchanged. Current corrected reconstructions remain explicitly labeled.

| Reader | PDF | Pages |
|---|---|---:|
| Traditional monograph | publication/pdfs/Paper_IX_Euler_Main_Final.pdf |232|
| Visual guide | publication/pdfs/Paper_IX_Euler_Visual_Guide_Final.pdf |25|
| Lean and evidence guide | publication/pdfs/Paper_IX_Euler_Lean_Guide_Final.pdf |139|

The 396-page set is mirrored in output/pdf/. All pages were reviewed in contact sheets, with 47 selected detail pages. The new reader set is built from the supplied source. Rebuilds match per-page text and pagination and differ only in generated PDF trailer IDs. This is not unqualified byte identity. Earlier frozen PDF mismatches and a corrected bibliography formatter failure remain recorded.

## Verification

```text
python3 -B verify_release.py --report /absolute/path/outside/release.json
python3 -B preflight_pdfs.py --output /absolute/path/outside/preflight.json
python3 -B scripts/verify_integrity.py --strict
python3 -B scripts/test_integrity.py --evidence /absolute/path/outside/controls.json
python3 -B replay_checks.py --output /absolute/path/outside/new_replay --jobs 1
python3 -B scripts/replay_finite.py --output verification/new_finite_run
python3 -B rebuild_pdfs.py --work-dir /absolute/path/outside/new_pdf_build
```

The strict verifier checks complete file membership, canonical paths, sizes and SHA256, with 21 passing control methods. The last finite command creates bounded v2 manifests in a disposable source copy; run it in a writable disposable extraction with a new relative evidence path. The lightweight replay_checks.py instead writes its receipts outside the release. Neither downloads dependencies or runs Lean. NumPy and Matplotlib are required for the finite figure suite. PDF reproduction requires the installed engines and fonts in FONT_DEPENDENCIES.txt and PyMuPDF. No dependency cache or standalone font binaries are supplied.

Nine fresh bounded arithmetic/source gates passed. See verification/2026-10-20/finite/. These gates overlap and have different units; their totals are not added as independent theorem counts. The dyadic 512 run uses 4096-bit modular precision and difference order through 128, with separately recorded exact rational checks. Failed stronger equality candidates remain recorded as failures.

## Mathematical and formal scope

Inherited formal evidence covers the external Nishibuchi capstone and the individually identified arithmetic, dyadic and lifting results. Current source/log reconciliation checks 15 inherited frontiers, 644 source hashes, 713 recorded log hashes and 202 source links. No fresh Lean or Lake compiler ran. The expanded factorial, mixed-step, all-rank and radius results retain written proofs, internal audits and bounded checks; they are not newly compiled Lean endpoints.

All 201 mathematical environment bodies and 153 proof bodies across 108 current source TeX files are preserved. Those overlapping counts are not independent new theorem or formal-coverage totals. The historical chapter retains its narrower proof qualifications, including Amice analytic pullback/depleted branches, finite-field modal minimality and unrestricted infinite polyphase statements. Bibliography identity checks are separate from verifying every source theorem or application.

General ordinary Euler-tail simplicity, remaining exact higher-difference classifications and the broad Native13.2/13.3 programs remain open. Their current quantifiers and restrictions are unchanged.

## Sources and history

sources/ contains editable current readers. preserved/ and figures/ retain all original selected-baseline bytes. recovered_history/ adds the exact earlier source archive, original bibliography witnesses, recovery inventory and primary metadata records. The 14 current reconstructed figures are not mislabeled as recovered original artwork. verification/2026-10-10/ and earlier audits remain dated history; current evidence is under verification/2026-10-20/.

## Licenses

MIT for original code, data, configuration, correspondence maps and machine-readable evidence. CC BY 4.0 for original papers, guides, figures, prose and editable sources. Original code listings also MIT. Third-party and font terms remain. Current grants supersede old restrictions on included original project material. See LICENSE.md, LICENSE_STATUS.json and adjacent PDF notices.

Progress and restart: PROGRESS_LEDGER_v1.0.0.txt. This closeout changes Paper IX only. The next technical hold is Paper X source/evidence recovery and production verification.
