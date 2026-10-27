# Block 14 — Failure and repair record

16 recorded mathematical development compilations, of which **8 failed**. Every failed source snapshot and compiler log is retained under the receipt directory shown below. These attempts do not count as checked results.

| Module | Return code | Receipt | Repair |
|---|---:|---|---|
| `ResolventDomain` | 1 | `verification/development/block14/20260914T090052821086Z/receipt.json` | Two theorems mentioned the shifted map but not the inverse certificate in their conclusion, so Lean omitted the section variable. Added explicit inclusion of that certificate. |
| `ResolventCommutator` | 1 | `verification/development/block14/20260914T090121854453Z/receipt.json` | Replaced deprecated zero-application names, used the correct side-cancellation lemma, and removed an unnecessary simplification warning. No assumptions or conclusions changed. |
| `ResolventBounds` | 1 | `verification/development/block14/20260914T090148172698Z/receipt.json` | Made real/imaginary self-pairing equalities explicit for complex inner products and normalized absolute values without rewriting the wrong subexpression. |
| `DiagonalResolvents` | 1 | `verification/development/block14/20260914T090329946156Z/receipt.json` | Explicitly included the nonreal hypothesis in scalar support theorems. Its omission caused cascading type errors in later definitions. Also supplied the proved nonzero denominator to exact field simplification. |
| `NonreducingPacket` | 1 | `verification/development/block14/20260914T090600562344Z/receipt.json` | Removed an unreachable arithmetic tactic after simplification had already closed all goals. |
| `ResolventParameters` | 1 | `verification/development/block14/20260914T090738931863Z/receipt.json` | Avoided rewriting the source vector inside its own nested expression and used scalar injectivity on the operator space rather than on its vector space. |
| `ResolventExamples` | 1 | `verification/development/block14/20260914T090923405429Z/receipt.json` | First failure: removed an already-closed tactic and proved additive torsion cancellation through complex scalar multiplication rather than assuming the operator ring has no zero divisors. Second failure: normalized complex conjugation of rational numerals in the exact z=i calculation. |
| `ResolventExamples` | 1 | `verification/development/block14/20260914T091051313296Z/receipt.json` | First failure: removed an already-closed tactic and proved additive torsion cancellation through complex scalar multiplication rather than assuming the operator ring has no zero divisors. Second failure: normalized complex conjugation of rational numerals in the exact z=i calculation. |

All seven final new modules subsequently compiled individually without admissions or weakened statements. The production and extraction audits have their own complete reports and must be checked independently of this development summary.

## Environment and inspections

The original runtime was not installed in this container. Its seven already-mounted offline archive parts were assembled and extracted by the included `runtime_restore_support/assemble.py`. All seven part hashes and the combined SHA-256 passed; the completed console log is `verification/development/block14/runtime_restore.log`. Runtime bytes are external to the source package.

An initial filesystem inspection asked for a nonexistent `scripts/restore_runtime.py`. No restoration was performed by that absent path. The actual included assembler was located and executed successfully. Some metadata grep/inspection commands returned no matching names; no mathematical result was inferred from them.

No development execution timeout, incomplete proof admission, custom axiom, numerical approximation, or disabled kernel check is counted as success. The complete 1,173-theorem baseline passed before extending the inventory. Production/extraction status is determined by their finished reports, not by an uncompleted console tail.


## First cumulative audit failure and repair

The first production audit freshly compiled all 78 modules and the aggregate, and passed the complete 1,502-name axiom audit. It did **not** complete the negative-control contract. With 101 deliberately invalid controls, Lean's default `maxErrors=100` stopped reporting before the final control's designated diagnostic. The verifier correctly reported FAIL, not PASS.

The complete failed run is retained under `verification/failed_block14_audit_01/`, including its source-hash record, all compiler logs and the negative-control batch. No mathematical source or negative-control assertion was changed. The repaired verifier adds `-DmaxErrors=1000` only to the deliberately invalid batch, so it can report all errors. Warnings-as-errors, all intended diagnostic requirements, no-import-failure checks, axiom restrictions and every preservation condition remain unchanged. The full cumulative verifier is rerun from clean local outputs after this repair.

The repaired full production audit completed with PASS: 78 modules plus aggregate, 1,502 inventoried names and 101/101 invalid controls. Its proof-input set contains 199 hashed files. The fresh archive audit is delivered as separate external evidence.
