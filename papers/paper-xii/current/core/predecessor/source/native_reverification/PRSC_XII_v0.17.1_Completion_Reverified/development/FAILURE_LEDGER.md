# Development failures and corrections

The preserved per-module development journal has 58 attempts: 37 unsuccessful elaborations
and 21 successful compilations, with no per-process timeouts in that journal. Failed draft
sources and raw compiler logs are retained. The final production source tree contains no
unfinished proofs. The cumulative certificate is a separate clean run of the frozen sources.

The corrected failures concerned explicit quotient-topology and adic carrier coercions,
instance synthesis, equality directions, exact theorem argument order, and unused section
variables rejected by warning-as-error. The global quotient proof required explicit types
to prevent Lean from inferring the adic carrier topology at the wrong ring.

Three larger cumulative wrapper calls exceeded the container execution window while the
report was RUNNING. Smaller calls resumed only after verifying source hashes and all
retained fresh object hashes. Interrupted modules were rebuilt. A wrapper timeout was
never reported as a successful Lean proof.

The first declaration census classified reuse by module-name prefix. This missed 18 reused
Paper X theorems housed in PaperXII reuse modules. The census now preserves the authoritative
per-declaration reuse flags: 748 own and 81 reused. No proof source or object changed in
that correction. The pre-correction verifier is preserved for provenance.

The initial manuscript build could not invoke the broken system `bibtex` link, so citations
remained unresolved. The installed `bibtex.original` binary produced the bibliography, and
two subsequent LaTeX passes resolved the references. The final PDF has no undefined-reference
or citation warnings and no overfull boxes. The supplied matching `.bbl` is included.

The coverage validator rejected a guessed separate inverse-continuity target name. The
actual theorem proves both continuity directions in a conjunction; the coverage map now
uses that real audited target. No claim was finalized using the nonexistent name.
