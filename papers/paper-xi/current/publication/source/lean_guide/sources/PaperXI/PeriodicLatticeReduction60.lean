import PaperXI.ActualELatticeNormalizer59
import Mathlib.Algebra.Ring.Periodic

/-!
# Finite reduction of the literal lattice-chain conditions

A positive period given by a base-field scalar reduces the entire integer
chain to finitely many levels for every base-field linear automorphism.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PeriodicLatticeReduction60
open ActualELatticeNormalizer59
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- The exact preservation and adjacent-congruence test at one chain level. -/
def levelCondition (L : ℤ → AddSubgroup V) (g : V ≃ₗ[K] V) (i : ℤ) : Prop :=
  (∀ v, g v ∈ L i ↔ v ∈ L i) ∧ (∀ v ∈ L i, g v - v ∈ L (i + 1))

/-- Multiplication by a base-field unit transfers each one-level condition. -/
theorem levelCondition_shift (L : ℤ → AddSubgroup V) (c : Kˣ) (r : ℤ)
    (hperiod : ∀ i v, (c : K) • v ∈ L (i + r) ↔ v ∈ L i)
    (g : V ≃ₗ[K] V) (i : ℤ) :
    levelCondition L g (i + r) ↔ levelCondition L g i := by
  have hmap (v : V) : g ((c : K) • v) = (c : K) • g v := g.map_smul _ _
  have hdiff (v : V) : g ((c : K) • v) - (c : K) • v = (c : K) • (g v - v) := by
    rw [hmap, smul_sub]
  constructor
  · rintro ⟨hg, hd⟩
    constructor
    · intro v
      have h := hg ((c : K) • v)
      rwa [hmap, hperiod, hperiod] at h
    · intro v hv
      have h := hd ((c : K) • v) ((hperiod i v).mpr hv)
      rw [hdiff, show i + r + 1 = (i + 1) + r by omega, hperiod] at h
      exact h
  · rintro ⟨hg, hd⟩
    constructor
    · intro v
      obtain ⟨w, rfl⟩ := (LinearEquiv.smulOfNeZero K V (c : K) c.ne_zero).surjective v
      change g ((c : K) • w) ∈ L (i + r) ↔ (c : K) • w ∈ L (i + r)
      rw [hmap, hperiod, hperiod]
      exact hg w
    · intro v hv
      obtain ⟨w, rfl⟩ := (LinearEquiv.smulOfNeZero K V (c : K) c.ne_zero).surjective v
      change (c : K) • w ∈ L (i + r) at hv
      change g ((c : K) • w) - (c : K) • w ∈ L (i + r + 1)
      rw [hdiff, show i + r + 1 = (i + 1) + r by omega, hperiod]
      exact hd w ((hperiod i w).mp hv)

/-- The level predicate is literally periodic as a `Prop`-valued function. -/
theorem levelCondition_periodic (L : ℤ → AddSubgroup V) (c : Kˣ) (r : ℤ)
    (hperiod : ∀ i v, (c : K) • v ∈ L (i + r) ↔ v ∈ L i)
    (g : V ≃ₗ[K] V) : Function.Periodic (levelCondition L g) r := by
  intro i
  exact propext (levelCondition_shift L c r hperiod g i)

/-- All infinitely many congruence conditions reduce to one positive period. -/
theorem mem_firstCongruence_iff_fin (L : ℤ → AddSubgroup V) (c : Kˣ) (r : ℕ)
    (hr : 0 < r)
    (hperiod : ∀ i v, (c : K) • v ∈ L (i + (r : ℤ)) ↔ v ∈ L i)
    (g : V ≃ₗ[K] V) :
    g ∈ firstCongruence L ↔ ∀ j : Fin r, levelCondition L g (j.val : ℤ) := by
  constructor
  · intro h j
    exact ⟨h.1 j.val, h.2 j.val⟩
  · intro h
    have hall : ∀ i : ℤ, levelCondition L g i := by
      intro i
      have hp := levelCondition_periodic L c (r : ℤ) hperiod g
      have hm := hp.sub_zsmul_eq (x := i) (i / (r : ℤ))
      have he : i - (i / (r : ℤ)) • (r : ℤ) = i % (r : ℤ) := by
        simp only [zsmul_eq_mul, Int.cast_id, Int.emod_def, mul_comm]
      rw [he] at hm
      rw [← hm]
      have hn : 0 ≤ i % (r : ℤ) := Int.emod_nonneg i (by omega)
      have hl : i % (r : ℤ) < (r : ℤ) := Int.emod_lt_of_pos i (by omega)
      let j : Fin r := ⟨(i % (r : ℤ)).toNat, by omega⟩
      have hj : (j.val : ℤ) = i % (r : ℤ) := by
        dsimp [j]
        exact Int.toNat_of_nonneg hn
      simpa only [hj] using h j
    exact ⟨fun i => (hall i).1, fun i => (hall i).2⟩

end PaperXI.PeriodicLatticeReduction60
