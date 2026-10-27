import CyclicTransverseObstruction
import ProjectorProbeSurjectivity

namespace Komorebi.StrongArtin.CyclicRelativeProbeObstruction

open Komorebi.StrongArtin.CyclicTransverseObstruction
open Komorebi.StrongArtin.ProjectorProbeSurjectivity

noncomputable section

variable {k V ι : Type*} [Field k]
  [AddCommGroup V] [Module k V]

/-- The transverse correction map supplied by a probe family after quotienting
out a deliberately retained defect subspace. -/
def transverseProbeCorrectionMap
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i)) :
    Module.Dual k (ι → k) →ₗ[k] Module.Dual k (V ⧸ D) :=
  (probeEvalMap (quotientProbe D probe hvan)).dualMap

/-- Transverse probe separation makes the probe correction map surjective. -/
theorem transverseProbeCorrectionMap_surjective
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D) :
    Function.Surjective (transverseProbeCorrectionMap D probe hvan) := by
  exact dual_quotientProbe_surjective_of_kernel_le_defect D probe hvan hsep

/-- **Cyclic-relative obstruction capstone.** Suppose the known quotient-prime
cyclic direction is retained rather than killed, and a family of auxiliary
projector/Frobenius probes vanishes on that direction while separating every
transverse class. Then the complete first-order lifting obstruction vanishes
if and only if its scalar cyclic residual is zero.

Thus, at the linear-algebra level, transverse adequacy is enough: full adequacy
at the bad quotient prime is unnecessary once the cyclic defect is isolated. -/
theorem full_obstruction_eq_zero_iff_cyclic_residual_zero_of_transverse_probes
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D)
    (b : k × Module.Dual k (V ⧸ D)) :
    obstructionClass
        (blockJacobian (0 : k →ₗ[k] k)
          (transverseProbeCorrectionMap D probe hvan)) b = 0 ↔
      b.1 = 0 := by
  apply quotientPrime_blockObstruction_eq_zero_iff_cyclicResidual_zero
  exact transverseProbeCorrectionMap_surjective D probe hvan hsep

/-- Finite-dimensional numerical form: under transverse probe separation, the
complete first-order quotient-prime obstruction space has dimension exactly
one, namely the deliberately retained scalar cyclic direction. -/
theorem full_obstruction_finrank_eq_one_of_transverse_probes
    [FiniteDimensional k V]
    (D : Submodule k V) (probe : ι → Module.Dual k V)
    (hvan : ∀ i : ι, D ≤ LinearMap.ker (probe i))
    (hsep : ∀ v : V, (∀ i : ι, probe i v = 0) → v ∈ D) :
    Module.finrank k
        ((k × Module.Dual k (V ⧸ D)) ⧸
          LinearMap.range
            (blockJacobian (0 : k →ₗ[k] k)
              (transverseProbeCorrectionMap D probe hvan))) = 1 := by
  apply finrank_blockCoker_eq_one_of_scalar_cyclic
  exact transverseProbeCorrectionMap_surjective D probe hvan hsep

end
end Komorebi.StrongArtin.CyclicRelativeProbeObstruction

#print axioms Komorebi.StrongArtin.CyclicRelativeProbeObstruction.transverseProbeCorrectionMap_surjective
#print axioms Komorebi.StrongArtin.CyclicRelativeProbeObstruction.full_obstruction_eq_zero_iff_cyclic_residual_zero_of_transverse_probes
#print axioms Komorebi.StrongArtin.CyclicRelativeProbeObstruction.full_obstruction_finrank_eq_one_of_transverse_probes
