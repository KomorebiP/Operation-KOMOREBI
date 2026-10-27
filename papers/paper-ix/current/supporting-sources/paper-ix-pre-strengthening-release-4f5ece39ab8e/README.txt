Paper IX — final traditional, visual and Lean companions
Komorebi P. — 6 October 2026

Start with papers/Paper_IX_Traditional_Final.pdf. The separate visual guide
works through concrete examples; the Lean guide explains the formal proof
mechanisms and their hypotheses with exact source excerpts.

The traditional paper retains the current consolidated core, full continuation
derivations, eleven complete checkpoint supplements, native prose arguments,
and the recovered historical polyphase text. Historical chapters carry their
own provenance and explicit correction notices. Their preservation does not
certify every historical statement or external dependency.

All 4,650 extracted files from both authoritative recovered source packages
are retained byte for byte, together with the original downloaded archives.
The 2,278-file consolidated package matches the complete package's snapshot.
Original TeX for the separate 28-page manuscript, its figure generator and
full historical experiment package remain unrecovered. Fourteen figure assets
and the bibliography of the recovered polyphase text were not supplied.

Fresh exact arithmetic, written proof review, static source/log reconciliation,
inherited Lean compilation, and historical computations are distinct evidence.
No fresh Lean or Lake compilation, original SymPy run, hardware benchmark,
infinite p-adic numerical construction, or unrestricted native descent is claimed.
Open research questions are explicitly retained in the paper and guides.

Editable sources and portable PDF builders are under editable/. From this
edition root, with the same TeX/Python dependencies used for the edition:

    python3 scripts/build_pdfs.py --check-only --report /tmp/paper_ix_build.json
    python3 scripts/verify_integrity.py
    python3 scripts/validate_evidence.py --report /tmp/paper_ix_evidence.json
    python3 scripts/preflight_pdfs.py --root . --out /tmp/paper_ix_preflight

The document checks accept --roles traditional visual_guide lean_guide to
select a subset. Check-only rebuilding requires identical PDF bytes and text.
The build scripts do not install dependencies. Computation contracts, exact
tested ranges, scripts, outputs and manifests are preserved in verification/.
The file manifest establishes package consistency, not an authenticity signature.
Evidence validation maps the packaged editable folders to their recorded paths
in a temporary validation root and verifies the unchanged input/output bytes.
Superseded or stale-input predecessors are retained with separate status notes.

EDITION.json records final scope and counts; COMPANION_MAP.json records
navigation; CORRECTIONS_AND_SCOPE.txt lists material repairs and limitations.
Papers I–VIII remain closed and unchanged. Papers X–XII remain frozen.
