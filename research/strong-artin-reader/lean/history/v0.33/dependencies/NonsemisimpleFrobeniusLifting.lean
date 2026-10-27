import PrimaryBlockNorm
import FrobeniusSingleRestriction

/-! Transfer the nonsemisimple operator calculation to the ACTUAL square-zero
kernel and the original prescribed Frobenius root. No alternative equation system. -/
noncomputable section
namespace Komorebi.StrongArtin.SquareZeroH2
open Komorebi.StrongArtin.NonsemisimpleNorm
variable {G A B k V : Type} [Group G] [Ring A] [Ring B]
variable [Field k] [AddCommGroup V] [Module k V]

/-- Coordinates need linearity of the action, not a diagonalization. -/
structure FrobeniusLinearCoordinates (D : Datum G A B) (F : Aˣ) (k V : Type)
    [Field k] [AddCommGroup V] [Module k V] where
  coordinates : D.Kernel ≃+ V
  operator : Module.End k V
  conjugate_coordinates : ∀ x, coordinates (D.conjugate F x) = operator (coordinates x)

namespace FrobeniusLinearCoordinates
variable {D : Datum G A B} {F : Aˣ} (S : FrobeniusLinearCoordinates D F k V)

theorem conjugate_pow_coordinates (n : ℕ) (x : D.Kernel) :
    S.coordinates (D.conjugate (F^n) x) = (S.operator^n) (S.coordinates x) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ', D.conjugate_mul]
    change S.coordinates (D.conjugate F (D.conjugate (F^n) x)) = _
    rw [S.conjugate_coordinates, ih, pow_succ']
    rfl

theorem norm_coordinates (d : ℕ) (x : D.Kernel) :
    S.coordinates (D.frobeniusNorm F d x) = operatorNorm S.operator d (S.coordinates x) := by
  induction d with
  | zero => simp
  | succ n ih =>
    rw [D.frobeniusNorm_succ, map_add, ih, S.conjugate_pow_coordinates, operatorNorm_succ]
    rfl

/-- Exact criterion for the original lift problem, without semisimplicity. -/
theorem prescribed_power_iff_operator_image (U : Aˣ) (d : ℕ)
    (hU : D.q U = D.q (F^d)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = U) ↔
      S.coordinates (D.unitMismatch U (F^d) hU) ∈ LinearMap.range (operatorNorm S.operator d) := by
  rw [D.power_lifting_iff_norm_image]
  constructor
  · rintro ⟨x, hx⟩
    exact ⟨S.coordinates x, (S.norm_coordinates d x).symm.trans (congrArg S.coordinates hx)⟩
  · rintro ⟨y, hy⟩
    refine ⟨S.coordinates.symm y, S.coordinates.injective ?_⟩
    rw [S.norm_coordinates, S.coordinates.apply_symm_apply, hy]

/-- Prime-power prescriptions are controlled by a power of Ad(F)-1 on the actual kernel. -/
theorem prescribed_primePower_iff (U : Aˣ) (p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hU : D.q U = D.q (F^(p^a))) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^(p^a) = U) ↔
      S.coordinates (D.unitMismatch U (F^(p^a)) hU) ∈
        LinearMap.range ((S.operator - 1)^(p^a-1)) := by
  rw [S.prescribed_power_iff_operator_image, operatorNorm_primePower]

/-- Complete primary-block restriction criterion, including nilpotent Jordan directions. -/
theorem prescribed_primary_power_iff (U : Aˣ) (m p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : (m : k) ≠ 0)
    (lam : k) (hl : lam ≠ 0)
    (hN : IsNilpotent (S.operator - algebraMap k (Module.End k V) lam))
    (hU : D.q U = D.q (F^(m*p^a))) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^(m*p^a) = U) ↔
      S.coordinates (D.unitMismatch U (F^(m*p^a)) hU) ∈
        LinearMap.range ((S.operator - algebraMap k (Module.End k V) lam)^
          resonanceExponent m p a lam) := by
  rw [S.prescribed_power_iff_operator_image, (primary_norm_range_ker S.operator lam hN m p a hm hl).1]

/-- One local conjugator is absorbed into the chosen global Frobenius root. -/
theorem prescribed_primePower_gauge_iff (U : Aˣ) (p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hU : D.q U = D.q (F^(p^a))) :
    (∃ F' u : Aˣ, D.q F' = D.q F ∧ D.q u = 1 ∧ u * F'^(p^a) * u⁻¹ = U) ↔
      S.coordinates (D.unitMismatch U (F^(p^a)) hU) ∈
        LinearMap.range ((S.operator - 1)^(p^a-1)) := by
  rw [D.one_power_gauge_iff_strict, S.prescribed_primePower_iff]

end FrobeniusLinearCoordinates
end Komorebi.StrongArtin.SquareZeroH2
