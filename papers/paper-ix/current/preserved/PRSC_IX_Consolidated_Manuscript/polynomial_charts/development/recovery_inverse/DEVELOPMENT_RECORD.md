# Inverse congruence reconstruction record

The unpublished previous source and development files were removed by automated workspace maintenance. This source was reconstructed from the surviving task summary and the restored published dependencies. Earlier source hashes and execution evidence are not reused as evidence for this reconstruction.

The reconstructed source has six theorems: integer one-step inverse congruence, arbitrary integer precision, p-adic evaluation congruence, p-adic inverse congruence, exact input/output congruence equivalence, and local injectivity.

The integer argument uses the actual polynomial Taylor remainder, cancellation by a nonzero power of the positive modulus, and injectivity of a surjective endomap on the finite residue-vector space. The p-adic argument uses canonical integer truncations at depth N+1, forward polynomial congruence, constancy of the reduced Jacobian in its residue class, the integer theorem, and separation by all residue maps.

Reconstruction attempt 01 failed on a no-progress simplification, unfolding only one occurrence of p-adic evaluation, and tactic terms without an expected type. Attempt 02 failed on a no-progress ring call and warnings about unnecessary tactic sequencing. Attempt 03 exposed the remaining equality of integer divisibility instances; the instance equality was closed by reflexivity and the arithmetic equality by the expanded actual Jacobian definition. Attempt 04 passed with warningAsError=true, one thread, the default heartbeat budget, and no new axioms. The retained logs show those failures and the final successful result. Failed elaborations print Lean's automatically inserted sorryAx in their diagnostic axiom output, but the final source contains no admissions and the successful run reports only propext, Classical.choice, and Quot.sound for every theorem.

Command for the clean reconstruction check:

```sh
python3 polynomial_charts/scripts/check_low_memory.py --kit /workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2 --threads 1 --timeout 240 --import-dir polynomial_charts/dev/recovery/build --output polynomial_charts/dev/recovery/build/PolynomialInverseCongruence.olean polynomial_charts/formalization/PolynomialInverseCongruence.lean
```

The final independent release replay must compile this frozen source again. Development compilation alone is not the release gate.
