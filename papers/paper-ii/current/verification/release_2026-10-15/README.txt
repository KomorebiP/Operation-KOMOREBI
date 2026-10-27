PAPER II — RELEASE EVIDENCE, 2026-10-15

This directory contains 1561 byte-for-byte evidence copies (29924328 payload bytes).
EVIDENCE_INDEX.json maps each original absolute source path and workspace-relative
path to its packaged path, byte size and SHA-256. The index is an evidence-copy
index, not a proof-coverage certificate or release gate/status declaration.
Failed development and negative-control receipts are deliberately retained.

HISTORICAL LOCATIONS
The original workspace was /workspace/scratch/9f53d520971c.
Absolute paths inside original receipts, logs, scripts and reports are historical
provenance. Their bytes have not been rewritten to simulate a new execution.
Use EVIDENCE_INDEX.json to locate an included original source in this directory.
A referenced path may identify an intentionally omitted compiler object, external
runtime/dependency source, recovered input archive, or other external input.

LAYOUT AND REPLAY
Workspace-relative paths are preserved, notably paper2_work/tools/ alongside
paper2_work/baseline_compile/, paper2_work/final_audit/ and the branch check trees.
The sibling replay_current.py dependency of check_module.py is included. The
final-audit helper directory, fixtures, runtime bindings and helper reviews are
also included. All tools are preserved as executed, including any historical
absolute defaults; inspect and explicitly adapt those locations for relocation.
The production sources remain elsewhere in the release at formal/current.
Compiler/dependency runtimes and .olean/.ilean objects are deliberately omitted.
A fresh replay needs the pinned external runtime and newly rebuilt objects; these
copies alone do not constitute a ready-to-run compiler environment. Existing
recorded PASS results do not certify a subsequent replay or a broader claim.

EXCLUSIONS AND SCOPE
No runtime, imported/recovered archive, library transfer material, object tree,
bytecode, preview/image cache or publication PDF is included. This helper does
not alter production sources/publications, create an archive or root manifest,
or decide the final replay/correspondence/visual-QA gates. The release owner runs
it only after accepting those separate gates.

INDEX INTEGRITY
Every copied file appears in files with a SHA-256. This generated README appears
in generated_files with its SHA-256. The index cannot contain its own checksum;
the final release's separate integrity mechanism may cover it after packaging.
