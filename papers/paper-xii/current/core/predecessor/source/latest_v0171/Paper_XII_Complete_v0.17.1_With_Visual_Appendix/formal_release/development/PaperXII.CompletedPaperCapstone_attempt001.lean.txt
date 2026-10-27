import PaperXII.CompletedLocalConditions
import PaperXII.CompletedGlobalQuotient

/-!
# Manuscript-level completion of Claims 3.1 and 3.3

Noetherian hypotheses supply finite generation, and the local global map
supplies the ideal bound. Neither is a new arithmetic existence input.
The scalar and local-point conclusions are retained explicitly.
-/
noncomputable section
set_option autoImplicit false
namespace PaperXII.CompletedLocalConditions

variable {O ι k : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
  [Field k] [Algebra O k]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable (res : ∀ i, R i →ₐ[O] k) (hO : Function.Surjective (algebraMap O k))
variable [IsNoetherianRing O] [∀ i, IsNoetherianRing (R i)]

include hO in
/-- The ideal defining the actual local tensor topology is its maximal ideal. -/
theorem localIdeal_eq_maximalIdeal :
    haveI := FiniteTensor.completedTensor_isLocalRing_noetherian R res hO
    localIdeal R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)) =
      IsLocalRing.maximalIdeal (LocalTensor R (RingHom.ker (algebraMap O k))
        (fun i ↦ RingHom.ker (res i))) := by
  have hm := FiniteTensor.residueIdeal_isMaximal R res hO
  exact (AdicModel.completed_maximalIdeal _ (FiniteTensor.definingIdeal_fg R _ _
    (Ideal.fg_of_isNoetherianRing _) (fun _i ↦ Ideal.fg_of_isNoetherianRing _))).symm

variable (I : ∀ i, Ideal (R i))
variable {B : Type*} [CommRing B]
  [Algebra (LocalTensor R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B]
  [IsLocalRing B]
  [IsLocalHom (algebraMap (LocalTensor R (RingHom.ker (algebraMap O k))
    (fun i ↦ RingHom.ker (res i))) B)]

include hO in
/-- A local global coefficient map automatically respects the required adic ideals. -/
theorem local_map_ideal_bound :
    (localIdeal R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))).map
      (algebraMap (LocalTensor R (RingHom.ker (algebraMap O k))
        (fun i ↦ RingHom.ker (res i))) B) ≤ IsLocalRing.maximalIdeal B := by
  have := FiniteTensor.completedTensor_isLocalRing_noetherian R res hO
  rw [localIdeal_eq_maximalIdeal R res hO]
  exact IsLocalRing.map_maximalIdeal_le _

variable [UniformSpace B] [IsUniformAddGroup B] [IsTopologicalRing B]
variable {P : Type*} [CommRing P] [UniformSpace P] [IsUniformAddGroup P]
  [IsTopologicalRing P] [CompleteSpace P] [T2Space P]

omit [IsUniformAddGroup B] in
include hO in
/-- Claim 3.3 at the manuscript's Noetherian and local-map boundary. -/
theorem global_base_change_noetherian (hB : IsAdic (IsLocalRing.maximalIdeal B))
    (p : B →+* P) (hp : Continuous p) :
    (∃! g : GlobalRing R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i)) I (IsLocalRing.maximalIdeal B) →+* P,
      Continuous g ∧ g.comp (globalMap R (RingHom.ker (algebraMap O k))
        (fun i ↦ RingHom.ker (res i)) I (IsLocalRing.maximalIdeal B)) = p) ↔
      ∀ i, I i ≤ RingHom.ker ((p.comp (algebraMap (LocalTensor R
        (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B)).comp
          (FiniteTensor.completedInclude R (RingHom.ker (algebraMap O k))
            (fun i ↦ RingHom.ker (res i)) i).toRingHom) :=
  global_base_change R _ _ I _ (Ideal.fg_of_isNoetherianRing _)
    (fun _i ↦ Ideal.fg_of_isNoetherianRing _) hB (local_map_ideal_bound R res hO) p hp

end PaperXII.CompletedLocalConditions
