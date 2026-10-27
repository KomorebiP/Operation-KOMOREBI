# Verification scope and observed development runs

The clean Block74 default verifier passed before development in 11.392 seconds.
Its report and log are preserved in this directory. It did not replay the entire
historical chain, and no such claim is made here.

The new recorded science runs completed with exit0:

- primary integral75.py: 0.819 seconds;
- separate independent75.py: 1.071 seconds;
- combined recorded execution: 1.891 seconds.

COMPUTATION_MANIFEST.json records actual input before/after SHA256 hashes, commands,
software version, exact coefficient domain, bounds, outputs, and nonclaims. This
is a project-local schema-v1 evidence record. verify.py validates the declared
fields and hashes; this is not a claim to have run the installed plugin's full
schema-v2 validator or bounded runner. No CPU/memory cap is claimed. Replayed
scientific subprocesses have a120-second wall timeout; predecessor default has180.
A timeout is inconclusive, never mathematical exclusion.

Production verify.py rebuilds both expected science files after deleting them in
a fresh scratch copy, compares full bytes, verifies eight immediate pinned source
copies, and requires rejection of eight intentionally altered certificates plus
one altered payload. The separate checker derives the whole finite certificate
using its own arithmetic before comparing. No cached success flag suffices.

The default command verifies this block only. --replay-predecessor adds exactly
one immediate Block74 DEFAULT run. The original ZIP contains all earlier history,
but preservation is not a fresh execution of that history.

The final immutable ZIP has a separate fresh-extraction execution report and archive
integrity audit, emitted outside the ZIP to avoid self-referential hashes. Consult
those records for observed final runtimes and payload counts, rather than treating
this development record as a final archive replay.

No new point counts, Lean proof, external independent mathematical review, actual
candidate C matrix, labelled mixed trace, or arithmetic realization is claimed.
