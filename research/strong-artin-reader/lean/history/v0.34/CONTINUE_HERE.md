# Continue from v0.34

Read README.md, RESEARCH_BOUNDARY.md, SELF_REVIEW.md and RESULT.json. Preserve the exact v0.33 parent hash 88706e3980c6c8306e250df8d3ba45618a1f33e803f9984ff8a6cf7d28079e24.

The new core is `MixedCharacteristic.matrixKernelEquiv`, `kernelCoordinates_division`, `conjugation_coordinates`, `primePowerLayerModel`, and `primePower_layer_simultaneous_criterion`.

The next question is compatible PRESCRIBED lifts through a coefficient tower. The coordinate model is no longer missing at Z/p-power layers. The same residual adjoint operator governs corrections, but the error changes with the chosen lift and targets. Do not infer a full tower or unconditional obstruction vanishing.

Matrix controls are over Z/9 -> F3. No integral splitting is used; no_additive_layer_retraction proves a global additive retraction cannot exist. Actual Frobenius class vanishing is checked, not an augmented surrogate equation.

Replay in bounded batches with `python3 verify.py --kit PATH --max-modules 8`, then `--resume`. Run checks/exact_mixed_characteristic.py. A new release must report observed compiler exit codes and preserve prior arithmetic non-claims.
