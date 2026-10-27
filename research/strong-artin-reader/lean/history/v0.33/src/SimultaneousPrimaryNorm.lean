import SimultaneousOperatorNorm
import PrimaryBlockNorm

/-! Complete simultaneous classification on a supplied nilpotent primary block. -/
noncomputable section
namespace Komorebi.StrongArtin.SimultaneousNorm
open Komorebi.StrongArtin.NonsemisimpleNorm
open Polynomial
variable {k V I : Type*} [Field k] [AddCommGroup V] [Module k V]

/-- Away from eigenvalue one, local gauge directions eliminate the shared constraint. -/
theorem one_sub_surjective_of_primary_ne_one (T : Module.End k V) (lam : k)
    (hN : IsNilpotent (T - algebraMap k (Module.End k V) lam)) (hl : lam ≠ 1) :
    Function.Surjective (1-T : Module.End k V) := by
  have hu := aeval_isUnit_of_primary T lam hN (1-X)
    (by simpa using sub_ne_zero.mpr (Ne.symm hl))
  have hunit : IsUnit (1-T : Module.End k V) := by simpa using hu
  exact (end_unit_bijective hunit).2

/-- A non-one primary block has no additional simultaneous obstruction. -/
theorem simultaneous_primary_ne_one_iff (T : Module.End k V) (lam : k)
    (hN : IsNilpotent (T - algebraMap k (Module.End k V) lam))
    (hl0 : lam ≠ 0) (hl1 : lam ≠ 1) (m a : I → ℕ) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : ∀ i, (m i : k) ≠ 0) (e : I → V) :
    LocalizationSolvable T (fun i => m i * p ^ a i) e ↔
      ∀ i, e i ∈ LinearMap.range
        ((T - algebraMap k (Module.End k V) lam) ^ resonanceExponent (m i) p (a i) lam) := by
  rw [localization_iff_individual_of_one_sub_surjective T
    (one_sub_surjective_of_primary_ne_one T lam hN hl1)]
  simp only [(primary_norm_range_ker T lam hN _ p _ (hm _) hl0).1]

/-- Canonical invertible factor on an eigenvalue-one primary block. -/
theorem unipotent_norm_unit (T : Module.End k V) (hN : IsNilpotent (T-1))
    (m p a : ℕ) (hm : (m : k) ≠ 0) : IsUnit ((operatorNorm T m) ^ (p^a)) := by
  have hn : IsNilpotent (T - algebraMap k (Module.End k V) (1 : k)) := by simpa using hN
  have hu := aeval_isUnit_of_primary T 1 hn (normPolynomial k m)
    (by simpa using hm)
  have hu' : IsUnit (operatorNorm T m) := by simpa using hu
  exact hu'.pow _

/-- Normalizer is exactly S_m(T)^(p^a), with its unit witness supplied by nilpotence. -/
def unipotentNormalizer (T : Module.End k V) (hN : IsNilpotent (T-1))
    (m p a : ℕ) (hm : (m : k) ≠ 0) : (Module.End k V)ˣ :=
  (unipotent_norm_unit T hN m p a hm).unit

@[simp] theorem unipotentNormalizer_val (T : Module.End k V) (hN : IsNilpotent (T-1))
    (m p a : ℕ) (hm : (m : k) ≠ 0) :
    (↑(unipotentNormalizer T hN m p a hm) : Module.End k V) =
      (operatorNorm T m) ^ (p^a) := by
  exact (unipotent_norm_unit T hN m p a hm).unit_spec

theorem mixed_norm_factor_left (T : Module.End k V) (m p a : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] :
    operatorNorm T (m*p^a) = (operatorNorm T m)^(p^a) * (T-1)^(p^a-1) := by
  rw [operatorNorm_mixed_degree]
  have hc := (Commute.all ((X-1 : k[X])^(p^a-1))
    ((normPolynomial k m)^(p^a))).map (aeval T).toRingHom
  exact (by simpa using hc.eq)

/-- Exact unit-normalized mismatches. This is not just a leading-term approximation. -/
def normalizedUnipotentErrors (T : Module.End k V) (hN : IsNilpotent (T-1))
    (m a : I → ℕ) (p : ℕ) (hm : ∀ i, (m i : k) ≠ 0) (e : I → V) : I → V :=
  fun i => (↑((unipotentNormalizer T hN (m i) p (a i) (hm i))⁻¹) : Module.End k V) (e i)

/-- Remove invertible factors without changing the one shared correction. -/
theorem unipotent_localization_iff_powerFamily (T : Module.End k V)
    (hN : IsNilpotent (T-1)) (m a : I → ℕ) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : ∀ i, (m i : k) ≠ 0) (e : I → V) :
    LocalizationSolvable T (fun i => m i * p ^ a i) e ↔
      PowerFamilySolvable (T-1) (fun i => p ^ a i - 1)
        (normalizedUnipotentErrors T hN m a p hm e) := by
  rw [localization_iff_factored]
  have hnorm (i : I) : operatorNorm T (m i * p ^ a i) =
      (↑(unipotentNormalizer T hN (m i) p (a i) (hm i)) : Module.End k V) *
        (T-1)^(p^a i-1) := by
    rw [unipotentNormalizer_val, mixed_norm_factor_left]
  have hsign (z : V) : (1-T) (-z) = (T-1) z := by
    simp only [map_neg, LinearMap.sub_apply, Module.End.one_apply]
    abel
  have hsign' (z : V) : (T-1) (-z) = (1-T) z := by
    simp only [map_neg, LinearMap.sub_apply, Module.End.one_apply]
    abel
  constructor
  · rintro ⟨x,z,hz⟩
    refine ⟨x,fun i => -(z i),?_⟩
    intro i
    dsimp [normalizedUnipotentErrors]
    rw [hz i, hnorm, ← Module.End.mul_apply, ← mul_assoc, Units.inv_mul, one_mul]
    exact congrArg (fun v => ((T-1)^(p^a i-1)) (x+v)) (hsign' (z i)).symm
  · rintro ⟨x,z,hz⟩
    refine ⟨x,fun i => -(z i),?_⟩
    intro i
    have hi := congrArg (fun y => (↑(unipotentNormalizer T hN (m i) p (a i) (hm i)) :
      Module.End k V) y) (hz i)
    dsimp [normalizedUnipotentErrors] at hi
    rw [← Module.End.mul_apply, Units.mul_inv, Module.End.one_apply] at hi
    rw [hnorm, Module.End.mul_apply, hsign]
    exact hi

/-- Complete finite or infinite mixed-degree family criterion, given a least
p-part pivot. Only nilpotence of T-1, not a Jordan basis, is needed. -/
theorem unipotent_localization_iff_pivot (T : Module.End k V)
    (hN : IsNilpotent (T-1)) (m a : I → ℕ) (p : ℕ)
    [Fact (Nat.Prime p)] [CharP k p] (hm : ∀ i, (m i : k) ≠ 0) (e : I → V)
    (i₀ : I) (hmin : ∀ i, p ^ a i₀ ≤ p ^ a i) :
    let f := normalizedUnipotentErrors T hN m a p hm e
    LocalizationSolvable T (fun i => m i * p ^ a i) e ↔
      f i₀ ∈ LinearMap.range ((T-1) ^ (p ^ a i₀ - 1)) ∧
      ∀ i, f i - ((T-1) ^ (p ^ a i - p ^ a i₀)) (f i₀) ∈
        LinearMap.range ((T-1) ^ (p ^ a i)) := by
  dsimp only
  rw [unipotent_localization_iff_powerFamily]
  rw [← primePower_localization_iff T p]
  exact primePower_localization_iff_pivot T p a _ i₀ hmin

end Komorebi.StrongArtin.SimultaneousNorm
