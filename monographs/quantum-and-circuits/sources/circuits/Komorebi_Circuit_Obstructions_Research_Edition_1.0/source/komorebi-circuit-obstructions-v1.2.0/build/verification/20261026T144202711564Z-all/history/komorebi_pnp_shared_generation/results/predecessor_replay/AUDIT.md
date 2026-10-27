# Audit

The sole immediate predecessor is pinned by archive SHA256 in the research note. All 25 sealed files are checked before and after the new runner. Both predecessor scientific outputs are replayed and compared as JSON, separately from mathematical validation.

The new Boolean checker uses integer truth tables and GF2 kernel elimination. Its small immunity values are checked by an independent enumeration of all supported nonzero truth tables. The restored circuit check uses both bit-parallel full truth tables and separate scalar evaluations. Controls and target wires are required to be distinct.

The graph checker constructs actual padded adjacency matrices and runs an independent exact maximum-clique search on every tested target. The closed-form bound table is not represented as a synthesis run. The hash compression theorem is an all-size probabilistic-method proof, not a Monte Carlo claim.

The first combined replay failed with `ModuleNotFoundError`: the isolated graph checker imports `degree` from its sibling restoration checker, which had not been copied into the isolated directory. The runner now copies and hashes both files. The failed runner, manifest, and log are preserved in `historical/`. This was a replay-packaging error, not a mathematical counterexample. The complete runner was rerun after correction. No finite assertion failed in the final new suites. During development the two-vertex padding control was simplified to use the same `s >= max(v,4)` rule as the general proof rather than adding isolated source vertices first; both constructions preserve the truth value. The final verifier implements the literal construction in the note.

An early predecessor-clique invocation supplied an unused `--out` argument to a script without argument parsing; it reproduced the identical sealed result in its existing directory. The final runner instead copies that unchanged checker to an isolated replay directory and confirms source hashes and original file hashes. No result from a failed or timed-out run is used. This did not change the predecessor bytes.

A PMC web page returned a browser challenge. Primary arXiv source text was used instead for algebraic-immunity terminology. No unverifiable source was promoted to a dependency.

Scope distinctions retained:
- classical NCT versus quantum or measurement-based gates;
- Toffoli count versus ordinary Boolean circuit size;
- input length in bits versus vertex count;
- max of one-sided support parameters versus minimum in two-sided cryptographic immunity;
- shared arithmetic circuit cost versus expanded monomial count;
- existence of compact semantic packets versus efficient construction/evaluation;
- exact finite controls versus formal universal verification;
- a stronger linear lower bound versus a superpolynomial separation.

Known-context boundary: multicontrol Toffoli count 2k-3 and one-sided algebraic immunity have established literature. No comprehensive novelty search, Lean proof, external review, or P-versus-NP resolution is claimed.
