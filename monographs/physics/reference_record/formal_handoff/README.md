# Komorebi Physics v0.49.0 Complete Handoff

Classification: **CHECKED MODULAR CUMULATIVE**

Block 49 proves the exact first-order weighted Fourier characterization of the maximal free Dirac domain and constructs the Fourier-conjugated physical torus Hamiltonian as a densely defined, self-adjoint, closed `LinearPMap`.

## Verification

- production module build: 3,064 jobs, pass
- clean-stage module build: 3,064 jobs, pass
- exact published-source archive replay: 3,064 jobs, pass
- warning-as-error source compile: pass
- API checks: 40/40
- theorem/lemma axiom audits: 30/30
- negative controls: 3/3 correctly rejected
- parent Lean files: 905/905 byte-identical
- final Lean/config identity: 919/919

## Boundary

The release does not identify the checked unitary group with the unbounded functional-calculus exponential and does not prove graph or strong-resolvent convergence.

## Local verification

Extract the source ZIP, attach the exact portable Lean 4.34.0-rc2 / Mathlib cache, and run:

```text
lake build KomorebiPhysics.Relativistic3DWeightedDiracDomain
lake env lean -DwarningAsError=true KomorebiPhysics/Relativistic3DWeightedDiracDomain.lean
lake env lean -DwarningAsError=true CheckBlock49API.lean
lake env lean -DwarningAsError=true AuditBlock49.lean
```
