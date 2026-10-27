# Development failures and limitations retained

## Environment

* A container attempt to query the public GitHub release API failed with a DNS
  resolution error. A direct asset download route was also unavailable. Neither
  attempt supplied an execution toolchain.
* The streaming container execution endpoint was unavailable. The command was
  not executed, so its intended directory creation did not occur; the next command
  reported that missing output directory. The directories were then created by a
  normal synchronous command.
* A full offline runtime extraction exceeded the enclosing 180-second cap. The
  whole runtime/Mathlib cache is NOT reported restored. The extracted Lean binary
  and Std dependencies were usable; a smoke test and all five project builds
  passed. The complete concatenated saved archive payload was separately hashed
  and matched the expected digest. See ENVIRONMENT_VERIFIED.json.

## Lean drafts

* RepresentationCore attempt 01 failed to infer the setoid for a bare
  `Quotient.sound` application, and a definition depending on classical choice
  needed its explicit `noncomputable` marker. Both were corrected; attempt 02
  compiled.
* FiniteCertificates attempt 01 used `by_contra`, unavailable in this Std-only
  setup. The proofs were rewritten with `Classical.byContradiction`; attempt 02
  compiled. This was an API/tactic issue, not a failed mathematical implication.
* The generic and generated minimum-state comparison was strengthened during
  review to cover competitor encodings preserving all word outputs without
  assuming their internal transition intertwining. The final cold audit checks
  the strengthened version.

## Execution

* One enclosing combined tool command timed out after a complete successful Lean
  audit but before the Python manifest existed. The missing manifest was not
  treated as a pass. The Python run was then executed separately and its manifest
  validated successfully.
* Deliberately corrupted certificates, impossible finite identities and the sorry
  placeholder are EXPECTED rejections, not unexpected mathematical failures.

## Claims not completed

The universal finite-ring matrix-to-Lean adapter, verified Python/JSON execution,
trained proposal policy, blind structural benchmark and broad novelty/advantage
assessment remain unfinished. This release makes no new p-adic classification.
