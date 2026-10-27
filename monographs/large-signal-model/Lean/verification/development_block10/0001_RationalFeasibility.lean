import Mathlib

/-! Exact rational feasibility, including boundary faces. Fourier–Motzkin
elimination transfers a finite weak linear system from the reals to rationals. -/
set_option autoImplicit false
namespace Komorebi.LSM.RationalSearch
open scoped BigOperators

/-- A finite collection of rational lower and upper bounds that contains a real
point contains a rational point. Endpoints need not have positive separation. -/
theorem rational_interval {I : Type*} [Fintype I]
    (lo hi : I → ℚ) (L U : I → Prop) [DecidablePred L] [DecidablePred U]
    (t : ℝ) (hl : ∀ i, L i → (lo i : ℝ) ≤ t)
    (hu : ∀ i, U i → t ≤ (hi i : ℝ)) :
    ∃ q : ℚ, (∀ i, L i → lo i ≤ q) ∧ (∀ i, U i → q ≤ hi i) := by
  classical
  let ls := Finset.univ.filter L
  let us := Finset.univ.filter U
  by_cases hn : ls.Nonempty
  · obtain ⟨i, hiL, hmax⟩ := ls.exists_max_image lo hn
    have hLi : L i := (Finset.mem_filter.mp hiL).2
    refine ⟨lo i, ?_, ?_⟩
    · intro j hj
      exact hmax j (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩)
    · intro j hj
      exact_mod_cast (hl i hLi).trans (hu j hj)
  · by_cases hm : us.Nonempty
    · obtain ⟨i, hiU, hmin⟩ := us.exists_min_image hi hm
      refine ⟨hi i, ?_, ?_⟩
      · intro j hj
        exact False.elim (hn ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)
      · intro j hj
        exact hmin j (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩)
    · refine ⟨0, ?_, ?_⟩
      · intro j hj
        exact False.elim (hn ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)
      · intro j hj
        exact False.elim (hm ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)

/-- Every feasible finite weak linear system with rational coefficients has a
rational solution. Equality and nonnegativity are encoded as weak inequalities. -/
theorem rational_feasible (n : ℕ) : ∀ {I : Type*} [Fintype I]
    (a : I → Fin n → ℚ) (b : I → ℚ),
    (∃ x : Fin n → ℝ, ∀ i, ∑ j, (a i j : ℝ) * x j ≤ (b i : ℝ)) →
    ∃ x : Fin n → ℚ, ∀ i, ∑ j, a i j * x j ≤ b i := by
  induction n with
  | zero =>
    intro I _ a b ⟨x,hx⟩
    refine ⟨fun _ => 0, ?_⟩
    intro i
    simpa using (show (0 : ℚ) ≤ b i by exact_mod_cast (by simpa using hx i : (0 : ℝ) ≤ b i))
  | succ n ih =>
    intro I _ a b ⟨x,hx⟩
    classical
    let c : I → ℚ := fun i => a i 0
    let d : I → Fin n → ℚ := fun i j => a i j.succ
    let aa : I ⊕ (I × I) → Fin n → ℚ
      | .inl i => if c i = 0 then d i else 0
      | .inr (i,k) => if c i < 0 ∧ 0 < c k then
          fun j => d i j / (-c i) + d k j / c k else 0
    let bb : I ⊕ (I × I) → ℚ
      | .inl i => if c i = 0 then b i else 0
      | .inr (i,k) => if c i < 0 ∧ 0 < c k then b i / (-c i) + b k / c k else 0
    have hx' (i : I) : (c i : ℝ) * x 0 + ∑ j, (d i j : ℝ) * x j.succ ≤ b i := by
      simpa only [c,d,Fin.sum_univ_succ] using hx i
    have hred : ∃ y : Fin n → ℝ, ∀ i, ∑ j, (aa i j : ℝ) * y j ≤ bb i := by
      refine ⟨fun j => x j.succ, ?_⟩
      intro row
      cases row with
      | inl i =>
        by_cases h : c i = 0
        · simpa [aa,bb,h] using hx' i
        · simp [aa,bb,h]
      | inr p =>
        obtain ⟨i,k⟩ := p
        by_cases h : c i < 0 ∧ 0 < c k
        · have hi : (0 : ℝ) < -(c i : ℝ) := by exact_mod_cast neg_pos.mpr h.1
          have hk : (0 : ℝ) < (c k : ℝ) := by exact_mod_cast h.2
          have hh := add_le_add (div_le_div_of_nonneg_right (hx' i) hi.le)
            (div_le_div_of_nonneg_right (hx' k) hk.le)
          simp only [aa,bb,if_pos h,Rat.cast_add,Rat.cast_div,Rat.cast_neg]
          simp_rw [add_mul,div_mul_eq_mul_div,Finset.sum_add_distrib,← Finset.sum_div]
          have ci : (c i : ℝ) ≠ 0 := ne_of_lt (by linarith)
          have ck : (c k : ℝ) ≠ 0 := ne_of_gt hk
          field_simp at hh ⊢
          nlinarith
        · simp [aa,bb,h]
    obtain ⟨y,hy⟩ := ih aa bb hred
    let r : I → ℚ := fun i => b i - ∑ j, d i j * y j
    have hz (i : I) (h : c i = 0) : 0 ≤ r i := by
      have := hy (.inl i)
      simp only [aa,bb,if_pos h] at this
      exact sub_nonneg.mpr this
    have hp (i k : I) (hi : c i < 0) (hk : 0 < c k) : r i / c i ≤ r k / c k := by
      have hh := hy (.inr (i,k))
      simp only [aa,bb,if_pos (show c i < 0 ∧ 0 < c k from ⟨hi,hk⟩)] at hh
      simp_rw [add_mul,div_mul_eq_mul_div,Finset.sum_add_distrib,← Finset.sum_div] at hh
      dsimp [r]
      apply (div_le_div_iff_of_neg_of_pos hi hk).mpr
      have hi' : 0 < -c i := neg_pos.mpr hi
      have hmul := (div_add_div_le_div_add_div_iff ..)
      field_simp at hh
      nlinarith
    -- The eliminated rational system makes every lower bound ≤ every upper bound.
    have hpoint : ∃ t : ℝ, (∀ i, c i < 0 → (r i / c i : ℚ) ≤ t) ∧
        (∀ i, 0 < c i → t ≤ (r i / c i : ℚ)) := by
      let ls := Finset.univ.filter (fun i => c i < 0)
      by_cases hn : ls.Nonempty
      · obtain ⟨i,hi,hmax⟩ := ls.exists_max_image (fun i => r i / c i) hn
        refine ⟨(r i / c i : ℚ),?_,?_⟩
        · intro j hj
          exact_mod_cast hmax j (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩)
        · intro j hj
          exact_mod_cast hp i j (Finset.mem_filter.mp hi).2 hj
      · let us := Finset.univ.filter (fun i => 0 < c i)
        by_cases hm : us.Nonempty
        · obtain ⟨i,hi,hmin⟩ := us.exists_min_image (fun i => r i / c i) hm
          refine ⟨(r i / c i : ℚ),?_,?_⟩
          · intro j hj
            exact False.elim (hn ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)
          · intro j hj
            exact_mod_cast hmin j (Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩)
        · refine ⟨0,?_,?_⟩
          · intro j hj
            exact False.elim (hn ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)
          · intro j hj
            exact False.elim (hm ⟨j,Finset.mem_filter.mpr ⟨Finset.mem_univ _,hj⟩⟩)
    obtain ⟨t,htl,htu⟩ := hpoint
    obtain ⟨q,hql,hqu⟩ := rational_interval (fun i => r i / c i) (fun i => r i / c i)
      (fun i => c i < 0) (fun i => 0 < c i) t htl htu
    refine ⟨Fin.cons q y, ?_⟩
    intro i
    rw [Fin.sum_univ_succ]
    change c i * q + ∑ j, d i j * y j ≤ b i
    have hr : c i * q ≤ r i := by
      rcases lt_trichotomy (c i) 0 with hi | hi | hi
      · exact (div_le_iff_of_neg hi).mp (hql i hi)
      · simpa [hi] using hz i hi
      · exact (le_div_iff₀ hi).mp (hqu i hi) |>.trans_eq (mul_comm q (c i))
    dsimp [r] at hr
    linarith
end Komorebi.LSM.RationalSearch
