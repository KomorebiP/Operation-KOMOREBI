import PaperXII.CompletedPointCategory

/-!
Independent end-to-end consumers for the two final manuscript claims.
These are release checks, not additional manuscript claims. The production
proofs are imported unchanged. Every ideal, completion, map, and topology
appearing below is the corresponding constructed production object.
-/
noncomputable section
set_option autoImplicit false
namespace PaperXIIFinalConsumer
open PaperXII


section Kernel
variable {S : Type*} [CommRing S] [UniformSpace S] [IsUniformAddGroup S]
  [IsTopologicalRing S]
open scoped Uniformity
variable [Filter.IsCountablyGenerated (𝓤 S)]

/-- The completed quotient map kills exactly the closed extended ideal. -/
theorem exact_completed_kernel (I : Ideal S) :
    RingHom.ker (CompletionQuotient.forwardMap I) =
      CompletionQuotient.closedExtension I := by
  apply le_antisymm
  · intro x hx
    apply Ideal.Quotient.eq_zero_iff_mem.mp
    apply (CompletionQuotient.equiv I).injective
    change CompletionQuotient.forwardMap I x = CompletionQuotient.equiv I 0
    simpa only [map_zero] using hx
  · exact CompletionQuotient.closedExtension_le_ker I
end Kernel

section Tensor
variable {O ι : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable (mO : Ideal O) (m : ∀ i, Ideal (R i)) (I : ∀ i, Ideal (R i))

/-- Claim 3.1, with existence, the two topologies, and every factor map
in one statement. No isomorphism or inverse law is an input. -/
theorem claim31 :
    ∃ e : FiniteTensor.CompletedTensor (fun i ↦ R i ⧸ I i) mO
        (fun i ↦ (m i).map (Ideal.Quotient.mk (I i))) ≃ₐ[O]
        (FiniteTensor.CompletedTensor R mO m ⧸ FiniteTensor.closedConditions R mO m I),
      Continuous e ∧ Continuous e.symm ∧
      ∀ (i : ι) (x : R i),
        e (FiniteTensor.completedInclude (fun i ↦ R i ⧸ I i) mO
          (fun i ↦ (m i).map (Ideal.Quotient.mk (I i))) i
            (Ideal.Quotient.mk (I i) x)) =
          Ideal.Quotient.mk _ (FiniteTensor.completedInclude R mO m i x) := by
  refine ⟨FiniteTensor.completed_tensor_quotient R mO m I,
    (FiniteTensor.completed_tensor_quotient_continuous R mO m I).1,
    (FiniteTensor.completed_tensor_quotient_continuous R mO m I).2, ?_⟩
  exact FiniteTensor.completed_tensor_quotient_factor R mO m I
end Tensor

section Global

variable {O ι k : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
  [Field k] [Algebra O k] [IsNoetherianRing O]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
  [∀ i, IsNoetherianRing (R i)]
variable (res : ∀ i, R i →ₐ[O] k) (hO : Function.Surjective (algebraMap O k))
variable (I : ∀ i, Ideal (R i))
variable {B : Type*} [CommRing B] [Algebra (CompletedLocalConditions.LocalTensor R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B] [Algebra O B]
  [IsLocalRing B] [IsLocalHom (algebraMap (CompletedLocalConditions.LocalTensor R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B)]
  [UniformSpace B] [IsUniformAddGroup B] [IsTopologicalRing B] [CompleteSpace B]
variable {P : Type*} [CommRing P] [Algebra O P]
  [UniformSpace P] [IsUniformAddGroup P] [IsTopologicalRing P]
  [CompleteSpace P] [T2Space P]
attribute [local instance] CompletedLocalConditions.globalCoefficientAlgebra

include hO in
/-- Claim 3.3 for continuous local coefficient-algebra points. Finite generation
and the required structural ideal bound are derived from Noetherianity, the
common residue field, and locality, rather than supplied as extra hypotheses. -/
theorem claim33 (hB : IsAdic (IsLocalRing.maximalIdeal B))
    (p : B →ₐ[O] P) [IsLocalHom p.toRingHom] (hp : Continuous p) :
    (∃! g : CompletedLocalConditions.GlobalRing R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)) I
        (IsLocalRing.maximalIdeal B) →ₐ[O] P,
      Continuous g ∧ IsLocalHom g.toRingHom ∧
        g.comp (CompletedLocalConditions.globalAlgMap R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)) I
          (IsLocalRing.maximalIdeal B)) = p) ↔
      ∀ i, I i ≤ RingHom.ker ((p.toRingHom.comp (algebraMap (CompletedLocalConditions.LocalTensor R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))) B)).comp
        (FiniteTensor.completedInclude R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)) i).toRingHom) := by
  exact CompletedLocalConditions.local_algebra_point_iff R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)) I
    (IsLocalRing.maximalIdeal B) (Ideal.fg_of_isNoetherianRing _)
    (fun _ ↦ Ideal.fg_of_isNoetherianRing _) hB
    (CompletedLocalConditions.local_map_ideal_bound R res hO) p hp
end Global

#print axioms exact_completed_kernel
#print axioms claim31
#print axioms claim33
end PaperXIIFinalConsumer
