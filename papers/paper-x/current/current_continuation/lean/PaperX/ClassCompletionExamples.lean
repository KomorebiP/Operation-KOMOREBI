import PaperX.ClassCompletion
import PaperX.ClassInvariants
import PaperX.CompletionExamples

/-! Completion from actual conjugacy classes, instantiated over the actual
3-adic integers.  The finite source group is C2, not a global Galois group. -/
set_option autoImplicit false
namespace PaperX.ClassCompletionExamples
open PaperX.RepresentationLimits PaperX.RepresentationTopology
open PaperX.RepresentationClasses PaperX.ClassInvariants PaperX.ClassCompletion
open PaperX.CompletionExamples

variable {R : Type} [CommRing R] (I : Ideal R)

/-- The allowed nodes are genuine representation classes, constrained by the
characteristic polynomial of the actual generator action. -/
noncomputable def involutionClasses : ClassConditions (G := C2) (ι := Fin 2) I where
  allowed k c := classCharpoly c generator =
    (target (R := R)).map (Ideal.Quotient.mk (I^k))
  downward := by
    intro j k hjk c hc
    change classCharpoly (changeClassCoefficients (Ideal.Quotient.factorPow I hjk) c)
      generator = _
    rw [classCharpoly_changeCoefficients, hc, Polynomial.map_map]
    simp

theorem involution_classes_nonempty (k : ℕ) :
    ∃ c, (involutionClasses I).allowed k c := by
  obtain ⟨ρ, hρ⟩ := involution_levels_nonempty I k
  exact ⟨classOf ρ, hρ⟩

theorem involution_classes_finite (hI : I.FG) [Finite (R ⧸ I)] (k : ℕ) :
    Finite {c // (involutionClasses I).allowed k c} := by
  let : Finite (R ⧸ I^k) := Ideal.finite_quotient_pow hI k
  let : Finite (MatrixRep (R ⧸ I^k) C2 (Fin 2)) :=
    Finite.of_injective (fun ρ : MatrixRep (R ⧸ I^k) C2 (Fin 2) => (ρ : C2 → _))
      DFunLike.coe_injective
  let : Finite (ClassRep (R ⧸ I^k) C2 (Fin 2)) :=
    Finite.of_surjective classOf classOf_surjective
  infer_instance

/-- Apply the unframed completion theorem, then detect the polynomial from all
reductions. Continuity is actual continuity from the discrete finite group. -/
theorem involution_classes_realized [IsAdicComplete I R]
    (hI : I.FG) [Finite (R ⧸ I)] :
    ∃ ρ : MatrixRep R C2 (Fin 2),
      (∀ k, (involutionClasses I).allowed k (classOf (reduce I ρ k))) ∧
      AdicRepContinuous I ρ ∧ (ρ generator).charpoly = target := by
  obtain ⟨ρ, hρ⟩ := (class_realization_iff I (involutionClasses I)
    (finite_coefficients I hI) (fun k _ => involution_classes_finite I hI k)).mpr
      (fun k _ => involution_classes_nonempty I k)
  refine ⟨ρ, hρ, ?_, ?_⟩
  · let : TopologicalSpace R := I.adicTopology
    exact continuous_of_discreteTopology
  · exact PaperX.CommonSpine.charpoly_detected I ρ generator target hρ

/-- A nontrivial continuous 3-adic representation obtained from finite classes. -/
theorem actual_three_adic_class_completion :
    ∃ ρ : MatrixRep ℤ_[3] C2 (Fin 2),
      (∀ k, (involutionClasses (IsLocalRing.maximalIdeal ℤ_[3])).allowed k
        (classOf (reduce (IsLocalRing.maximalIdeal ℤ_[3]) ρ k))) ∧
      AdicRepContinuous (IsLocalRing.maximalIdeal ℤ_[3]) ρ ∧
      (ρ generator).charpoly = Polynomial.X^2 - 1 ∧ ρ generator ≠ 1 := by
  obtain ⟨ρ, hρ, hc, hp⟩ := involution_classes_realized
    (IsLocalRing.maximalIdeal ℤ_[3]) (IsNoetherian.noetherian _)
  exact ⟨ρ, hρ, hc, hp, nontrivial_generator ρ hp⟩

end PaperX.ClassCompletionExamples
