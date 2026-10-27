# Imported mathematical inputs

The new source uses proved Mathlib mathematics. It does not reclassify the classical cyclic-vector or spectral theorems as novel results. The pinned Mathlib commit is `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

## `Module.exists_ker_toSpanSingleton_eq_annihilator`

A vector attaining the full polynomial-module annihilator. Actual dependency of the new cyclic proof.

Source: `Mathlib/Algebra/Module/PID.lean:271`. Source-file SHA-256: `045f88f612385ab1ea5f1b656ddef9315c958e842bb7ccf2db7a28f58676588f`.

## `Module.equiv_directSum_of_isTorsion`

Proved primary PID decomposition available upstream. Inspected and type-checked; not claimed as a newly integrated general seed-rank theorem.

Source: `Mathlib/Algebra/Module/PID.lean:232`. Source-file SHA-256: `045f88f612385ab1ea5f1b656ddef9315c958e842bb7ccf2db7a28f58676588f`.

## `LinearMap.IsSymmetric.card_filter_eigenvalues_eq`

Counts the spectral list fibre as intrinsic eigenspace dimension.

Source: `Mathlib/Analysis/InnerProductSpace/Spectrum.lean:289`. Source-file SHA-256: `064c28a59f0099705d320ea54fdb8184ea3ad3bfbd38889b3d2405c0ba6de4bf`.

## `LinearMap.IsSymmetric.eigenvectorBasis`

Proved finite-dimensional orthonormal eigenbasis supplied by self-adjointness.

Source: `Mathlib/Analysis/InnerProductSpace/Spectrum.lean:300`. Source-file SHA-256: `064c28a59f0099705d320ea54fdb8184ea3ad3bfbd38889b3d2405c0ba6de4bf`.

The declaration-type test prints these inputs and their axioms. This does not amount to rebuilding every upstream source file. The runtime and full dependency sources remain external prerequisites.
