import SmithCanonicalRoot
import Mathlib.RingTheory.RootsOfUnity.Complex
import SmithExamples

/-! Discrete reachability and explicit boundary witnesses. -/

namespace SmithBoundaries

/-- Any target in the specified nonzero cyclic orbit passes the phase test. -/
theorem cyclic_reachable_necessary {N k : ℕ} (hN : 0 < N) {start target : ℂ}
    (hstart : start ≠ 0) (hreach : target = SmithCanonicalRoot.omega N ^ k * start) :
    (target / start) ^ N = 1 := by
  rw [hreach, mul_div_cancel_right₀ _ hstart, ← pow_mul, Nat.mul_comm k N, pow_mul]
  rw [(SmithCanonicalRoot.omega_pow_eq_one_iff hN N).2 (dvd_refl N)]
  simp

theorem cyclic_reachable_iff {N : ℕ} (hN : 0 < N) {start target : ℂ} (hstart : start ≠ 0) :
    (∃ k : ℕ, k < N ∧ target = SmithCanonicalRoot.omega N ^ k * start) ↔
      (target / start) ^ N = 1 := by
  let _ : NeZero N := ⟨hN.ne'⟩
  have hroot : IsPrimitiveRoot (SmithCanonicalRoot.omega N) N := by
    exact Complex.isPrimitiveRoot_exp N hN.ne'
  constructor
  · rintro ⟨k, hk, hr⟩
    exact cyclic_reachable_necessary hN hstart hr
  · intro ht
    obtain ⟨k, hk, he⟩ := hroot.eq_pow_of_pow_eq_one ht
    refine ⟨k, hk, ?_⟩
    have he' := congrArg (fun v : ℂ => v * start) he
    simpa [div_mul_cancel₀ _ hstart] using he'.symm

theorem quarter_turn_phase_test : (Complex.I : ℂ) ^ 2 ≠ 1 ∧ (Complex.I : ℂ) ^ 4 = 1 := by
  norm_num [Complex.I_sq, pow_succ]

theorem zero_start_reachable_iff {N : ℕ} (hN : 0 < N) {target : ℂ} :
    (∃ k : ℕ, k < N ∧ target = SmithCanonicalRoot.omega N ^ k * 0) ↔ target = 0 := by
  constructor
  · rintro ⟨k, hk, he⟩
    simpa using he
  · intro he
    refine ⟨0, hN, ?_⟩
    simpa using he

theorem quarter_turn_infeasible_order_two :
    ¬ ∃ k : ℕ, k < 2 ∧ Complex.I / 2 = SmithCanonicalRoot.omega 2 ^ k * (1 / 2) := by
  intro h
  have he := (cyclic_reachable_iff (N := 2) (by decide) (start := (1 / 2 : ℂ))
      (target := Complex.I / 2) (by norm_num)).1 h
  have hratio : Complex.I / 2 / (1 / 2 : ℂ) = Complex.I := by
    field_simp
  rw [hratio] at he
  exact quarter_turn_phase_test.1 he

theorem quarter_turn_feasible_order_four :
    ∃ k : ℕ, k < 4 ∧ Complex.I / 2 = SmithCanonicalRoot.omega 4 ^ k * (1 / 2) := by
  apply (cyclic_reachable_iff (N := 4) (by decide) (start := (1 / 2 : ℂ))
    (target := Complex.I / 2) (by norm_num)).2
  have hratio : Complex.I / 2 / (1 / 2 : ℂ) = Complex.I := by
    field_simp
  rw [hratio]
  exact quarter_turn_phase_test.2

def noncoprimeFixture (n : ℕ) : ℂ := if n = 0 ∨ n = 4 then 1 else 0

theorem noncoprime_projector_counterexample :
    SmithAlgebra.project 2 0 (SmithAlgebra.project 4 0 noncoprimeFixture) 4 = 1 ∧
    SmithAlgebra.project 8 0 noncoprimeFixture 4 = 0 := by
  norm_num [SmithAlgebra.project, noncoprimeFixture]

def firstSample (_t : ℂ) : ℂ := 1

noncomputable def secondSample (t : ℂ) : ℂ := 15 / 16 + t ^ 2 / 4

theorem two_sample_equal_but_not_identical :
    firstSample (1 / 2) = secondSample (1 / 2) ∧
    firstSample (-1 / 2) = secondSample (-1 / 2) ∧
    firstSample 0 ≠ secondSample 0 := by
  norm_num [firstSample, secondSample]

theorem second_sample_positive_real {t : ℂ} (ht : ‖t‖ < 1) :
    (11 / 16 : ℝ) < (secondSample t).re := by
  have hnorm : ‖t ^ 2‖ < 1 := by
    rw [norm_pow]
    nlinarith [norm_nonneg t]
  have hbound : -1 < (t ^ 2).re := by
    have habs : |(t ^ 2).re| < 1 := lt_of_le_of_lt (Complex.abs_re_le_norm _) hnorm
    exact (abs_lt.mp habs).1
  simp only [secondSample, Complex.add_re, Complex.div_ofNat_re]
  norm_num
  linarith

end SmithBoundaries
