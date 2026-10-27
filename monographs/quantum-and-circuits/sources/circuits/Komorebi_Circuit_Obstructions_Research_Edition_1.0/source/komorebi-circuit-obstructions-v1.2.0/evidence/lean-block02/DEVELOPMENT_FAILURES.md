# Development failures and corrections — Block 02

## Environment and toolchain

A GitHub download probe failed at DNS resolution. A streaming container launch was rejected (`StreamingExecNotEnabledContainerError`); it did not start a compiler. The first subsequent extraction command failed because its destination directory had not been created. After creating that directory, the stored/CRC-checked first portable archive part produced a usable core toolchain.

The XZ and TAR readers reported EOF at the truncated multipart boundary. This was expected for the first part and is **not** a successful verification of the full multipart distribution. The recovered Lean, Lake, and leanchecker binaries match the predecessor's recorded hashes, and their version/build/checker behavior was tested. No full-distribution authenticity claim is made. No recovered binary is redistributed.

## Lean development

Initial proofs used tactics or library identifiers not available in bundled Std, including Nat.find, Nat.strong_induction_on and a Mathlib-style list length lemma. Some Bool goals also needed explicit case splitting rather than an open-variable `decide`. Partial-application reductions and unused simplifier arguments caused additional strict-build failures. These implementation/elaboration failures are retained in the attempt logs. They were resolved with explicit Bool cases, Nat.strongRecOn, direct list proofs and correct unfolding. No assertion was weakened by inserting an axiom or admitted proof.

The final source audit includes all 115 declarations and all eight modules. Eight intentionally invalid proof controls are required to fail. Those expected rejections are success conditions of the audit, not mathematical counterexamples to maintained results.

## Packaging

A pre-seal unit-test run caught a README link to the not-yet-created Block 02 PDF. This is a packaging failure; the PDF and source were subsequently created and the final link test is rerun. A draft documentation reference used `betaStar_le_input_size` rather than the actual declaration `betaStar_le_inputs`; source-inventory comparison corrected that reference before delivery.

## Remaining limits

No universal mathematical claim failed in the final source. No independent mathematical reviewer or independent kernel implementation was used. The exact Python controls are bounded and do not prove circuit optimality outside the stated formal examples. The C02 dual certificate remains unformalized rather than implicitly assumed.
