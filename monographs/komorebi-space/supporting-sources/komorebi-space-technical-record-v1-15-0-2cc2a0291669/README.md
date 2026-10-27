# Komorebi Space technical record, publication edition 1.15.0

The canonical publication ZIP is in `publication/`. The complete, byte-preserved
v1.14.0 technical record is in `history/`; it retains the earlier evidence chain.
`current/` contains this edition's source snapshots, proof attempts and compiler
logs, independent reviews, complete fresh replay receipt and declaration
inventory, compiler/cache identity inventory, book-build attempts, and editorial
records. Failed attempts are retained with their causes. Static checks and
development-cache builds are not represented as fresh integrated verification.

Fresh project object bytes are hashed in the receipt but omitted from this
archive, as are external compiler/dependency caches and reproducible page PNGs.
The public portable runner recreates project objects in an empty output directory.
Book PDFs, logs, text extractions, structural checks, and visual-review records
are retained. The final delivery receipt is separate because its saved-file
identities become available only after these archives have been created.

`host_environment/` discloses the external wrapper and narrow proc-self-exe
compatibility shim used on this host. Official Lean compiler files were not
patched. The portable runner itself does not require or install this adapter.
The full compiler, dependency-cache, and preload byte inventories are in the
fresh replay record. These are trusted runtime inputs, not independently
authenticated dependency rebuilds.

Technical work is complete. The owner has not chosen public reuse licenses.
`current/records/PROPOSED_REUSE_TERMS.json` is a concrete MIT-code / CC BY 4.0-text
proposal, not a license grant. The public `REUSE.md` states the current boundary.
