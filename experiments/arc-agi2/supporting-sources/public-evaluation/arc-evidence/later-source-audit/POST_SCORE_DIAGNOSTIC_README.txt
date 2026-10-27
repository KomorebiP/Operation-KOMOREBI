Post-score candidate-pool diagnostic

Preparation and review only: this script has not been executed, and no query
solution file was opened while preparing it. Run the final scoring workflow
first. The diagnostic requires its complete sealed pre-score prediction freeze,
final sealed independent scoring audit, both fixed-policy score files and their
hash-bound dispatches, submissions and ledgers. Missing prerequisites fail before
target access. Final scoring and result packaging have priority.

From the restored snapshot root, after the final artifacts exist:
  PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python arc-evidence/later-source-audit/post_score_candidate_pool_diagnostic.py --workspace "$(pwd -P)"

The script creates new files only:
  arc-evidence/fullbank-public-evaluation/post_score_candidate_pool_diagnostic.json
  arc-evidence/fullbank-public-evaluation/post_score_candidate_pool_diagnostic.csv
Existing output files are not overwritten. The frozen runtime and existing
inputs, predictions, score receipts and policies are never written.

It reuses the reviewed JSONStream parser and record-membership validator. The
first complete streaming pass authenticates all 120 tasks / 172 outputs, full
census semantic and byte hashes, input bindings, 77 interface receipts per task
and source identity without targets. The second pass measures recorded outputs
after authenticating the exact query-target bytes against the final score audit.
It makes no compiler, dispatcher, ranking or serialized-program execution calls.

The raw candidate-pool oracle chooses any correct recorded candidate separately
at each test position using query labels. Its coverage is a label-aware diagnostic,
never a solver score or a new frozen policy. The separate single-candidate whole
task count requires one complete candidate output vector to match all outputs.
Recorded live-base attempts remain separate. Saved eligible behavior pools help
separate coverage removed by filtering/supersession/abstention from coverage
present in an eligible behavior but missed by the fixed two-attempt selection.
The actual frozen-policy exact counts must agree with both final score receipts.
All retained non-ok compiler receipts are reported by provider and status.

Source inventory, size and content hashes must match the original authenticated
snapshot. Extraction mtimes may differ after relocation, but must remain stable
throughout the diagnostic. Cache writes are disabled inside the script. Its
stream parser imports Linux resource; execute in Linux or WSL, as in the portable
run note. Review and AST parsing are static checks, not runtime validation.
