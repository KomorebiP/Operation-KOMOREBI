# Verification protocol and observed evidence

The original Block63 archive was freshly extracted and replayed with its
complete declared selected predecessor chain. It passed in128.654021799 seconds.
The process log and full result are retained in verification/Block63_Replay.*.
No concurrent code imports wrote into that extraction.

The five new deterministic outputs are count281, independent_count281,
conductor64, independent_conductor64 and algebra64. They are regenerated from
source, with all conductor modes included in their full results. The inherited
fixtures have their own provenance checks. Point
counts cover11240 good pairs,285 degree-one classes,41 degree-two classes and
80 residual pairs. The independent counter checks every pair assignment and
all11240 smoothness gcds. It does not claim a direct degree-two count per pair.

The complete expanded finite sieve covers345600 normalized coefficient/vector
pairs after two justified rows. The separate implementation enumerates all7200
kernel vectors and evaluates every48-coefficient set by exact bit masks. Its
larger743 control covers5877504 pairs by122448 kernel vectors. These are exact
finite covers, not millions of independent global arithmetic tests. Both solver
methods agree on all stage counts and complete survivor lists.

The algebra program checks117649 coefficient triples,112896 distinct product
pairs, the twist identity and49 automatic13 cocycle values. It is one executable
check plus a written proof, not a claimed second independent algebra verifier.

verify.py checks the exact payload set, all hashes and13 named inherited files
inside two nested archives. It rebuilds every new expected output in a clean
scratch copy, compares complete JSON, and requires rejection of altered counts,
a twisted column, an invented exclusion survivor, a false polynomial pairing,
and a modified archive payload. Optional predecessor replay invokes the exact
frozen Block63 verifier and checks its precise PASS status.

Final ZIP execution, member-set/CRC/hash audit and wall-clock timings are recorded
OUTSIDE the immutable archive to avoid a self-referential hash claim. A final
external PASS record governs release acceptance. None of these tests is a new
Lean proof or an independent review of upstream analytical geometry.

Observed new-block development replay: PASS in11.818783 seconds,
including full regeneration and all five deliberate rejection tests. The final
fresh-extracted replay is recorded externally and also includes the predecessor.
