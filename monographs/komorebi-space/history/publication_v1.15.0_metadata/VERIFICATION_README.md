# Verification record

Publication edition 1.15.0 has passed a fresh integrated Lean replay: 166 targets,
5,339 exported project declarations, and 56 diagnostic controls.
The controls gave 18 expected acceptances, 35 intended elaboration rejections, and
three axiom-policy rejections. The 1,859 explicit theorem/lemma count is a source
count; the declaration inventory also includes definitions and generated helpers.

`EDITION_VERIFICATION.json` binds the current books, sources, and reviews.
`current/INTEGRATED_REPLAY.json` records the fresh commands and outcomes.
`current/DECLARATIONS.json` is the complete project inventory, with defining
module, declaration kind, safety status, and recursive axiom dependencies.
`LEAN_THEOREM_MAP.json` identifies 114 selected reader-facing declarations; its
names, modules, kinds, source hashes, and source lines were matched to that
inventory. Independent reviews of both new mathematical statements and the
portable runner are included in `current/`.

Run the complete check using the instructions in [runner/README.md](runner/README.md).
No previous project object files are used by a fresh run. The installed external
dependency caches are byte-recorded at both endpoints; they are trusted inputs,
not rebuilt or independently authenticated by the procedure. Endpoint checks
cannot exclude a transient change restored before the last snapshot.

The two additions retain the measured-data normal residual and rounded schedule,
and construct the actual diagonal unit witnesses and a datum in the range closure
without a preimage. Compiler acceptance and statement correspondence are separate
checks. Neither asserts a formal counterpart for every line of the books.

The 29 monograph chapter files preserve all 192 previous formal environments and 512
bracketed displays. Book build, structural, page-comparison, visual-review, and
worked-example records are in `current/`. The exact rational example is explained
in [WORKED_EXAMPLE.md](../examples/WORKED_EXAMPLE.md).

`history/v1.14.0/` retains the previous publication's records. The `DIAGONAL_*`
files preserve the earlier diagonal evidence, and `visual/` preserves the checks
for unchanged visual examples. These historical records are not relabeled as
current runs. The Technical Record preserves the complete parent technical
archive, current failed proof attempts, raw fresh replay logs, source snapshots,
compiler/cache identities, editorial records, and book-build attempts.

`SHA256SUMS` in the package binds the canonical archive bytes. Standalone PDFs may
receive embedded Content Credentials when saved, changing their bytes. The
separate `Komorebi_Space_Delivery_Verification_v1.15.0.json` records the hashes and
text/raster comparison of the actual downloaded copies. This does not authenticate
the Content Credentials signature. Reuse status is stated in [REUSE.md](../REUSE.md).
