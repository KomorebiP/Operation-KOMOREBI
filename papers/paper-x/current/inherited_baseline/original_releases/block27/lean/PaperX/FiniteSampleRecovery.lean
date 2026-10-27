import PaperX.GeneralReconstructionRecovery
import PaperX.WeilSmooth
import Mathlib.GroupTheory.OrderOfElement

/-! Finite original inertia actions supply a common unipotent sample after taking
an explicitly positive power. The norm character and a nonzero cocycle value
are still hypotheses on the supplied element; no arithmetic attachment is asserted. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.FiniteSampleRecovery

open PaperX.WeilData PaperX.MonodromyReconstruction

variable {K G : Type*} [Field K] [CharZero K] [Group G] {ν : G →* Kˣ}
variable {V W : Type*} [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]

/-- On the kernel of the norm character the twisted cocycle is additive on powers. -/
theorem cocycle_pow (t : TwistedCocycle ν) (u : G) (hν : ν u = 1) (n : ℕ) :
    t.value (u ^ n) = (n : K) * t.value u := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ, t.mul_value, ih, map_pow, hν]
    simp only [one_pow, Units.val_one, one_mul, Nat.cast_add, Nat.cast_one]
    ring

/-- Positive powers retain the nonzero cocycle value in characteristic zero. -/
theorem cocycle_pow_ne_zero (t : TwistedCocycle ν) (u : G) (hν : ν u = 1)
    (htu : t.value u ≠ 0) {n : ℕ} (hn : 0 < n) : t.value (u ^ n) ≠ 0 := by
  rw [cocycle_pow t u hν]
  exact mul_ne_zero (Nat.cast_ne_zero.mpr (Nat.ne_of_gt hn)) htu

/-- Two finite-order original actions become trivial at one positive common power. -/
theorem exists_common_sample {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (u : G) (hν : ν u = 1) (htu : t.value u ≠ 0)
    (hD : IsOfFinOrder (D.r u)) (hE : IsOfFinOrder (E.r u)) :
    ∃ n : ℕ, 0 < n ∧ D.r (u ^ n) = 1 ∧ E.r (u ^ n) = 1 ∧ t.value (u ^ n) ≠ 0 := by
  obtain ⟨d, hd, hdp⟩ := hD.exists_pow_eq_one
  obtain ⟨e, he, hep⟩ := hE.exists_pow_eq_one
  refine ⟨d * e, Nat.mul_pos hd he, ?_, ?_,
    cocycle_pow_ne_zero t u hν htu (Nat.mul_pos hd he)⟩
  · rw [map_pow, pow_mul, hdp, one_pow]
  · rw [map_pow, Nat.mul_comm d e, pow_mul, hep, one_pow]

/-- Full reconstruction faithfulness when the sampled original actions have finite order. -/
theorem reconstruct_intertwiner_iff_of_finite_order {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (u : G) (hν : ν u = 1) (htu : t.value u ≠ 0)
    (hD : IsOfFinOrder (D.r u)) (hE : IsOfFinOrder (E.r u)) (f : V →ₗ[K] W) :
    (∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) ↔
      (∀ g x, f (D.r g x) = E.r g (f x)) ∧ E.N ∘ₗ f = f ∘ₗ D.N := by
  obtain ⟨n, _, hDn, hEn, htn⟩ := exists_common_sample t u hν htu hD hE
  exact GeneralReconstructionRecovery.reconstruct_intertwiner_iff t (u ^ n) hDn hEn htn f

omit [CharZero K] in
/-- Finite actual image on a subgroup makes each restricted action element finite order. -/
theorem action_finite_order_of_finite_image (ρ : Representation K G V) (H : Subgroup G)
    (hfinite : Set.Finite (Set.range (fun g : H => ρ g))) (u : H) :
    IsOfFinOrder (ρ u) := by
  have hmem (n : ℕ) : (ρ u) ^ n ∈ Set.range (fun g : H => ρ g) := by
    refine ⟨u ^ n, ?_⟩
    simp
  obtain ⟨m, n, hmn, hpow⟩ := hfinite.exists_lt_map_eq_of_forall_mem hmem
  apply isOfFinOrder_iff_pow_eq_one.mpr
  refine ⟨n - m, Nat.sub_pos_of_lt hmn, ?_⟩
  have hm : IsUnit ((ρ u) ^ m) := by
    rw [← map_pow]
    exact ⟨ρ.toHomUnits ((u : G) ^ m), rfl⟩
  apply hm.mul_left_cancel
  rw [← pow_add, Nat.add_sub_of_le hmn.le, mul_one]
  exact hpow.symm

/-- Actual finite inertia images supply the common sample needed for full faithfulness. -/
theorem reconstruct_intertwiner_iff_of_finite_inertia {D : Datum ν V} {E : Datum ν W}
    (t : TwistedCocycle ν) (H : Subgroup G) (u : H)
    (hν : ν u = 1) (htu : t.value u ≠ 0)
    (hD : Set.Finite (Set.range (fun g : H => D.r g)))
    (hE : Set.Finite (Set.range (fun g : H => E.r g))) (f : V →ₗ[K] W) :
    (∀ g x, f (reconstruct D t g x) = reconstruct E t g (f x)) ↔
      (∀ g x, f (D.r g x) = E.r g (f x)) ∧ E.N ∘ₗ f = f ∘ₗ D.N := by
  exact reconstruct_intertwiner_iff_of_finite_order t u hν htu
    (action_finite_order_of_finite_image D.r H hD u)
    (action_finite_order_of_finite_image E.r H hE u) f

end PaperX.FiniteSampleRecovery
