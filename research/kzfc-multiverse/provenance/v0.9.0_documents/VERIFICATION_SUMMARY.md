# Verification summary v0.9.0

The authoritative result is verification/RESULTS.json plus process_record.json. This prose is not a success flag.

Contract: 439 named declarations in 40 mathematical modules, plus the root. Preserve 33 predecessor modules with 378 declarations. Check all 61 new declarations, including technical support and interpretation lemmas, by Lean. Audit every name and reject nonstandard/custom axioms or proof placeholders. Run expected-failure controls.

The fixed clean staged plan comprises 87 compiler commands. Proof input hashes remain fixed across batches. Project outputs are rebuilt, while the pinned dependency cache is reused. Every compiler process exit and log hash is recorded. The finalizer checks all plan coverage and integrity before a verdict exists.

Mathematical scope is supplied by the universal theorem statements and kernel-checked proofs, not bounded testing. The all-model theorem is a reduction to internal small-product closure. The arithmetic discharge and unconditional guarded forward implication are concrete ZFSet results only. No uncountable existence or full arbitrary-model classification is claimed.
