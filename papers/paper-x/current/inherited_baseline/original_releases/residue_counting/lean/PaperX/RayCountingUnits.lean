import Mathlib.NumberTheory.NumberField.Units.Regulator

/-!
An actual arithmetic input for ray-class counting: powers of the existing fundamental units
are congruent to one modulo a nonzero integral ideal and positive at every real embedding.
Their logarithms still form a full-rank family. This does not prove a ray-class ideal-count
estimate, nor identify a fundamental domain for the complete ray-unit group.
-/

set_option autoImplicit false
noncomputable section

namespace PaperX.RayCountingUnits

open NumberField NumberField.Units
open scoped NumberField

variable (K : Type*) [Field K] [NumberField K]

/-- The actual reduction homomorphism on integral units. -/
def unitReduction (m : Ideal (𝓞 K)) : (𝓞 K)ˣ →* (𝓞 K ⧸ m)ˣ :=
  Units.map (Ideal.Quotient.mk m).toMonoidHom

/-- The finite-modulus congruence subgroup. -/
def congruenceUnits (m : Ideal (𝓞 K)) : Subgroup (𝓞 K)ˣ :=
  (unitReduction K m).ker

omit [NumberField K] in
theorem mem_congruenceUnits_iff (m : Ideal (𝓞 K)) (u : (𝓞 K)ˣ) :
    u ∈ congruenceUnits K m ↔ (u : 𝓞 K) - 1 ∈ m := by
  change unitReduction K m u = 1 ↔ _
  rw [← Units.val_inj]
  exact Ideal.Quotient.mk_eq_one_iff_sub_mem (u : 𝓞 K)

theorem congruenceUnits_finiteIndex (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    (congruenceUnits K m).FiniteIndex := by
  let : Finite (𝓞 K ⧸ m) := Ring.HasFiniteQuotients.finiteQuotient hm
  exact Subgroup.finiteIndex_ker (unitReduction K m)

/-- Doubling the order of the finite residue-unit group also imposes total positivity. -/
def rayExponent (m : Ideal (𝓞 K)) : ℕ := 2 * Nat.card (𝓞 K ⧸ m)ˣ

theorem rayExponent_pos (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    0 < rayExponent K m := by
  let : Finite (𝓞 K ⧸ m) := Ring.HasFiniteQuotients.finiteQuotient hm
  exact Nat.mul_pos (by decide) Nat.card_pos

omit [NumberField K] in
theorem pow_rayExponent_mem (m : Ideal (𝓞 K)) (u : (𝓞 K)ˣ) :
    u ^ rayExponent K m ∈ congruenceUnits K m := by
  change unitReduction K m (u ^ rayExponent K m) = 1
  rw [map_pow, rayExponent, Nat.mul_comm 2, pow_mul, pow_card_eq_one', one_pow]

omit [NumberField K] in
theorem pow_rayExponent_real_pos (m : Ideal (𝓞 K)) (u : (𝓞 K)ˣ)
    (σ : K →+* ℝ) :
    0 < σ ((u ^ rayExponent K m : (𝓞 K)ˣ) : K) := by
  rw [NumberField.Units.coe_pow, map_pow, rayExponent, Nat.mul_comm 2, pow_mul]
  exact sq_pos_of_ne_zero (pow_ne_zero _ ((map_ne_zero σ).mpr (NumberField.Units.coe_ne_zero u)))

theorem isMaxRank_pow {u : Fin (rank K) → (𝓞 K)ˣ} (hu : IsMaxRank u)
    {n : ℕ} (hn : n ≠ 0) : IsMaxRank (fun i => u i ^ n) := by
  have hn' : (n : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hn
  convert hu.units_smul (fun _ => Units.mk0 (n : ℝ) hn') using 1
  funext i
  change logEmbedding K (Additive.ofMul (u i ^ n)) =
    (n : ℝ) • logEmbedding K (Additive.ofMul (u i))
  rw [ofMul_pow, map_nsmul, Nat.cast_smul_eq_nsmul]

/-- A concrete full-rank family satisfying the finite and all real-place ray conditions. -/
def rayFamily (m : Ideal (𝓞 K)) : Fin (rank K) → (𝓞 K)ˣ :=
  fun i => fundSystem K i ^ rayExponent K m

theorem rayFamily_isMaxRank (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    IsMaxRank (rayFamily K m) :=
  isMaxRank_pow K (isMaxRank_fundSystem K) (rayExponent_pos K m hm).ne'

theorem rayFamily_mem (m : Ideal (𝓞 K)) (i : Fin (rank K)) :
    (rayFamily K m i : 𝓞 K) - 1 ∈ m :=
  (mem_congruenceUnits_iff K m _).mp (pow_rayExponent_mem K m _)

theorem rayFamily_real_pos (m : Ideal (𝓞 K)) (i : Fin (rank K)) (σ : K →+* ℝ) :
    0 < σ (rayFamily K m i : K) :=
  pow_rayExponent_real_pos K m _ σ

theorem rayFamily_closure_finiteIndex (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    (Subgroup.closure (Set.range (rayFamily K m))).FiniteIndex :=
  isMaxRank_iff_closure_finiteIndex.mp (rayFamily_isMaxRank K m hm)

theorem rayFamily_regulator_pos (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    0 < regOfFamily (rayFamily K m) :=
  regOfFamily_pos (rayFamily_isMaxRank K m hm)

/-- Positivity is imposed on actual real field embeddings, rather than on local labels. -/
def totallyPositiveUnits : Subgroup (𝓞 K)ˣ where
  carrier := {u | ∀ σ : K →+* ℝ, 0 < σ (u : K)}
  one_mem' := by intro σ; simp
  mul_mem' := by
    intro u v hu hv σ
    rw [NumberField.Units.coe_mul, map_mul]
    exact mul_pos (hu σ) (hv σ)
  inv_mem' := by
    intro u hu σ
    rw [← zpow_neg_one u, NumberField.Units.coe_zpow, map_zpow₀, zpow_neg_one]
    exact inv_pos.mpr (hu σ)

/-- The actual ray-unit subgroup for finite modulus `m` and every real place. -/
def rayUnits (m : Ideal (𝓞 K)) : Subgroup (𝓞 K)ˣ :=
  congruenceUnits K m ⊓ totallyPositiveUnits K

omit [NumberField K] in
theorem mem_rayUnits_iff (m : Ideal (𝓞 K)) (u : (𝓞 K)ˣ) :
    u ∈ rayUnits K m ↔
      (u : 𝓞 K) - 1 ∈ m ∧ ∀ σ : K →+* ℝ, 0 < σ (u : K) := by
  exact and_congr_left (fun _ => mem_congruenceUnits_iff K m u)

theorem rayFamily_mem_rayUnits (m : Ideal (𝓞 K)) (i : Fin (rank K)) :
    rayFamily K m i ∈ rayUnits K m :=
  ⟨pow_rayExponent_mem K m _, rayFamily_real_pos K m i⟩

theorem rayUnits_finiteIndex (m : Ideal (𝓞 K)) (hm : m ≠ ⊥) :
    (rayUnits K m).FiniteIndex := by
  let := rayFamily_closure_finiteIndex K m hm
  apply Subgroup.finiteIndex_of_le (H := Subgroup.closure (Set.range (rayFamily K m)))
  rw [Subgroup.closure_le]
  rintro _ ⟨i, rfl⟩
  exact rayFamily_mem_rayUnits K m i

/-- The real-place condition is not the automatically nonnegative absolute-value map. -/
theorem neg_one_not_rayUnits_rat (m : Ideal (𝓞 ℚ)) :
    (-1 : (𝓞 ℚ)ˣ) ∉ rayUnits ℚ m := by
  intro h
  have hp := h.2 (algebraMap ℚ ℝ)
  norm_num [NumberField.Units.coe_neg_one] at hp

end PaperX.RayCountingUnits
