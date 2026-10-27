import PaperXII.CompletedPointCategory

/-!
Direct restatement tests for the two disputed manuscript contracts.
These use the concrete tensor, completion and quotient definitions of the release.
They do not postulate an equivalence, a universal property, or an arithmetic realization.
They are audit tests, not new manuscript claims or additions to the theorem census.
-/
noncomputable section
set_option autoImplicit false
namespace PaperXII.ManuscriptContractReplay

open PaperXII

section TensorQuotient
variable {O ι : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable (mO : Ideal O) (m : ∀ i, Ideal (R i)) (I : ∀ i, Ideal (R i))

/-- Claim 3.1: existence, both continuity directions and canonical-factor compatibility. -/
theorem claim31_contract :
    ∃ e : FiniteTensor.CompletedTensor (fun i ↦ R i ⧸ I i) mO
      (fun i ↦ (m i).map (Ideal.Quotient.mk (I i))) ≃ₐ[O]
      (FiniteTensor.CompletedTensor R mO m ⧸ FiniteTensor.closedConditions R mO m I),
      Continuous e ∧ Continuous e.symm ∧
        ∀ (i : ι) (x : R i),
          e (FiniteTensor.completedInclude (fun i ↦ R i ⧸ I i) mO
            (fun i ↦ (m i).map (Ideal.Quotient.mk (I i))) i (Ideal.Quotient.mk (I i) x)) =
          Ideal.Quotient.mk _ (FiniteTensor.completedInclude R mO m i x) := by
  exact ⟨FiniteTensor.completed_tensor_quotient R mO m I,
    (FiniteTensor.completed_tensor_quotient_continuous R mO m I).1,
    (FiniteTensor.completed_tensor_quotient_continuous R mO m I).2,
    FiniteTensor.completed_tensor_quotient_factor R mO m I⟩
end TensorQuotient

section LocalPoints
open CompletedLocalConditions
variable {O ι k : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
variable [Field k] [Algebra O k]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable [IsNoetherianRing O] [∀ i, IsNoetherianRing (R i)]
variable (res : ∀ i, R i →ₐ[O] k) (hO : Function.Surjective (algebraMap O k))
variable (I : ∀ i, Ideal (R i))
variable {B : Type*} [CommRing B] [Algebra O B]
  [Algebra (LocalTensor R (RingHom.ker (algebraMap O k))
    (fun i ↦ RingHom.ker (res i))) B]
  [IsLocalRing B]
  [IsLocalHom (algebraMap (LocalTensor R (RingHom.ker (algebraMap O k))
    (fun i ↦ RingHom.ker (res i))) B)]
  [UniformSpace B] [IsUniformAddGroup B] [IsTopologicalRing B] [CompleteSpace B]
variable {P : Type*} [CommRing P] [Algebra O P] [UniformSpace P]
  [IsUniformAddGroup P] [IsTopologicalRing P] [CompleteSpace P] [T2Space P]
attribute [local instance] CompletedLocalConditions.globalCoefficientAlgebra

include hO in
/-- Claim 3.3: exact continuous local algebra-point factorization, with no supplied
finite-generation or structural-ideal-bound hypotheses. They follow from the
Noetherian/common-residue/local-map context. -/
theorem claim33_contract (hB : IsAdic (IsLocalRing.maximalIdeal B))
    (p : B →ₐ[O] P) [IsLocalHom p.toRingHom] (hp : Continuous p) :
    (∃! g : GlobalRing R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i)) I (IsLocalRing.maximalIdeal B) →ₐ[O] P,
      Continuous g ∧ IsLocalHom g.toRingHom ∧
        g.comp (globalAlgMap R (RingHom.ker (algebraMap O k))
          (fun i ↦ RingHom.ker (res i)) I (IsLocalRing.maximalIdeal B)) = p) ↔
      ∀ i, I i ≤ RingHom.ker ((p.toRingHom.comp (algebraMap
        (LocalTensor R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B)).comp
          (FiniteTensor.completedInclude R (RingHom.ker (algebraMap O k))
            (fun i ↦ RingHom.ker (res i)) i).toRingHom) := by
  exact local_algebra_point_iff R _ _ I _ (Ideal.fg_of_isNoetherianRing _)
    (fun _i ↦ Ideal.fg_of_isNoetherianRing _) hB (local_map_ideal_bound R res hO) p hp
end LocalPoints

section Kernel
open UniformSpace
open scoped Uniformity
variable {R : Type*} [CommRing R] [UniformSpace R] [IsUniformAddGroup R]
  [IsTopologicalRing R] [Filter.IsCountablyGenerated (𝓤 R)]

/-- The constructed comparison has precisely the stated closed extended kernel. -/
theorem exact_closed_kernel (I : Ideal R) :
    RingHom.ker (CompletionQuotient.forwardMap I) = CompletionQuotient.closedExtension I := by
  apply le_antisymm
  · intro x hx
    apply Ideal.Quotient.eq_zero_iff_mem.mp
    apply (CompletionQuotient.equiv I).injective
    change CompletionQuotient.forwardMap I x = 0 at hx
    calc
      _ = CompletionQuotient.forwardMap I x := rfl
      _ = 0 := hx
      _ = (CompletionQuotient.equiv I) 0 := (map_zero _).symm
  · exact CompletionQuotient.closedExtension_le_ker I
end Kernel

#print axioms claim31_contract
#print axioms claim33_contract
#print axioms exact_closed_kernel
end PaperXII.ManuscriptContractReplay
