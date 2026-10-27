import PaperXI.DyadicGauss

noncomputable section
set_option autoImplicit false
namespace PaperXI.Dyadic
open scoped BigOperators Classical
variable {ι κ : Type*} [Fintype ι] [Fintype κ]

def pairing (v x : ι → F2 × F2) : F2 :=
  ∑ i, ((v i).1 * (x i).2 + (v i).2 * (x i).1)

def translate (a v : ι → F2 × F2) : ι → F2 × F2 :=
  fun i => ((a i).1 + (v i).2, (a i).2 + (v i).1)

theorem quadratic_translate (a v x : ι → F2 × F2) :
    quadratic (translate a v) x = quadratic a x + pairing v x := by
  simp only [quadratic, pairing, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  simp only [plane, translate]
  ring

theorem arf_translate (a v : ι → F2 × F2) :
    arf (translate a v) = arf a + quadratic a v := by
  simp only [arf, quadratic, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  simp only [plane, translate]
  ring

theorem gauss_translate (a v : ι → F2 × F2) :
    (∑ x, sign (quadratic (translate a v) x)) =
      sign (quadratic a v) * ∑ x, sign (quadratic a x) := by
  rw [gauss_sum, gauss_sum, arf_translate, sign_add]
  ring

theorem arf_orthogonal (a : ι → F2 × F2) (b : κ → F2 × F2) :
    arf (Sum.elim a b) = arf a + arf b := by
  simp [arf, Fintype.sum_sum_type]

theorem gauss_orthogonal (a : ι → F2 × F2) (b : κ → F2 × F2) :
    (∑ x, sign (quadratic (Sum.elim a b) x)) =
      (∑ x, sign (quadratic a x)) * ∑ x, sign (quadratic b x) := by
  calc
    _ = sign (arf (Sum.elim a b)) * 2 ^ Fintype.card (ι ⊕ κ) := by
      convert gauss_sum (Sum.elim a b) using 1
      apply Finset.sum_congr
      · ext x
        simp
      · intro x _
        rfl
    _ = _ := by
      rw [gauss_sum a, gauss_sum b, arf_orthogonal, sign_add]
      simp only [Fintype.card_sum, pow_add]
      ring

theorem sign_orthogonal (a : ι → F2 × F2) (b : κ → F2 × F2) :
    sign (arf (Sum.elim a b)) = sign (arf a) * sign (arf b) := by
  rw [arf_orthogonal, sign_add]

@[simp] theorem arf_zero : arf (0 : ι → F2 × F2) = 0 := by
  simp [arf]

def anisotropic (i : ι) : ι → F2 × F2 := Pi.single i (1, 1)

theorem arf_anisotropic (i : ι) : arf (anisotropic i) = 1 := by
  classical
  unfold arf
  calc
    _ = ∑ j, if j = i then (1 : F2) else 0 := by
      apply Finset.sum_congr rfl
      intro j _
      by_cases h : j = i <;> simp [anisotropic, h]
    _ = 1 := by simp

theorem opposite_gauss (i : ι) :
    (∑ x, sign (quadratic (anisotropic i) x)) =
      -(∑ x, sign (quadratic (0 : ι → F2 × F2) x)) := by
  rw [gauss_sum, gauss_sum, arf_anisotropic, arf_zero, sign_zero, sign_one]
  ring

theorem both_arf [Nonempty ι] :
    (∃ a : ι → F2 × F2, arf a = 0) ∧ (∃ a : ι → F2 × F2, arf a = 1) := by
  constructor
  · exact ⟨0, arf_zero⟩
  · obtain ⟨i⟩ := ‹Nonempty ι›
    exact ⟨anisotropic i, arf_anisotropic i⟩

end PaperXI.Dyadic
