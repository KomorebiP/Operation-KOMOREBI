import PaperXI.CyclicInducedDegree

/-! Explicit wrap coefficients in the Frobenius-indexed induced basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicInduced
open scoped Classical
variable {G : Type*} [Group G] {n : ℕ} [NeZero n]
variable (d : G →* Multiplicative (ZMod n)) (φ : G)
variable (hφ : d φ = Multiplicative.ofAdd (1 : ZMod n))
variable (χ : d.ker →* ℂˣ)

/-- The scalar coefficient is represented by the discrepancy in integer representatives. -/
theorem cyclicWeight_phi_value (j : ZMod n) :
    cyclicWeight d φ hφ χ φ j =
      χ ⟨φ ^ ((j.val : ℤ) + 1 - ((j + 1).val : ℤ)), by
        apply Multiplicative.toAdd.injective
        simp [map_zpow, hφ, toAdd_zpow, zsmul_eq_mul]⟩ := by
  apply congrArg χ
  apply Subtype.ext
  change φ ^ (-((d φ * Multiplicative.ofAdd j).toAdd.val : ℤ)) * φ *
    (φ ^ (-((d (cyclicRep φ (d φ * Multiplicative.ofAdd j) * φ))⁻¹).toAdd.val : ℤ))⁻¹ =
      φ ^ ((j.val : ℤ) + 1 - ((j + 1).val : ℤ))
  have hd : d (cyclicRep φ (d φ * Multiplicative.ofAdd j) * φ) =
      (Multiplicative.ofAdd j)⁻¹ := by
    rw [map_mul, cyclicRep_degree d φ hφ]
    simp
  rw [hd, inv_inv, hφ]
  change φ ^ (-((1 + j).val : ℤ)) * φ * (φ ^ (-(j.val : ℤ)))⁻¹ =
    φ ^ ((j.val : ℤ) + 1 - ((j + 1).val : ℤ))
  rw [← zpow_neg, neg_neg]
  rw [← zpow_add_one, ← zpow_add]
  congr 1
  rw [add_comm (1 : ZMod n) j]
  omega

/-- A full cycle is an element of the inducing subgroup. -/
def period : d.ker :=
  ⟨φ ^ (n : ℤ), by
    apply Multiplicative.toAdd.injective
    simp [hφ]⟩

/-- The integer discrepancy vanishes before the last residue. -/
theorem val_succ_of_lt (j : ZMod n) (hj : j.val + 1 < n) :
    (j + 1).val = j.val + 1 := by
  have he : j + 1 = ((j.val + 1 : ℕ) : ZMod n) := by simp
  rw [he, ZMod.val_natCast, Nat.mod_eq_of_lt hj]

/-- At the last residue the successor returns to zero. -/
theorem val_succ_of_last (j : ZMod n) (hj : j.val + 1 = n) :
    (j + 1).val = 0 := by
  have he : j + 1 = ((j.val + 1 : ℕ) : ZMod n) := by simp
  rw [he, hj]
  simp

/-- Non-wrapping Frobenius steps have scalar one. -/
theorem cyclicWeight_phi_of_lt (j : ZMod n) (hj : j.val + 1 < n) :
    cyclicWeight d φ hφ χ φ j = 1 := by
  rw [cyclicWeight_phi_value]
  calc χ _ = χ 1 := by
         apply congrArg χ
         apply Subtype.ext
         change φ ^ ((j.val : ℤ) + 1 - ((j + 1).val : ℤ)) = 1
         rw [val_succ_of_lt j hj]
         simp
       _ = 1 := map_one χ

/-- The unique wrap step carries the actual value of the inducing character at `φ^n`. -/
theorem cyclicWeight_phi_of_last (j : ZMod n) (hj : j.val + 1 = n) :
    cyclicWeight d φ hφ χ φ j = χ (period d φ hφ) := by
  rw [cyclicWeight_phi_value]
  apply congrArg χ
  apply Subtype.ext
  change φ ^ ((j.val : ℤ) + 1 - ((j + 1).val : ℤ)) = φ ^ (n : ℤ)
  rw [val_succ_of_last j hj]
  congr 1
  omega

section Degree
variable (ν : G →* Multiplicative ℤ)
variable (hν : ν φ = Multiplicative.ofAdd (1 : ℤ))
variable (ξ : TameDegree.degreeSubgroup ν n →* ℂˣ)

/-- The source's full Frobenius period, as an actual subgroup element. -/
def degreePeriod : TameDegree.degreeSubgroup ν n :=
  period (TameDegree.degreeMod ν n) φ (degreeMod_phi ν φ hν n)

omit [NeZero n] in
@[simp] theorem degreePeriod_coe : (degreePeriod φ ν hν (n := n) : G) = φ ^ (n : ℤ) := rfl

/-- Before wrap, the source Frobenius basis coefficient equals one. -/
theorem degreeWeight_phi_of_lt (j : ZMod n) (hj : j.val + 1 < n) :
    degreeWeight ν φ hν n ξ φ j = 1 :=
  cyclicWeight_phi_of_lt (TameDegree.degreeMod ν n) φ (degreeMod_phi ν φ hν n) ξ j hj

/-- At wrap, the source basis coefficient is exactly the period character value. -/
theorem degreeWeight_phi_of_last (j : ZMod n) (hj : j.val + 1 = n) :
    degreeWeight ν φ hν n ξ φ j = ξ (degreePeriod φ ν hν) :=
  cyclicWeight_phi_of_last (TameDegree.degreeMod ν n) φ (degreeMod_phi ν φ hν n) ξ j hj

/-- Explicit shift along the non-wrapping part of the induced basis. -/
theorem degreeBasis_phi_of_lt (j : ZMod n) (hj : j.val + 1 < n) :
    degreeInduced ν n ξ φ (degreeBasis ν φ hν n ξ j) =
      degreeBasis ν φ hν n ξ (j + 1) := by
  rw [degreeBasis_action_phi, degreeWeight_phi_of_lt φ ν hν ξ j hj]
  simp

/-- Explicit closing step of the induced basis, including the case `n = 1`. -/
theorem degreeBasis_phi_of_last (j : ZMod n) (hj : j.val + 1 = n) :
    degreeInduced ν n ξ φ (degreeBasis ν φ hν n ξ j) =
      (ξ (degreePeriod φ ν hν) : ℂ) • degreeBasis ν φ hν n ξ 0 := by
  rw [degreeBasis_action_phi, degreeWeight_phi_of_last φ ν hν ξ j hj]
  have he : j + 1 = (0 : ZMod n) := by
    apply ZMod.val_injective
    simpa using val_succ_of_last j hj
  rw [he]
end Degree

end PaperXI.CyclicInduced
