# Verification scope and observed development execution

Block75 default replay passed before development in11.242384 seconds. This was
not a new full historical-chain replay. Its report is preserved unchanged.

The recorded new primary and separate science runs passed in1.469625 and2.016294
seconds, with combined elapsed3.485947 seconds. SCIENCE_RUN.json preserves exact
argv, timestamps, stdout and exit status. COMPUTATION_MANIFEST.json pins execution
input hashes before and after and complete scientific output hashes. This is a
project-local legacy schema-v1 record, not a claim to have run the installed
plugin's full schema-v2 bounded runner. No CPU or memory cap is claimed; scientific
subprocesses have a120-second wall timeout. Timeouts are inconclusive.

verify.py regenerates both expected scientific files in a fresh scratch copy. It
requires complete output equality and runs the separate checker against eight
corrupted certificates using ONE freshly recomputed independent result, not eight
repeated expensive arithmetic runs. It separately tests a modified payload.
The two programs do not import one another's arithmetic. Their independent
finite calculations do not prove the universal Galois or closed-group statements.

The final immutable ZIP is extracted anew and verified, optionally with one
immediate Block75 DEFAULT run. External final verification/audit records supply
that actual runtime, counts and archive SHA256; these are not included inside the
immutable ZIP to avoid self-referential hashes. Preservation of nested predecessor
archives is not a fresh execution of their full historical chain.

No new point counts, Lean compilation, independent mathematical reviewer,
labelled Galois map, actual uniformizer mixed trace or pattern exclusion.
