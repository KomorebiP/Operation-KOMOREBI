# Reproduction and evidence

Run with Python3 (standard library only) from the package root:

    python -B verify.py --replay-predecessors --report ../Block67_Replay.json

The report must be outside the immutable package. Bytecode writes are disabled
for every subprocess. No network, random seed, Sage, NumPy or Lean is required
by production replay. The default per-job wall limit is1200 seconds and can
be raised explicitly with--job-timeout. A timeout returns INCONCLUSIVE_TIMEOUT,
never success. A failing check returnsFAIL.

The verifier checks the exact member set and all payload hashes,17 named inherited
source leaves across14 archive levels, and the byte-identical immediate candidate
certificate. It then copies to a fresh scratch directory, deletes the eight
expected output JSON files, reruns all eight programs, and compares the complete
regenerated JSONs. It requires specific diagnostic rejection of nine altered
inputs, including point counts, polynomial pairs, shallow and minus controls,
and a modified package payload. Optional predecessor replay is cleanly extracted
and runs the declared full selected chain, not just its retained success flag.

Every scientific output stored here has actually been generated. The final
fresh-extracted run and ZIP audit are recorded outside the archive, with elapsed
times and process exits. This document is not itself a substitute for those
execution records. The initial observed predecessor replay is included under
verification/Block66_Replay_for67.*.

The unbounded mathematical claims depend on written proofs and the explicit
upstream arithmetic inputs. Finite enumeration, checksum success and exit0
cannot certify those inputs or prove Beal by themselves.
