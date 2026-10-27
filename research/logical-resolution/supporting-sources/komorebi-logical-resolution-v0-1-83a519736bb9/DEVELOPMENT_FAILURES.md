# Failures and corrections retained

No failure below is counted as proof success.

## Environment and retrieval

- One unused Files read used a mistyped reference and failed to resolve. The
  authoritative v0.4 coverage note was read successfully; actual source came from
  the mounted, hash-checked archive rather than that failed lookup.
- Direct container access to GitHub failed DNS resolution. The existing user-supplied
  five-part portable Lean archive was then materialized through Files.
- An initial restoration probe attempted to import the unavailable `zstandard`
  Python package. Inspection of the real archive header showed it is xz; restoration
  used Python's standard `tarfile`/`lzma` support instead.
- A streaming-session container request was unsupported and did not execute its
  setup command. An immediate run consequently found no script/directory. The setup
  was executed synchronously, then the actual toolchain was restored successfully.
  `evidence/RUNTIME_RESTORE.log` records the completed restoration. Earlier environment
  errors are summarized from current-turn tool outputs, not mislabelled as saved raw
  logs.
- Some broad web search results were irrelevant and one documentation endpoint
  failed. Only the successfully opened official Mathlib syntax/type pages are used
  as terminology references. No web result supplies an unproved mathematical premise.

## Lean development

- `LogicalHorizon_attempt01.log`: an unavailable `List.length_eq_zero.mp` name.
  Replaced by explicit list cases and natural arithmetic.
- `SemanticBoundaries_attempt01.log`: automatic decidability was unavailable for
  the existential Bool/Unit cardinality expression. Replaced by explicit witnesses
  and the Unit subsingleton proof.
- `StreamBoundary_attempt01.log`: an unnecessary tactic after the goal was solved,
  and a zero-add simplification that is propositional rather than definitional.
  Both were corrected in the next attempt.
- `ConcreteLogical_attempt01.log`: the finite evaluator proposition did not expose
  a decidability instance before unfolding. Its exact Boolean-equality expression
  was exposed with `change`, then checked by ordinary `decide`.

All accepted modules pass the final cold warnings-as-errors build. No placeholder
or additional axiom was introduced to repair these errors. The deliberate negative
controls remain outside the library and reject as intended.

## Computation

Both completed finite Python runs passed; no mathematical audit mismatch occurred.
Finite checks are not promoted to universal results. Universal conclusions come
from the named Lean statements and retain their stated fragment restrictions.
