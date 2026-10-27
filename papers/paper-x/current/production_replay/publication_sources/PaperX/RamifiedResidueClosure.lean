module

public import PaperX.FrobeniusArtinDomination
public import Mathlib.Analysis.SpecialFunctions.Pow.Continuity
public import Mathlib.Tactic.NormNum

/-!
# Finite ramified Euler factors and nonvanishing closure

For a supplied finite list of prime-ideal norms at least two, the correction
factor has a finite nonzero boundary value. This discharges the correction
limit in the residue bridge. It does not prove that any particular list is the
full ramified set: that identification is still part of the factorization.
-/
@[expose] public section
set_option autoImplicit false
noncomputable section
open Filter NumberField
open scoped Topology BigOperators
namespace PaperX.RamifiedResidueClosure

/-- The Euler factor retained on the full-zeta side at a removed prime. -/
def localFactor (q : ℕ) (s : ℝ) : ℂ := (1 - (q : ℂ) ^ (-(s : ℂ)))⁻¹

def localBoundary (q : ℕ) : ℂ := (1 - (q : ℂ)⁻¹)⁻¹

theorem one_sub_inv_ne_zero (q : ℕ) (hq : 2 ≤ q) : (1 - (q : ℂ)⁻¹) ≠ 0 := by
  have hq0 : (q : ℂ) ≠ 0 := Nat.cast_ne_zero.mpr (by omega)
  intro hz
  have hi : (q : ℂ)⁻¹ = 1 := (sub_eq_zero.mp hz).symm
  have hq1 : (q : ℂ) = 1 := by
    calc
      (q : ℂ) = (q : ℂ) * (q : ℂ)⁻¹ := by rw [hi, mul_one]
      _ = 1 := mul_inv_cancel₀ hq0
  have hq1' : q = 1 := by exact_mod_cast hq1
  omega

theorem localBoundary_ne_zero (q : ℕ) (hq : 2 ≤ q) : localBoundary q ≠ 0 :=
  inv_ne_zero (one_sub_inv_ne_zero q hq)

theorem localFactor_limit (q : ℕ) (hq : 2 ≤ q) :
    Tendsto (localFactor q) (𝓝 (1 : ℝ)) (𝓝 (localBoundary q)) := by
  let : NeZero (q : ℂ) := ⟨Nat.cast_ne_zero.mpr (by omega)⟩
  have hc : Continuous (fun s : ℝ => (q : ℂ) ^ (-(s : ℂ))) :=
    (continuous_const_cpow (q : ℂ)).comp Complex.continuous_ofReal.neg
  have hp : Tendsto (fun s : ℝ => (q : ℂ) ^ (-(s : ℂ)))
      (𝓝 (1 : ℝ)) (𝓝 (q : ℂ)⁻¹) := by
    simpa only [Complex.ofReal_one, Complex.cpow_neg_one] using hc.tendsto 1
  exact (tendsto_const_nhds.sub hp).inv₀ (one_sub_inv_ne_zero q hq)

section Finite
variable {J : Type*} [Fintype J] (q : J → ℕ)

def correction (s : ℝ) : ℂ := ∏ j, localFactor (q j) s

def correctionBoundary : ℂ := ∏ j, localBoundary (q j)

theorem correctionBoundary_ne_zero (hq : ∀ j, 2 ≤ q j) : correctionBoundary q ≠ 0 := by
  classical
  exact Finset.prod_ne_zero_iff.mpr (fun j _ => localBoundary_ne_zero (q j) (hq j))

theorem correction_limit (hq : ∀ j, 2 ≤ q j) :
    Tendsto (correction q) (𝓝[>] (1 : ℝ)) (𝓝 (correctionBoundary q)) :=
  (tendsto_finsetProd Finset.univ (fun j _ => localFactor_limit (q j) (hq j))).mono_left
    nhdsWithin_le_nhds
end Finite

section Closure
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
variable [Algebra K L] [IsGalois K L]
variable {I J : Type*} [Fintype I] [Fintype J]
variable (q : J → ℕ) (hq : ∀ j, 2 ≤ q j)
variable {F : I → ℝ → ℂ} {v : I → ℂ}
include hq

/-- Domination, positive actual number-field residues, and the finite correction
limit are proved internally. Only the global factorization and the boundary
limits of its regular factors are supplied. -/
theorem finite_correction_factors_nonzero
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1, NumberField.dedekindZeta L (s : ℂ) =
      PaperX.FrobeniusArtinDomination.idealArtinSeries K L 1 s *
        (correction q s * ∏ i, F i s))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    ∀ i, v i ≠ 0 :=
  (PaperX.FrobeniusArtinDomination.actual_factors_nonzero K L hfactor
    (correction_limit q hq) hF).2

/-- An explicit positive lower bound for the product of the limiting regular
factors, including the complete finite Euler correction. -/
theorem finite_correction_product_lower_bound
    (hfactor : ∀ᶠ s : ℝ in 𝓝[>] 1, NumberField.dedekindZeta L (s : ℂ) =
      PaperX.FrobeniusArtinDomination.idealArtinSeries K L 1 s *
        (correction q s * ∏ i, F i s))
    (hF : ∀ i, Tendsto (F i) (𝓝[>] (1 : ℝ)) (𝓝 (v i))) :
    (NumberField.dedekindZeta_residue L / NumberField.dedekindZeta_residue K) /
      ‖correctionBoundary q‖ ≤ ‖∏ i, v i‖ := by
  apply (div_le_iff₀ (norm_pos_iff.mpr (correctionBoundary_ne_zero q hq))).mpr
  simpa only [norm_mul, mul_comm] using
    PaperX.FrobeniusArtinDomination.actual_product_ratio_bound K L hfactor
      (correction_limit q hq) hF
end Closure

/-- A norm-two omitted prime contributes a factor two, not one, at the boundary. -/
theorem norm_two_boundary : localBoundary 2 = 2 := by norm_num [localBoundary]

end PaperX.RamifiedResidueClosure
