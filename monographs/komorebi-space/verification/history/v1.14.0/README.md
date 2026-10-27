# Verification scope

`EDITION_VERIFICATION.json` records this edition's source identities, exact environment, formal coverage, integrated build, and PDF identities. `LEAN_THEOREM_MAP.json` gives selected declarations discussed in the Lean guide. Explicit theorem/lemma declarations and the larger exported declaration environment are counted separately.

The current formal source combines the parent development with the accepted infinite diagonal completion. All mathematical Lean source files match their accepted source bytes. Only package version metadata and usage documentation change during publication integration.

## Accepted evidence

The parent verification covered 153 production modules and three entrypoints, 5,048 exported declarations, and 44 controls. Its detailed command receipts, original controls, and source audit are retained in the separate Technical Record. `history/` preserves the preceding edition's publication and editorial records with their original identities and scope.

`DIAGONAL_ACCEPTED_EVIDENCE.zip` is the exact standalone source-and-evidence package for the three completed diagonal results. It includes the actual infinite Hilbert model, all new source files, strict compilation records, the full 273-declaration axiom inventory, eight targeted controls, independent statement audits, failed proof attempts, and reproduction instructions. Unpack it into its own directory before following those instructions. Paths inside its records are relative to that accepted package, not this verification directory.

`DIAGONAL_COMPLETION.json` and `DIAGONAL_DECLARATIONS.json` are unchanged copies of the completion summary and declaration inventory from that archive. Their source paths are interpreted in the archive's root. The same Lean proof files are present in this edition's top-level `lean/` directory.

## This edition's review

The files in `current/` preserve their original working-directory paths as provenance. `EDITION_VERIFICATION.json` lists the packaged copies and their hashes under `current_reviews`; the Technical Record retains the corresponding integration directory layout. A path recorded inside a copied review is interpreted in that original layout, rather than relative to `current/`.

The integrated build checks the publication's two default Lean import targets together. It does not replay the historical 44 controls. The diagonal controls retain their own eight-outcome scope. Neither the summed declaration count nor successful compilation implies that every monograph sentence or finite plotted example has a distinct Lean counterpart.

`MONOGRAPH_PROOFREAD_REVIEW.json` records the coverage-text edits and their review. Mathematical statements and printed proofs are preserved. The new formal asymptotic proof follows a different valid integral-comparison route, documented in the Lean guide.

`VISUAL_GUIDE_REVIEW.json` records the current guide's build and visual review, with explicit links to the historical checks of its unchanged figures. The files in `visual/` retain those model checks: 52 generator checks include typography, and 23 independent checks concern the declared models. They are finite computational evidence. The current title update does not turn them into new proof checks.

The trusted environment includes Lean 4.34.0-rc2, its kernel, the recorded three standard axioms, and pinned external dependencies. The diagonal record discloses the host-specific executable-path compatibility shim and the checks establishing unchanged official Lean binaries. An ordinary matching host can use the native reproduction path without that shim.
