import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.FieldTheory.Finite.Basic

/-!
Protected realization and exact observation counts.  The source proves
statements about declared linear maps, not soundness of arbitrary annotations.
-/
namespace ProofPath
open Module

variable {K E R S W : Type*} [Field K]
  [AddCommGroup E] [Module K E] [AddCommGroup R] [Module K R]
  [AddCommGroup S] [Module K S] [AddCommGroup W] [Module K W]

def CorrectionImage (D : E →ₗ[K] R) (p : E →ₗ[K] S) : Submodule K R :=
  p.ker.map D

theorem protected_iff_correction (D : E →ₗ[K] R) (p : E →ₗ[K] S) (x : E) :
    (∃ y, D y = 0 ∧ p y = p x) ↔ D x ∈ CorrectionImage D p := by
  constructor
  · rintro ⟨y, hy, hpy⟩
    exact ⟨x - y, by simp [hpy], by simp [hy]⟩
  · rintro ⟨h, hh, he⟩
    have hp : p h = 0 := hh
    exact ⟨x - h, by simp [he], by simp [hp]⟩

theorem obstruction_sound (D : E →ₗ[K] R) (p : E →ₗ[K] S) (x : E)
    (l : R →ₗ[K] K) (hz : ∀ h, p h = 0 → l (D h) = 0)
    (hne : l (D x) ≠ 0) : ¬ ∃ y, D y = 0 ∧ p y = p x := by
  intro h
  rcases (protected_iff_correction D p x).mp h with ⟨v, hv, he⟩
  exact hne (he ▸ hz v hv)

theorem protected_alternative (D : E →ₗ[K] R) (p : E →ₗ[K] S) (x : E) :
    (¬ ∃ y, D y = 0 ∧ p y = p x) ↔
    ∃ l : R →ₗ[K] K, (∀ h, p h = 0 → l (D h) = 0) ∧ l (D x) = 1 := by
  constructor
  · intro hn
    have hx : D x ∉ CorrectionImage D p :=
      fun h => hn ((protected_iff_correction D p x).mpr h)
    obtain ⟨l, hl, hz⟩ :=
      Submodule.exists_dual_map_eq_bot_of_notMem hx inferInstance
    have vanish : ∀ h, p h = 0 → l (D h) = 0 := by
      intro h hp
      have hm : l (D h) ∈ (CorrectionImage D p).map l :=
        ⟨D h, ⟨h, hp, rfl⟩, rfl⟩
      simpa [hz] using hm
    refine ⟨(l (D x))⁻¹ • l, ?_, ?_⟩
    · intro h hp
      simp [vanish h hp]
    · simp [hl]
  · rintro ⟨l, hz, hone⟩
    exact obstruction_sound D p x l hz (by rw [hone]; exact one_ne_zero)

/-- Translation by a chosen point classifies a nonempty linear fiber. -/
def kernelEquivFiber (T : E →ₗ[K] R) (x₀ : E) :
    T.ker ≃ {y : E // T y = T x₀} where
  toFun h := ⟨x₀ + h, by simp⟩
  invFun y := ⟨y - x₀, by simp [y.property]⟩
  left_inv h := by ext; simp
  right_inv y := by ext; simp

theorem fiber_card [Fintype K] [Fintype E] (T : E →ₗ[K] R) (x₀ : E) :
    Nat.card {y : E // T y = T x₀} =
      Fintype.card K ^ finrank K T.ker := by
  classical
  rw [← Nat.card_congr (kernelEquivFiber T x₀), Nat.card_eq_fintype_card]
  exact Module.card_eq_pow_finrank

def observationMap (T : E →ₗ[K] R) (Q : E →ₗ[K] W) : T.ker →ₗ[K] W :=
  Q.comp T.ker.subtype

/-- Every attained observation fiber is a translate of the same kernel. -/
def observationKernelEquiv (T : E →ₗ[K] R) (Q : E →ₗ[K] W) (x₀ : E) :
    (observationMap T Q).ker ≃ {y : E // T y = T x₀ ∧ Q y = Q x₀} where
  toFun h := ⟨x₀ + h.val.val, by
    have ht : T h.val.val = 0 := h.val.property
    have hq : Q h.val.val = 0 := h.property
    simp [ht, hq]⟩
  invFun y := ⟨⟨y - x₀, by simp [y.property.1]⟩, by
    change Q (y.val - x₀) = 0
    simp [y.property.2]⟩
  left_inv h := by ext; simp
  right_inv y := by ext; simp

theorem observation_fiber_card [Fintype K] [Fintype E]
    (T : E →ₗ[K] R) (Q : E →ₗ[K] W) (x₀ : E) :
    Nat.card {y : E // T y = T x₀ ∧ Q y = Q x₀} =
      Fintype.card K ^ finrank K (observationMap T Q).ker := by
  classical
  rw [← Nat.card_congr (observationKernelEquiv T Q x₀), Nat.card_eq_fintype_card]
  exact Module.card_eq_pow_finrank

theorem observation_rank_nullity [FiniteDimensional K E]
    (T : E →ₗ[K] R) (Q : E →ₗ[K] W) :
    finrank K (observationMap T Q).range + finrank K (observationMap T Q).ker =
      finrank K T.ker :=
  (observationMap T Q).finrank_range_add_finrank_ker

theorem exact_observation_count [Fintype K] [Fintype E]
    (T : E →ₗ[K] R) (Q : E →ₗ[K] W) (x₀ : E) :
    Nat.card {y : E // T y = T x₀} =
      Nat.card {y : E // T y = T x₀ ∧ Q y = Q x₀} *
        Fintype.card K ^ finrank K (observationMap T Q).range := by
  classical
  rw [fiber_card, observation_fiber_card,
    ← observation_rank_nullity T Q, pow_add, mul_comm]

/-- Original protected constraints are exactly a fiber of the stacked map. -/
theorem stacked_fiber (D : E →ₗ[K] R) (p : E →ₗ[K] S) (x y : E) :
    (D.prod p) y = (0, p x) ↔ D y = 0 ∧ p y = p x := by
  simp

end ProofPath
