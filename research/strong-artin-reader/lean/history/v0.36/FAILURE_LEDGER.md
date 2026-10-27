# Failure ledger — v0.36

- The initial interactive runtime launch failed with StreamingExecNotEnabledContainerError.
  A local synchronous/polled execution restored the complete runtime; archive hash verified.
- Rejected proof drafts are recorded below. None was counted as evidence. They
  involved section-variable linting, a documentation comment placed before omit,
  an attempted import after its dependency had failed, Option.elim argument order,
  insufficient explicit unfolding, and a finite-ring normalization tactic that
  left a goal open. Final proofs passed with warnings as errors.

- `FiniteBranchCompactness` exit 1: `development/FiniteBranchCompactness_1789204733891417152.log`.
- `PadicFiniteBranch` exit 1: `development/PadicFiniteBranch_1789204848276535592.log`.
- `PersistentFinitePrefix` exit 1: `development/PersistentFinitePrefix_1789204904146165080.log`.
- `PersistentFinitePrefix` exit 1: `development/PersistentFinitePrefix_1789204972321500175.log`.
- `ResonantPadicRoots` exit 1: `development/ResonantPadicRoots_1789204974417008845.log`.
- `SimultaneousGaugeBranch` exit 1: `development/SimultaneousGaugeBranch_1789205085331467975.log`.
- `SimultaneousGaugeBranch` exit 1: `development/SimultaneousGaugeBranch_1789205107670342801.log`.
- `ResonantBranchControls` exit 1: `development/ResonantBranchControls_1789205258798812819.log`.

No false theorem was accepted or replaced by an axiom. No new numerical failure
is a purported counterexample to Strong Artin. See RESULT.json for final checks.
