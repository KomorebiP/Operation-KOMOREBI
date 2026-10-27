import SimultaneousPowerFiltration
import OperatorNormPolynomial
import Mathlib.Tactic.Omega

/-! Actual shared correction shape, including independent local gauge variables. -/
noncomputable section
namespace Komorebi.StrongArtin.SimultaneousNorm
open Komorebi.StrongArtin.NonsemisimpleNorm
variable {k V I : Type*} [Field k] [AddCommGroup V] [Module k V]

def LocalizationSolvable (T : Module.End k V) (d : I → ℕ) (e : I → V) : Prop :=
  ∃ x : V, ∃ z : I → V, ∀ i,
    e i = operatorNorm T (d i) x + z i - (T ^ d i) (z i)

theorem operatorNorm_mul_one_sub (T : Module.End k V) (d : ℕ) :
    operatorNorm T d * (1-T) = 1-T^d := by
  exact geom_sum_mul_neg T d

theorem norm_gauge_factor (T : Module.End k V) (d : ℕ) (x z : V) :
    operatorNorm T d x + z - (T^d) z =
      operatorNorm T d (x + (1-T) z) := by
  rw [map_add, ← Module.End.mul_apply, operatorNorm_mul_one_sub]
  simp only [LinearMap.sub_apply, Module.End.one_apply]
  abel

theorem localization_iff_factored (T : Module.End k V) (d : I → ℕ) (e : I → V) :
    LocalizationSolvable T d e ↔
      ∃ x : V, ∃ z : I → V, ∀ i, e i = operatorNorm T (d i) (x + (1-T) (z i)) := by
  simp only [LocalizationSolvable, norm_gauge_factor]

/-- If 1-T is onto, independent conjugators solve all individual prescriptions
simultaneously, using the same global correction x=0. -/
theorem localization_iff_individual_of_one_sub_surjective (T : Module.End k V)
    (hT : Function.Surjective (1-T : Module.End k V)) (d : I → ℕ) (e : I → V) :
    LocalizationSolvable T d e ↔ ∀ i, e i ∈ LinearMap.range (operatorNorm T (d i)) := by
  rw [localization_iff_factored]
  constructor
  · rintro ⟨x,z,hz⟩ i
    exact ⟨x + (1-T) (z i), (hz i).symm⟩
  · intro he
    choose y hy using he
    choose z hz using fun i => hT (y i)
    exact ⟨0, z, fun i => by rw [zero_add, hz i, hy i]⟩

/-- Prime-power localization is a pure power-filtration problem for T-1. -/
theorem primePower_localization_iff (T : Module.End k V) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (a : I → ℕ) (e : I → V) :
    LocalizationSolvable T (fun i => p ^ a i) e ↔
      PowerFamilySolvable (T-1) (fun i => p ^ a i - 1) e := by
  rw [localization_iff_factored]
  simp only [operatorNorm_primePower]
  constructor <;> rintro ⟨x,z,hz⟩ <;> refine ⟨x,fun i => -(z i),?_⟩ <;> intro i
  · have he : (T-1) (-(z i)) = (1-T) (z i) := by
      simp only [map_neg, LinearMap.sub_apply, Module.End.one_apply]
      abel
    rw [he]
    exact hz i
  · have he : (1-T) (-(z i)) = (T-1) (z i) := by
      simp only [map_neg, LinearMap.sub_apply, Module.End.one_apply]
      abel
    rw [he]
    exact hz i

/-- A least-degree pivot gives a complete criterion with no nilpotent,
diagonalization, finite-dimension, or finite-family hypothesis. -/
theorem primePower_localization_iff_pivot (T : Module.End k V) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (a : I → ℕ) (e : I → V)
    (i₀ : I) (hmin : ∀ i, p ^ a i₀ ≤ p ^ a i) :
    LocalizationSolvable T (fun i => p ^ a i) e ↔
      e i₀ ∈ LinearMap.range ((T-1) ^ (p ^ a i₀ - 1)) ∧
      ∀ i, e i - ((T-1) ^ (p ^ a i - p ^ a i₀)) (e i₀) ∈
        LinearMap.range ((T-1) ^ (p ^ a i)) := by
  rw [primePower_localization_iff,
    powerFamily_iff_pivot (T-1) (fun i => p ^ a i - 1) e i₀
      (fun i => Nat.sub_le_sub_right (hmin i) 1)]
  have hp := (Fact.out : Nat.Prime p).pos
  have h0 : 0 < p ^ a i₀ := pow_pos hp _
  have hdiff (i : I) : (p ^ a i - 1) - (p ^ a i₀ - 1) = p ^ a i - p ^ a i₀ := by
    have hi := hmin i
    omega
  have hs (i : I) : p ^ a i - 1 + 1 = p ^ a i := Nat.sub_add_cancel (pow_pos hp _)
  simp only [hdiff, hs]

end Komorebi.StrongArtin.SimultaneousNorm
