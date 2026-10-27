# Mixed-characteristic kernel route

Base: v0.33 SHA-256 88706e3980c6c8306e250df8d3ba45618a1f33e803f9984ff8a6cf7d28079e24.
Target: replace the field-linear kernel-coordinate assumption at Mat_n(Z/p^(r+1)) -> Mat_n(Z/p^r), r>=1, and apply the existing prescribed Frobenius norm criteria.
Success criterion: an actual additive equivalence and proved conjugation compatibility, integrated with the inherited matching class; include nonsemisimple positive/negative mixed-characteristic controls.
Route: multiplication by m defines an additive map ZMod p -> ZMod(m*p). Integer divisibility proves injectivity and the exact image. Entrywise lifting and left/right multiplication prove the residual adjoint model. The inherited norm and simultaneous criteria then apply without a coordinate assumption.
Outcome: proved as written at the source scope, with verification status in RESULT.json. Genuine nonsplitting is checked, and original unit-power prescriptions are used.
Next unresolved implication: choose compatible successful corrections through a prescribed coefficient tower. Automatic coordinates do not imply the mismatch at each layer vanishes.
