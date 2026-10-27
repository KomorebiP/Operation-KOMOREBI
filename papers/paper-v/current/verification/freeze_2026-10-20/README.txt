All 1,519 files in the accepted release are preserved byte for byte. Only the
root manifest moves to before/; the current manifest uses the same strict schema
and includes every freeze addition. Every original-to-preserved mapping is in
BASELINE_PRESERVATION.json. The two existing verifier scripts are unchanged.

The accepted twenty-one integrity controls are bound to the exact current
verifier and harness hashes. They are authenticated inherited tooling evidence,
not newly executed controls. This freeze performs separate positive full-tree,
source/evidence and clean-extraction checks. The seventeen historical missing
artifacts remain inventoried; they are not newly missing current source files.

The baseline audit script targets the original unmodified tree. Reconstruct
its original manifest from before/ in a separate working copy if reproducing
that baseline-only event. No Lean, finite experiments, TeX rebuild or whole-paper
proof audit was performed for this freeze.
