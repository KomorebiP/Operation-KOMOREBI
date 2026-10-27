module
public import Mathlib.Analysis.Matrix.HermitianFunctionalCalculus
public import Mathlib.Analysis.Matrix.PosDef
public import Mathlib.Analysis.Normed.Algebra.MatrixExponential
public import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.ExpLog.Basic
public import Mathlib.Tactic
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.EuclideanTransfer
open Matrix NormedSpace
open scoped Matrix.Norms.Operator ComplexOrder
variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The power-series exponential, not a separately postulated transfer family. -/
noncomputable def transfer (H : Matrix n n ℂ) (e t : ℝ) : Matrix n n ℂ :=
  exp ((-t) • (H - e • (1 : Matrix n n ℂ)))

theorem shifted_hermitian (H : Matrix n n ℂ) (hH : H.IsHermitian) (e t : ℝ) :
    ((-t) • (H - e • (1 : Matrix n n ℂ))).IsHermitian := by
  exact (hH.sub (isHermitian_one.smul (IsSelfAdjoint.all e))).smul (IsSelfAdjoint.all (-t))

theorem transfer_hermitian (H : Matrix n n ℂ) (hH : H.IsHermitian) (e t : ℝ) :
    (transfer H e t).IsHermitian := (shifted_hermitian H hH e t).exp

theorem transfer_zero (H : Matrix n n ℂ) (e : ℝ) : transfer H e 0 = 1 := by
  simp [transfer]

theorem transfer_add (H : Matrix n n ℂ) (e t s : ℝ) :
    transfer H e (t+s) = transfer H e t * transfer H e s := by
  unfold transfer
  rw [neg_add, add_smul]
  exact Matrix.exp_add_of_commute _ _ (((Commute.refl _).smul_left (-t)).smul_right (-s))

theorem transfer_cfc (H : Matrix n n ℂ) (hH : H.IsHermitian) (e t : ℝ) :
    transfer H e t = cfc (fun x : ℝ => Real.exp ((-t)*(x-e))) H := by
  rw [cfc_comp' Real.exp (fun x : ℝ => (-t)*(x-e)) H]
  have hlin : cfc (fun x : ℝ => (-t)*(x-e)) H = (-t) • (H - e • (1 : Matrix n n ℂ)) := by
    rw [cfc_const_mul (-t) (fun x : ℝ => x-e) H,
      cfc_sub (fun x : ℝ => x) (fun _ : ℝ => e) H, cfc_id' ℝ H hH, cfc_const e H hH]
    simp only [Algebra.algebraMap_eq_smul_one]
  rw [hlin, CFC.real_exp_eq_normedSpace_exp (shifted_hermitian H hH e t).isSelfAdjoint]
  rfl

theorem transfer_spectrum (H : Matrix n n ℂ) (hH : H.IsHermitian) (e t : ℝ) :
    spectrum ℝ (transfer H e t) =
      (fun x : ℝ => Real.exp ((-t)*(x-e))) '' spectrum ℝ H := by
  rw [transfer_cfc H hH, cfc_map_spectrum (f := fun x : ℝ => Real.exp ((-t)*(x-e))) (a := H) hH.isSelfAdjoint]

theorem transfer_posDef (H : Matrix n n ℂ) (hH : H.IsHermitian) (e t : ℝ) :
    (transfer H e t).PosDef := by
  let ht := transfer_hermitian H hH e t
  rw [ht.posDef_iff_eigenvalues_pos]
  intro i
  have hi := ht.eigenvalues_mem_spectrum_real i
  rw [transfer_spectrum H hH] at hi
  obtain ⟨x, _, hx⟩ := hi
  rw [← hx]
  exact Real.exp_pos _

theorem transfer_spectrum_interval (H : Matrix n n ℂ) (hH : H.IsHermitian)
    (e t : ℝ) (ht : 0 ≤ t) (he : ∀ x ∈ spectrum ℝ H, e ≤ x) :
    spectrum ℝ (transfer H e t) ⊆ Set.Ioc 0 1 := by
  rw [transfer_spectrum H hH]
  rintro _ ⟨x, hx, rfl⟩
  exact ⟨Real.exp_pos _, Real.exp_le_one_iff.mpr (mul_nonpos_of_nonpos_of_nonneg
    (neg_nonpos.mpr ht) (sub_nonneg.mpr (he x hx)))⟩

/-- A minimum is defined only for a nonempty state space. -/
noncomputable def groundEnergy [Nonempty n] {H : Matrix n n ℂ} (hH : H.IsHermitian) : ℝ :=
  (Finset.univ.image hH.eigenvalues).min' (Finset.univ_nonempty.image _)

theorem ground_energy_le [Nonempty n] {H : Matrix n n ℂ} (hH : H.IsHermitian)
    (x : ℝ) (hx : x ∈ spectrum ℝ H) : groundEnergy hH ≤ x := by
  rw [hH.spectrum_real_eq_range_eigenvalues] at hx
  obtain ⟨i, rfl⟩ := hx
  exact Finset.min'_le _ _ (Finset.mem_image.mpr ⟨i, Finset.mem_univ _, rfl⟩)

theorem ground_energy_mem [Nonempty n] {H : Matrix n n ℂ} (hH : H.IsHermitian) :
    groundEnergy hH ∈ spectrum ℝ H := by
  rw [hH.spectrum_real_eq_range_eigenvalues]
  obtain ⟨i, _, hi⟩ := Finset.mem_image.mp (Finset.min'_mem _ (Finset.univ_nonempty.image hH.eigenvalues))
  exact ⟨i, hi⟩

theorem finite_euclidean_transfer [Nonempty n] (H : Matrix n n ℂ)
    (hH : H.IsHermitian) (t s : ℝ) (ht : 0 ≤ t) :
    (transfer H (groundEnergy hH) t).PosDef ∧
    transfer H (groundEnergy hH) (t+s) =
      transfer H (groundEnergy hH) t * transfer H (groundEnergy hH) s ∧
    spectrum ℝ (transfer H (groundEnergy hH) t) ⊆ Set.Ioc 0 1 := by
  exact ⟨transfer_posDef H hH _ _, transfer_add H _ _ _,
    transfer_spectrum_interval H hH _ _ ht (ground_energy_le hH)⟩
end KomorebiPaperVII.EuclideanTransfer
