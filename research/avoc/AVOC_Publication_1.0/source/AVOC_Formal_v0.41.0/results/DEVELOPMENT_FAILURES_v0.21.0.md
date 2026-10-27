# Development failures and corrections — v0.21.0

## Environment and recovery

The first terminal-session invocation was rejected by the execution environment
(`StreamingExecNotEnabledContainerError`). Runtime assembly was instead run through
a directly launched process and monitored to completion. All seven CRC/SHA part
checks and the combined archive hash passed; extraction returned normally.

The mounted files included the latest v0.20 archive but no active Lean runtime.
The archive was extracted to the new version directory. Its own 3,275 recorded
payload hashes and ZIP CRC passed. An early check on the already edited working
copy reported expected manifest mismatches; that is not counted as baseline
validation. The separately checked frozen ZIP is the baseline evidence.

## Lean proof scripts

1. Multiline record-update formatting caused parser errors. Record fields were
   put on consistent lines. Early failed elaboration logs contain Lean-generated
   error placeholders; the delivered source contains no such proof placeholders.
2. `if_pos` is deprecated in the pinned toolchain under warnings-as-errors. The
   proofs use `ite_eq_left` instead. Broad `simp` also rewrote record fields too
   aggressively; narrow simplification preserved the needed equalities.
3. Omega needed explicit record-projection reduction in two reservation bounds.
4. Case splitting in recovery contract proofs had already rewritten the goal;
   returning the old equality was incorrect. Reflexivity solved the reduced goal.
5. The exact source predicate is ArtifactWorkflow.SourceParsed, not Binding.SourceParsed.
6. A nested monadic parser return escaped the intended match; explicit `map` fixed it.
7. Concrete Except equalities had no inferred DecidableEq in the minimal imports.
   They were proved by kernel definitional reduction (`rfl`) instead, not native evaluation.

The final accounting, adapter, codec and examples all compile without warnings.

## Python and executable tests

Source review caught the known `executescript`/explicit-transaction initialization
pitfall before the first live run. Schema creation is outside the metadata
transaction. The initialized database and real normal workflow then passed.

The first `committed_not_retried` test exposed an exit/status mismatch: recovery
correctly acknowledged the committed verification without another stage or fee,
but returned the intermediate status `running`, causing CLI exit 2. The branch now
computes its completed/ready status before returning. It was not a ledger or proof
safety failure. Prior development case records are retained separately, and all
12 live cases were rerun against the final source pins after this correction.

The tests deliberately kill ONLY their own fresh child coordinators. Killed and
superseded attempts retain charges. No test timeout or setup/import failure is
counted as a successful negative result.

## What is not claimed

No full Python/SQL refinement, power-loss experiment, hostile rollback protection,
complete physical-compute-cost accounting, or optimal fault-policy theorem was
attempted or reported. Historical build/test records under older version folders
are not substituted for current evidence.
