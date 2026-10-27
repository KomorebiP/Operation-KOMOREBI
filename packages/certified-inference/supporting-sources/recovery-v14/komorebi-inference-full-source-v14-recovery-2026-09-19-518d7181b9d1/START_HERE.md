# Komorebi inference: full v14 project source recovery

Author: Komorebi P.
Recovery date: 2026-09-19

The complete v14 project archive has been recovered. Its SHA-256 matches the
recorded original exactly:

    fb5f7666b3e511fff384e16f1ea3b5f15d7ceed594b0c8dfe69afb3acde01632

The original directory below is preserved byte for byte, including all 4,568 files:

    Komorebi_Unified_Inference_Stochastic_Bayesian_CONTINUATION_v14_2026-09-12/

It contains 1,765 Lean files, 104 Python files, 138 Markdown files, two LaTeX files,
one PDF and 32 nested ZIPs. These counts include historical releases, repeated
sources and development attempts. They are not theorem counts. There are 303 unique
Lean file contents and 62 unique Python file contents by SHA-256.

## Start the project

Read the original root START_HERE.md, CONTINUE_HERE.md, AUDIT.json and PROTOCOL.md.
The active release is:

    CHECKED_RELEASES/FD_Certified_Inference_Core_v1.0.0_Checked/

Within that release, read README.md, RELEASE_SCOPE.md, PROOF_NOTE.md and
FINAL_VERIFICATION_RECEIPT.json. Its canonical Lean entry point is
Komorebi.CachedPosterior.runCached, in Komorebi/CachedPacketOutput.lean.
The Python producer is checks/cached_posterior.py, with examples and a Windows
PowerShell launcher in the active release.

The retained v14 records report 117 active modules and an audit of 543 theorem/lemma
declarations. Those are inherited proof-check records. This recovery verified
archive integrity, every original manifest entry, and byte-for-byte source
preservation. It did not rerun Lean or certify new mathematics.

## Important completeness boundaries

1. This is the full v14 inference project source archive. It is not a collection of
   every Komorebi project or all twelve foundational paper source distributions.
2. The September 13 standalone gap-closure extension was not recovered. It was
   not persistently saved when it was created, and the transient workspace was
   subsequently pruned by automated maintenance. Exact title searches for the
   extension ZIP, addendum and unique source names returned no matching saved
   records. LATER_EXTENSION_RECOVERY.json records the search. No later source or
   proof has been silently recreated from conversation summaries.
3. The portable Lean compiler, mathlib dependency payload and caches remain
   separately distributed, exactly as in v14. The original LEAN_RUNTIME_METADATA
   contains the assembler, checksums and reconstruction instructions for
   Lean_Compact_01.zip through Lean_Compact_05.zip (about 2.2 GB compressed total).
   This 40 MB source package is not a self-contained offline toolchain.
4. Cached selective iteration in v14 uses exact rational updates. The rounded
   full-update branch is separate. The later rounded selective proof discussion
   does not become a checked v14 theorem merely because the archive is recovered.

## Verify this package

Before adding or changing files, run from this directory:

    python verify_recovery.py

It checks every distributed file hash, complete manifest coverage, and the
unchanged original v14 manifest. It does not invoke Lean. The original runtime
restoration and clean-build commands are in the retained README files.

To continue formal work, recover the exact later extension ZIP if available, or
explicitly start a new reconstruction from its retained specification and this
verified v14 source. Keep that provenance distinct from recovery of original files.
