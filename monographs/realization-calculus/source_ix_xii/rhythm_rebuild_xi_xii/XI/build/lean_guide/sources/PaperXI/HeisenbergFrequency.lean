import PaperXI.DualCharacterSums
import PaperXI.HeisenbergNormalForm
import PaperXI.HeisenbergRepresentation

/-! Frequency projectors in an arbitrary representation of the actual Heisenberg group.
Completeness and translation produce a nonzero modulation-fixed vector without any
assumption on the dimension of the target representation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergFrequency
open scoped Classical
open PaperXI.Heisenberg

variable {K X W : Type*} [Field K] [AddCommGroup X] [Module K X]
variable [AddCommGroup W] [Module ℂ W]
variable [Fintype (Module.Dual K X)]

/-- The literal finite Fourier projector onto frequency `a`. -/
def projector (ψ : AddChar K ℂ) (σ : Representation ℂ (Element K X) W) (a : X) :
    Module.End ℂ W :=
  (Fintype.card (Module.Dual K X) : ℂ)⁻¹ •
    ∑ ξ : Module.Dual K X, ψ (-(ξ a)) • σ (modulationElement ξ)

@[simp] theorem projector_apply (ψ : AddChar K ℂ)
    (σ : Representation ℂ (Element K X) W) (a : X) (w : W) :
    projector ψ σ a w = (Fintype.card (Module.Dual K X) : ℂ)⁻¹ •
      ∑ ξ : Module.Dual K X, ψ (-(ξ a)) • σ (modulationElement ξ) w := by
  simp [projector, LinearMap.sum_apply]

/-- A projector value has the indicated modulation eigencharacter. -/
theorem eigen (ψ : AddChar K ℂ) (σ : Representation ℂ (Element K X) W)
    (a : X) (η : Module.Dual K X) (w : W) :
    σ (modulationElement η) (projector ψ σ a w) =
      ψ (η a) • projector ψ σ a w := by
  have hphase (ξ : Module.Dual K X) :
      ψ (-(ξ a)) = ψ (η a) * ψ (-((η + ξ) a)) := by
    rw [← ψ.map_add_eq_mul]
    congr 1
    simp
  have hshift : (∑ ξ : Module.Dual K X,
      ψ (-((η + ξ) a)) • σ (modulationElement (η + ξ)) w) =
      ∑ ξ : Module.Dual K X, ψ (-(ξ a)) • σ (modulationElement ξ) w := by
    exact Fintype.sum_equiv (Equiv.addLeft η) _ _ (fun _ => rfl)
  rw [projector_apply, map_smul, map_sum]
  simp only [map_smul]
  have hmul (ξ : Module.Dual K X) :
      σ (modulationElement η) (σ (modulationElement ξ) w) =
        σ (modulationElement (η + ξ)) w := by
    rw [← modulationElement_mul, map_mul]
    rfl
  simp_rw [hmul]
  have hs : (∑ ξ : Module.Dual K X,
      ψ (-(ξ a)) • σ (modulationElement (η + ξ)) w) =
      ψ (η a) • ∑ ξ : Module.Dual K X,
        ψ (-((η + ξ) a)) • σ (modulationElement (η + ξ)) w := by
    rw [Finset.smul_sum]
    apply Finset.sum_congr rfl
    intro ξ _
    rw [hphase ξ, mul_smul]
  rw [hs, hshift, smul_comm]

/-- Finite Fourier completeness as an equality of actual endomorphisms. -/
theorem complete [Fintype X] [FiniteDimensional K X]
    {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    (σ : Representation ℂ (Element K X) W) :
    (∑ a : X, projector ψ σ a) = LinearMap.id := by
  have hs (ξ : Module.Dual K X) : (∑ a : X, ψ (-(ξ a))) =
      if ξ = 0 then (Fintype.card X : ℂ) else 0 := by
    simpa using DualCharacters.sum_over_points hψ (-ξ)
  have hn : (Fintype.card (Module.Dual K X) : ℂ) ≠ 0 :=
    Nat.cast_ne_zero.mpr Fintype.card_ne_zero
  calc
    (∑ a : X, projector ψ σ a) =
        (Fintype.card (Module.Dual K X) : ℂ)⁻¹ •
          ∑ ξ : Module.Dual K X, (∑ a : X, ψ (-(ξ a))) •
            σ (modulationElement ξ) := by
      simp only [projector]
      rw [← Finset.smul_sum, Finset.sum_comm]
      congr 1
      apply Finset.sum_congr rfl
      intro ξ _
      rw [Finset.sum_smul]
    _ = (Fintype.card (Module.Dual K X) : ℂ)⁻¹ •
        ((Fintype.card X : ℂ) • LinearMap.id) := by
      simp [hs]
      rfl
    _ = LinearMap.id := by
      rw [← DualCharacters.card_dual (K := K) (X := X), ← mul_smul,
        inv_mul_cancel₀ hn, one_smul]

/-- A frequency projector selects its character on any eigenvector. -/
theorem projector_of_eigen {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    (σ : Representation ℂ (Element K X) W) (a b : X) (w : W)
    (hw : ∀ ξ : Module.Dual K X, σ (modulationElement ξ) w = ψ (ξ b) • w) :
    projector ψ σ a w = if a = b then w else 0 := by
  have hn : (Fintype.card (Module.Dual K X) : ℂ) ≠ 0 :=
    Nat.cast_ne_zero.mpr Fintype.card_ne_zero
  have hs : (∑ ξ : Module.Dual K X, ψ (-(ξ a)) •
      σ (modulationElement ξ) w) =
      (∑ ξ : Module.Dual K X, ψ (ξ (b - a))) • w := by
    rw [Finset.sum_smul]
    apply Finset.sum_congr rfl
    intro ξ _
    rw [hw, ← mul_smul, ← ψ.map_add_eq_mul]
    congr 2
    simp [sub_eq_add_neg, add_comm]
  rw [projector_apply, hs, DualCharacters.sum_over_dual hψ]
  by_cases hab : a = b
  · simp [hab, ← mul_smul, hn]
  · have hba : b - a ≠ 0 := sub_ne_zero.mpr (Ne.symm hab)
    simp [hab, hba]

/-- The projectors are pairwise orthogonal idempotents, without a unitary hypothesis. -/
theorem orthogonal_idempotents {ψ : AddChar K ℂ} (hψ : ψ ≠ 1)
    (σ : Representation ℂ (Element K X) W) (a b : X) :
    projector ψ σ a * projector ψ σ b =
      if a = b then projector ψ σ a else 0 := by
  ext w
  change projector ψ σ a (projector ψ σ b w) = _
  rw [projector_of_eigen hψ σ a b _ (fun ξ => eigen ψ σ b ξ w)]
  split_ifs with hab
  · simp [hab]
  · rfl

omit [Fintype (Module.Dual K X)] in
/-- The actual commutation law after imposing the central character. -/
theorem modulation_translation_action (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z : K, σ (centralElement z) = ψ z • LinearMap.id)
    (ξ : Module.Dual K X) (x : X) (w : W) :
    σ (modulationElement ξ) (σ (translationElement x) w) =
      ψ (-(ξ x)) • σ (translationElement x) (σ (modulationElement ξ) w) := by
  calc
    σ (modulationElement ξ) (σ (translationElement x) w) =
        σ (modulationElement ξ * translationElement x) w := by
      rw [map_mul]
      rfl
    _ = σ (centralElement (-(ξ x)) *
        (translationElement x * modulationElement ξ)) w := by
      rw [modulation_translation h2]
    _ = ψ (-(ξ x)) • σ (translationElement x)
        (σ (modulationElement ξ) w) := by
      rw [map_mul, map_mul, hcentral]
      rfl

/-- Translation shifts a frequency by minus its position, with the source convention. -/
theorem translation_covariance (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z : K, σ (centralElement z) = ψ z • LinearMap.id)
    (a x : X) :
    σ (translationElement x) * projector ψ σ a =
      projector ψ σ (a - x) * σ (translationElement x) := by
  ext w
  change σ (translationElement x) (projector ψ σ a w) =
    projector ψ σ (a - x) (σ (translationElement x) w)
  simp only [projector_apply, map_smul, map_sum]
  congr 1
  apply Finset.sum_congr rfl
  intro ξ _
  rw [modulation_translation_action ψ h2 σ hcentral, ← mul_smul,
    ← ψ.map_add_eq_mul]
  congr 2
  simp only [map_sub]
  abel

/-- Every nonzero target has a nonzero vector in the zero-frequency fiber.
Completeness first gives a nonzero projector value; an invertible translation
moves its frequency to zero. No irreducibility or target dimension is assumed. -/
theorem nonzero_zero_fiber [Fintype X] [FiniteDimensional K X] [Nontrivial W]
    (ψ : AddChar K ℂ) (hψ : ψ ≠ 1) (h2 : (2 : K) ≠ 0)
    (σ : Representation ℂ (Element K X) W)
    (hcentral : ∀ z : K, σ (centralElement z) = ψ z • LinearMap.id) :
    ∃ w₀ : W, w₀ ≠ 0 ∧
      ∀ ξ : Module.Dual K X, σ (modulationElement ξ) w₀ = w₀ := by
  obtain ⟨w, hw⟩ := exists_ne (0 : W)
  have hex : ∃ a : X, projector ψ σ a w ≠ 0 := by
    by_contra! h
    have hh := congrArg (fun f : Module.End ℂ W => f w) (complete hψ σ)
    simp only [LinearMap.sum_apply, LinearMap.id_apply] at hh
    simp only [h, Finset.sum_const_zero] at hh
    exact hw hh.symm
  obtain ⟨a, ha⟩ := hex
  refine ⟨σ (translationElement a) (projector ψ σ a w), ?_, ?_⟩
  · intro hz
    apply ha
    have hh := congrArg (fun v : W => σ (translationElement (-a)) v) hz
    have hinv : σ (translationElement (-a))
        (σ (translationElement a) (projector ψ σ a w)) = projector ψ σ a w := by
      rw [← Module.End.mul_apply, ← map_mul, translationElement_mul]
      simp
    simpa only [hinv, map_zero] using hh
  · intro ξ
    rw [modulation_translation_action ψ h2 σ hcentral, eigen, map_smul,
      ← mul_smul, ← ψ.map_add_eq_mul]
    simp

end PaperXI.HeisenbergFrequency
