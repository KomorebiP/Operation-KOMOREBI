# AVOC v0.25.0 — exact scope and evidence boundaries

## Kernel-checked in the new block

1. Eager Boolean interpreter returns the specified semantics and exactly its AST node
   count as its defined visit count.
2. Exhaustive comparison over all eight three-Boolean inputs is sound and complete for
   program equivalence. A disagreeing input forces rejection.
3. Grammar length and node bounds, monotonic pools, and completeness for bounded height.
4. Synthesis preserves semantics, does not increase node count, and selects a minimum
   among equivalent examined candidates plus the incumbent. Changed candidates originate
   in the generated pool. Full-pool hypotheses imply the bounded-grammar comparison.
5. Declared generation/trial charges obey credit and trial limits; unfunded generation
   does not enumerate the pool.
6. The actual shared-pool executable search has the stated result and accounting.
7. Generated programs instantiate the inherited sound upgrade authority and prepaid
   journal; complete search plus evaluation plus switch charges stay within total credit.
8. Replayed generated-program journals preserve the active semantic contract. Campaign
   net bounds include search costs and the stated initial-identity assumption.
9. Under the existing NoRevival condition, generated/promoted three-flag programs preserve
   the retry controller's action for every model, state and horizon.
10. Concrete pair synthesis, promotion, positive net and negative-net examples kernel check.

## Independently executed and tested

The actual Lean entrypoint is run by a bounded Python wrapper. A new SQLite campaign
reserves credit before search, publishes checked results and active AST together, and
replays the generated journal before invocation. Final evidence includes 747 exact
campaign comparisons, 255 equivalence comparisons, 5,976 per-input executions, ten
invalid wire requests and sixteen real-file/SQLite/Lean-process cases. Interruption
fixtures are controlled Python exceptions and transaction rollbacks, NOT SIGKILL or
power-failure tests. Older process-crash test records remain historical.

## Assumptions and exclusions

- **Language.** Three Boolean inputs and fixed total constructors only. Generated ASTs
  are data interpreted by trusted code, not arbitrary Lean, Python, machine code, tactics,
  plugin installation, effectful calls or open-ended scientific hypotheses.
- **Search scope.** Runtime depth is at most 2 and the trial prefix at most 21,845.
  Partial-budget search optimizes only its examined prefix plus the incumbent. Full
  bounded-grammar search does not prove unbounded program optimality or efficient search.
  Later grammar layers retain duplicates, which are charged rather than silently removed.
- **Generator.** Primitive grammar/operators and search ordering are fixed by us. No LLM
  proposes a candidate here. The actual expression tree is enumerated, not passed as a
  named replacement; that is not a new Boolean-identity discovery or recursive improvement
  of the proposer. No frozen-versus-upgraded proposer experiment was performed.
- **Costs.** Eager AST visits are exact for `runCount`; they are not exact costs of every
  path in `run` or of the machine. Generation is a protected pool-entry tariff and trial
  checking uses conservative eager-visit tariffs. List operations, allocations, syntax
  comparisons, runtime startup, parsing, IO, hash checks, SQLite, replay and arithmetic
  complexity are not all priced. Deployment call counts are declared workloads, not
  measured demand. No physical speedup, optimal net search or general efficiency claim.
- **Promotion.** A valid smaller program can be promoted despite negative total campaign
  net. Every evaluated candidate remains charged. The authority and semantic reference
  are protected inputs. Its metric string alone is not a cryptographic task identifier.
- **Retry bridge.** NoRevival remains required; the flags are precomputed. The transformation
  preserves action selection only, not exact value reports or the cost of computing
  probabilities/resources. It does not outperform the existing native threshold by proof.
- **Durability.** One new protected local campaign, one writer, one search/promotion batch.
  SQLite/OS/host and faithful Python parsing/storage are trusted. No hostile rollback,
  general path-attack, remote attestation or universal Python/SQL refinement guarantee.
  Altering both protected history and its matching checkpoint is outside the model.
- **Incomplete work.** Unconfirmed search retains the full reserved envelope and blocks
  dispatch. Automatic retry/refund, multi-campaign recovery and charge-idempotent repeated
  search are not supplied. New run directories are required; old stores are not migrated.
- **Reopening.** Invoke validates replay and executes the active AST without regenerating
  candidates. Pure check/replay costs recur. Exact result hashes are integrity fingerprints,
  not authenticated external provenance or a proof that a hostile fabricated history ran.
- **Runtime.** Lean kernel/compiler/Std/JSON, pinned mathlib cache, Python, and physical
  machine remain trusted. No whole JSON round-trip or independent kernel proof is claimed.
- **Evidence.** The old library remains byte-identical at inherited non-audit sources.
  All current local modules were checked against pinned cached dependencies. External
  mathlib was not rebuilt from source. Synthetic models do not measure real AI usefulness.

## Release census

74 new theorem/lemma declarations; 1,310 total; 123 non-audit AVOC modules;
19,935 non-audit Lean source lines; 136 local compilation targets; 63 negative files.
Counts include helpers and concrete examples, not independent mathematical discoveries.
