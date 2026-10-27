import PaperXI.CyclicInducedDegree

/-! Exact subgroup character values of the monomial coefficients of actual induction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicInduced
open TameDegree
variable {G : Type*} [Group G] (ν : G →* Multiplicative ℤ)
variable (φ : G) (hφ : ν φ = Multiplicative.ofAdd (1 : ℤ))
variable (n : ℕ) [NeZero n] (χ : degreeSubgroup ν n →* ℂˣ)

/-- Exact unit-valued coefficient on the inducing subgroup. -/
theorem degreeWeight_kernel (h : degreeSubgroup ν n) (j : ZMod n) :
    degreeWeight ν φ hφ n χ h j = degreeCharacter ν φ n χ j h :=
  weight_kernel (degreeMod ν n) (cyclicRep φ) (cyclicRep_degree (degreeMod ν n) φ
    (degreeMod_phi ν φ hφ n)) χ h (Multiplicative.ofAdd j)

/-- The subgroup coefficient is literally the expected Frobenius conjugate character. -/
theorem degreeCharacter_apply (h : degreeSubgroup ν n) (j : ZMod n) :
    degreeCharacter ν φ n χ j h =
      χ ⟨φ ^ (-(j.val : ℤ)) * (h : G) * φ ^ (j.val : ℤ), by
        change degreeMod ν n (φ ^ (-(j.val : ℤ)) * (h : G) * φ ^ (j.val : ℤ)) = 1
        have hh : degreeMod ν n h = 1 := h.property
        simp only [map_mul, map_inv, map_zpow, zpow_neg, hh, mul_one, inv_mul_cancel]⟩ :=
  cyclicCharacter_apply (degreeMod ν n) φ χ j h

/-- On residue zero, the conjugated character is the original character. -/
theorem degreeCharacter_zero (h : degreeSubgroup ν n) :
    degreeCharacter ν φ n χ 0 h = χ h := by
  rw [degreeCharacter_apply]
  apply congrArg χ
  apply Subtype.ext
  simp

/-- Exact origin coefficient, as an equality of units. -/
theorem degreeWeight_zero (h : degreeSubgroup ν n) :
    degreeWeight ν φ hφ n χ h 0 = χ h := by
  rw [degreeWeight_kernel, degreeCharacter_zero]

variable {l : ℕ} (hdiv : n ∣ l)

/-- Restricting to a smaller degree subgroup gives the explicitly conjugated character. -/
theorem degreeWeight_restrict (h : degreeSubgroup ν l) (j : ZMod n) :
    degreeWeight ν φ hφ n χ h j =
      χ (conjugationInto ν n l hdiv (φ ^ (-(j.val : ℤ))) h) := by
  let h' : degreeSubgroup ν n := ⟨h, degreeSubgroup_le ν n l hdiv h.property⟩
  change degreeWeight ν φ hφ n χ (h' : G) j = _
  rw [degreeWeight_kernel, degreeCharacter_apply]
  apply congrArg χ
  apply Subtype.ext
  simp [h', conjugationInto_apply, zpow_neg]

/-- The zeroth tensor factor restricts without conjugation. -/
theorem degreeWeight_restrict_zero (h : degreeSubgroup ν l) :
    degreeWeight ν φ hφ n χ h 0 =
      χ ⟨h, degreeSubgroup_le ν n l hdiv h.property⟩ := by
  let h' : degreeSubgroup ν n := ⟨h, degreeSubgroup_le ν n l hdiv h.property⟩
  exact degreeWeight_zero ν φ hφ n χ h'

end PaperXI.CyclicInduced
