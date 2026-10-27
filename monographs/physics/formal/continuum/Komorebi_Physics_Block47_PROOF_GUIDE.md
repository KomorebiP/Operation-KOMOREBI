# Block 47 Proof Guide

## Core objects

- `ScalarTorusL2`: scalar complex `L²` on `UnitAddTorus (Fin 3)`.
- `TorusSpinorL2`: the four-coordinate `PiLp` Hilbert sum of scalar torus `L²`.
- `CoeffL2`: square-summable mode-indexed four-spinors.
- `torusCoeffL2`: coordinatewise scalar Fourier analysis.
- `torusFourierEquiv`: the resulting linear isometric equivalence.

## Surjectivity route

For `f : TorusSpinorL2`, scalar Fourier synthesis gives a convergent series in each coordinate. Projecting the Hilbert-sum synthesis series to coordinate `j` identifies the synthesized coordinate with the scalar Fourier expansion of `f j`. Extensionality across `Fin 4` yields `modeEmbed_torusCoeffL2`.

Surjectivity follows by choosing `torusCoeffL2 f`. `IsHilbertSum.ofSurjective` then converts the orthogonal family into a linear isometric equivalence.

## Propagator transport

The physical propagators are conjugations:

```lean
torusFourierEquiv.trans
  ((continuumCoeffUnitary m t).trans torusFourierEquiv.symm)
```

and analogously for the lattice propagator. Norm, inner-product, and group laws follow from the equivalence and the checked coefficient-space laws.

## Convergence transfer

`norm_fullTorusResidual_eq_coeff` proves equality of physical and coefficient residual norms. `fullTorusPropagator_compactTime_converges` then invokes the Block 46 full coefficient theorem verbatim after Fourier transport.
