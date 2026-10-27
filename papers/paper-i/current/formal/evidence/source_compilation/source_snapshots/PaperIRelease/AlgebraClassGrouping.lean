import PaperIRelease.AlgebraQuotient

set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option maxHeartbeats 3000000
noncomputable section

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open PacketAggregation

universe u v w z
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I] [DecidableEq I]
variable {J : Type z} [Fintype J] [DecidableEq J]

theorem groupedProjection_original (P : LinearProjectorFamily K X I)
    (σ : I → J) (a : I) (x : X) :
    groupedProjection P σ (σ a) (P.proj a x) = P.proj a x := by
  obtain ⟨y, hy⟩ := original_mem_grouped P σ a ⟨P.proj a x, ⟨x, rfl⟩⟩
  change (groupedFamily P σ).proj (σ a) (P.proj a x) = P.proj a x
  change (groupedFamily P σ).proj (σ a) y = P.proj a x at hy
  rw [← hy]
  exact (groupedFamily P σ).idempotent (σ a) y

/-- Grouping by a relation-compatible class map preserves the exact support condition. -/
theorem grouped_operatorSupported_iff (P : LinearProjectorFamily K X I)
    (σ : I → J) (rel : J → J → Prop) (T : Module.End K X) :
    OperatorSupported (groupedFamily P σ) rel T ↔
      OperatorSupported P (fun a b => rel (σ a) (σ b)) T := by
  rw [operatorSupported_iff_ambient, operatorSupported_iff_ambient]
  constructor
  · intro h b a hab
    ext x
    have hh := congrArg (P.proj b) (LinearMap.congr_fun (h (σ b) (σ a) hab) (P.proj a x))
    simpa [transferBlock, groupedFamily,
      proj_groupedProjection, groupedProjection_original] using hh
  · intro h d c hcd
    ext x
    simp only [transferBlock, LinearMap.comp_apply, groupedFamily,
      groupedProjection, LinearMap.sum_apply, map_sum, LinearMap.zero_apply]
    apply Finset.sum_eq_zero
    intro b hb
    apply Finset.sum_eq_zero
    intro a ha
    have hab : ¬ rel (σ b) (σ a) := by
      rw [(Finset.mem_filter.mp ha).2, (Finset.mem_filter.mp hb).2]
      exact hcd
    exact LinearMap.congr_fun (h a b hab) x

section Preorder
variable [Preorder I]

abbrev PreorderClasses (I : Type w) [Preorder I] := Antisymmetrization I (· ≤ ·)

noncomputable instance preorderClassesFintype : Fintype (PreorderClasses I) := by
  classical
  exact Fintype.ofSurjective (toAntisymmetrization (· ≤ ·))
    (fun C => ⟨ofAntisymmetrization (· ≤ ·) C, toAntisymmetrization_ofAntisymmetrization (· ≤ ·) C⟩)
noncomputable instance preorderClassesDecidableEq : DecidableEq (PreorderClasses I) := Classical.decEq _

/-- The actual quotient class of a packet in the preorder. -/
def packetClass : I → PreorderClasses I := toAntisymmetrization (· ≤ ·)

/-- Projectors obtained by aggregating precisely the mutual-reachability classes. -/
def classPacketFamily (P : LinearProjectorFamily K X I) :
    LinearProjectorFamily K X (PreorderClasses I) :=
  groupedFamily P packetClass

theorem classSupport_iff (P : LinearProjectorFamily K X I) (T : Module.End K X) :
    OperatorSupported (classPacketFamily P) (· ≤ ·) T ↔ OperatorSupported P (· ≤ ·) T := by
  rw [classPacketFamily, grouped_operatorSupported_iff]
  simp only [packetClass, toAntisymmetrization_le_toAntisymmetrization_iff]

/-- Grouping equivalence does not alter the ambient operator: it changes only support coordinates. -/
def preorderClassSupportEquiv (P : LinearProjectorFamily K X I) :
    preorderSupportAlgebra P ≃ₐ[K] preorderSupportAlgebra (classPacketFamily P) where
  toFun T := ⟨T.1, (classSupport_iff P T.1).mpr T.property⟩
  invFun T := ⟨T.1, (classSupport_iff P T.1).mp T.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_mul' _ _ := rfl
  map_add' _ _ := rfl
  commutes' _ := rfl

/-- The diagonal-class map on the original preorder support algebra. -/
def preorderDiagonalHom (P : LinearProjectorFamily K X I) :
    preorderSupportAlgebra P →ₐ[K] ((C : PreorderClasses I) →
      Module.End K (LinearMap.range ((classPacketFamily P).proj C))) :=
  (diagonalClassHom (classPacketFamily P)).comp (preorderClassSupportEquiv P).toAlgHom

theorem preorderDiagonalHom_surjective (P : LinearProjectorFamily K X I) :
    Function.Surjective (preorderDiagonalHom P) :=
  (diagonalClassHom_surjective (classPacketFamily P)).comp (preorderClassSupportEquiv P).surjective

/-- The quotient map's kernel is exactly the ideal of strictly-between-class blocks. -/
theorem preorderDiagonalHom_eq_zero_iff (P : LinearProjectorFamily K X I)
    (T : preorderSupportAlgebra P) :
    preorderDiagonalHom P T = 0 ↔ OperatorSupported P (· < ·) T.1 := by
  change diagonalClassHom (classPacketFamily P) (preorderClassSupportEquiv P T) = 0 ↔ _
  rw [diagonalClassHom_eq_zero_iff]
  change OperatorSupported (classPacketFamily P) (· < ·) T.1 ↔ _
  rw [classPacketFamily, grouped_operatorSupported_iff]
  simp only [packetClass, toAntisymmetrization_lt_toAntisymmetrization_iff]

theorem preorderDiagonal_kernel_eq (P : LinearProjectorFamily K X I) :
    RingHom.ker (preorderDiagonalHom P).toRingHom = (strictSupportIdeal P).asIdeal := by
  ext T
  change preorderDiagonalHom P T = 0 ↔ T ∈ (strictSupportIdeal P).asIdeal
  rw [preorderDiagonalHom_eq_zero_iff]
  simp only [TwoSidedIdeal.mem_asIdeal, mem_strictSupportIdeal]

/-- Full preorder support algebra quotient, indexed by the actual quotient classes. -/
def preorderQuotientEquiv (P : LinearProjectorFamily K X I) :
    (preorderSupportAlgebra P ⧸ RingHom.ker (preorderDiagonalHom P).toRingHom) ≃ₐ[K]
      ((C : PreorderClasses I) → Module.End K (LinearMap.range ((classPacketFamily P).proj C))) :=
  Ideal.quotientKerAlgEquivOfSurjective (preorderDiagonalHom_surjective P)

/-- The quotient by the explicitly constructed nilpotent two-sided ideal. -/
def preorderStrictIdealQuotientEquiv (P : LinearProjectorFamily K X I) :
    (preorderSupportAlgebra P ⧸ (strictSupportIdeal P).asIdeal) ≃ₐ[K]
      ((C : PreorderClasses I) → Module.End K (LinearMap.range ((classPacketFamily P).proj C))) := by
  exact (Ideal.quotientEquivAlgOfEq K (preorderDiagonal_kernel_eq P).symm).trans
    (preorderQuotientEquiv P)

private theorem strictPath_map {A B : Type*} [Preorder A] [Preorder B]
    (f : A → B) (hf : ∀ a b, a < b → f a < f b) {n : ℕ} {a b : A}
    (h : StrictPath n a b) : StrictPath n (f a) (f b) := by
  induction n generalizing b with
  | zero => exact congrArg f h
  | succ n ih =>
    obtain ⟨c, hc, hcb⟩ := h
    exact ⟨f c, ih hc, hf c b hcb⟩

/-- Quotienting a preorder by mutual comparability preserves all strict path lengths. -/
theorem class_strict_path_lengths :
    {n | ∃ a b : I, StrictPath n a b} =
      {n | ∃ A B : PreorderClasses I, StrictPath n A B} := by
  ext n
  constructor
  · rintro ⟨a,b,h⟩
    exact ⟨packetClass a, packetClass b, strictPath_map packetClass
      (fun _ _ hlt => toAntisymmetrization_lt_toAntisymmetrization_iff.mpr hlt) h⟩
  · rintro ⟨A,B,h⟩
    refine ⟨ofAntisymmetrization (· ≤ ·) A, ofAntisymmetrization (· ≤ ·) B,
      strictPath_map (ofAntisymmetrization (· ≤ ·)) ?_ h⟩
    intro C D hCD
    apply toAntisymmetrization_lt_toAntisymmetrization_iff.mp
    simpa only [toAntisymmetrization_ofAntisymmetrization] using hCD

/-- The exponent is exactly one more than the height of the partial order of quotient classes. -/
theorem class_maximalStrictSteps : maximalStrictSteps I = maximalStrictSteps (PreorderClasses I) := by
  unfold maximalStrictSteps
  rw [class_strict_path_lengths]

/-- Each quotient-class space is canonically the direct sum of its original packet spaces. -/
def preorderClassRangeEquiv (P : LinearProjectorFamily K X I) (C : PreorderClasses I) :
    LinearMap.range ((classPacketFamily P).proj C) ≃ₗ[K]
      DirectSum {i : I // packetClass i = C} (fun i => LinearMap.range (P.proj i.val)) :=
  groupedRangeDirectSumEquiv P packetClass C

/-- Direct-sum form of the quotient-algebra decomposition printed in Paper I. -/
def preorderQuotientDirectSumEquiv (P : LinearProjectorFamily K X I) :
    (preorderSupportAlgebra P ⧸ (strictSupportIdeal P).asIdeal) ≃ₐ[K]
      ((C : PreorderClasses I) → Module.End K
        (DirectSum {i : I // packetClass i = C} (fun i => LinearMap.range (P.proj i.val)))) :=
  (preorderStrictIdealQuotientEquiv P).trans
    (AlgEquiv.piCongrRight fun C => (preorderClassRangeEquiv P C).conjAlgEquiv K)

end Preorder
end Komorebi.PaperIRelease
