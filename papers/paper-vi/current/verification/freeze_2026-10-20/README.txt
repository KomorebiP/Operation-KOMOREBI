All 2,136 files in the accepted release are preserved byte for byte. The old
root manifest and checksum list move to before/; the current indexes cover all
freeze additions without a self-referential hash cycle. Every original-to-
preserved mapping is in BASELINE_PRESERVATION.json. The two existing verifier
scripts, mathematical/scientific source, readers, evidence and licenses remain
unchanged at their original paths.

The accepted twenty-one integrity controls are bound to the exact current
verifier and harness hashes. They are inherited tooling evidence, not newly
executed controls. Fresh positive checks cover the complete file set, static
source, recorded evidence and clean extraction. No Lean, finite experiments,
control suites, TeX rebuild or whole-paper proof audit occurs in this freeze.

The baseline and reader audit scripts target the original unmodified tree.
Their preserved reports identify those read-only events. Reconstruct the two
old indexes from before/ in a separate working copy for a baseline-only replay.
Original IX/X restart pointers are historical. Next sequential freeze: VII.
