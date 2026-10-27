module
public import Euler.RestrictedJets
public import Euler.CollisionSeries
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- Geometric coefficient decay supplies restrictedness, even with an arbitrary integral seed. -/
lemma restricted_of_four_tail (f : Series) (d : ℕ) (w : ℕ → D)
    (h : ∀ n, coeff (n+d) f=(4:D)^n*w n) : Restricted f := by
  rw [restricted_iff]
  apply (tendsto_add_atTop_iff_nat d).mp
  have hfour : ‖(4:D)‖=(1/4:ℝ) := by
    rw [show (4:D)=(2:D)^2 by norm_num, norm_pow]
    have hp := PadicInt.norm_p (p:=2)
    norm_num at hp
    rw [hp]
    norm_num
  apply squeeze_zero (g:=fun n => (1/4:ℝ)^n) (fun n => norm_nonneg _)
  · intro n
    rw [h, norm_mul, norm_pow, hfour]
    exact mul_le_of_le_one_right (by positivity) (PadicInt.norm_le_one _)
  · exact tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num) (by norm_num)

/-- The weighted remainder in the nearest-neighbor factorization always converges on Z_2. -/
theorem restricted_rescale_four (e : Series) : Restricted (rescale (4:D) e) := by
  apply restricted_of_four_tail _ 0 (fun n => coeff n e)
  intro n
  simp only [Nat.add_zero, coeff_rescale]

/-- Formal one-neighbor coefficient identities now give an actual convergent function. -/
theorem oneNeighbor_restricted (r ε : D) (e H : Series) (z : D)
    (h : IsHalfCore (oneRatio r ε e) H z) : Restricted H := by
  apply restricted_of_four_tail H 2 (fun n => r*(2*coeff (n+1) e+ε*coeff n e))
  intro n
  rw [oneNeighbor_coeff _ _ _ _ _ h]
  ring

/-- Both before and after the permitted extra division, the two-neighbor core converges. -/
theorem twoNeighbor_restricted (r : D) (e H : Series) (z : D)
    (h : IsHalfCore (twoRatio r e) H z) : Restricted H := by
  apply restricted_of_four_tail H 3 (fun n => 2*r*(4*coeff (n+2) e-coeff n e))
  intro n
  rw [twoNeighbor_coeff _ _ _ _ h]
  ring

theorem twoNeighbor_divided_restricted (r : D) (e H F : Series) (z : D)
    (h : IsHalfCore (twoRatio r e) H z) (hF : C (2:D)*F=H) : Restricted F := by
  apply restricted_of_four_tail F 3 (fun n => r*(4*coeff (n+2) e-coeff n e))
  intro n
  apply cancel_two
  have hh := congrArg (coeff (n+3)) hF
  rw [coeff_C_mul, twoNeighbor_coeff _ _ _ _ h] at hh
  calc
    2*coeff (n+3) F=2*4^n*r*(4*coeff (n+2) e-coeff n e) := hh
    _ = 2*(4^n*(r*(4*coeff (n+2) e-coeff n e))) := by ring

/-- The v13 coefficient dichotomy upgraded to restricted-series statements, without
assuming closed-disc Weierstrass preparation or a conclusion about root multiplicity. -/
theorem twoNeighbor_restricted_dichotomy (r : D) (e H : Series) (z : D)
    (hr : red r=1) (he : coeff 0 e=1)
    (h : IsHalfCore (twoRatio r e) H z) :
    Restricted H ∧ (LastOdd H 0 ∨ LastOdd H 1 ∨
      ∃ F : Series, C (2:D)*F=H ∧ Restricted F ∧ LastOdd F 3) := by
  refine ⟨twoNeighbor_restricted r e H z h,?_⟩
  rcases twoNeighbor_dichotomy r e H z hr he h with h0 | h1 | ⟨F,hF,h3⟩
  · exact Or.inl h0
  · exact Or.inr (Or.inl h1)
  · exact Or.inr (Or.inr ⟨F,hF,twoNeighbor_divided_restricted r e H F z h hF,h3⟩)

/-- Mod-8 terminal-161-shaped coefficients exclude genuine analytic triple-jet vanishing
for an arbitrary restricted series, not only for a polynomial truncation. -/
theorem restricted_terminal161_no_analytic_triple
    {f : Series} (hf : Restricted f) (t : ZMod 8)
    (hc : ∀ n, redPow 3 (coeff n f)=(model161 t).coeff n) :
    ∀ x : D, ¬ (qeval f (x:ℚ_[2])=0 ∧ deriv (qeval f) (x:ℚ_[2])=0 ∧
      deriv (deriv (qeval f)) (x:ℚ_[2])=0) := by
  exact restricted_no_analytic_triple_of_residue hf 3 (model161 t) hc
    (model161_certificate t)

/-- The mod-4 certificate is sound for the full infinite evaluation on the entire unit disc. -/
theorem restricted_terminal514_rootfree
    {f : Series} (hf : Restricted f) (t u : ZMod 4)
    (ht : t=1 ∨ t=3) (hu : u=1 ∨ u=3)
    (hc : ∀ n, redPow 2 (coeff n f)=
      (Polynomial.C u*Polynomial.X^2+
       Polynomial.C (3*(1+t))*Polynomial.X+Polynomial.C 2).coeff n) :
    ∀ x : D, reval f x ≠ 0 := by
  apply restricted_rootfree_of_residue hf 2 _ hc
  intro y
  simp only [Polynomial.eval_add, Polynomial.eval_mul, Polynomial.eval_C,
    Polynomial.eval_pow, Polynomial.eval_X]
  rcases hu with rfl | rfl
  · simpa only [one_mul] using (quadratic514_templates_rootfree t y ht).1
  · exact (quadratic514_templates_rootfree t y ht).2

/-- One-neighbor restrictedness is discharged by its formal identity; only the exact
Euler-shaped coefficient certificate remains as an explicit input. -/
theorem oneNeighbor_terminal514_rootfree (r ε : D) (e H : Series) (z : D)
    (h : IsHalfCore (oneRatio r ε e) H z) (t u : ZMod 4)
    (ht : t=1 ∨ t=3) (hu : u=1 ∨ u=3)
    (hc : ∀ n, redPow 2 (coeff n H)=
      (Polynomial.C u*Polynomial.X^2+
       Polynomial.C (3*(1+t))*Polynomial.X+Polynomial.C 2).coeff n) :
    ∀ x : D, reval H x ≠ 0 :=
  restricted_terminal514_rootfree (oneNeighbor_restricted r ε e H z h) t u ht hu hc

/-- Exact two-root existence, uniqueness in parity classes and analytic simplicity for
one-neighbor cores whose whole coefficient reduction is X^2+X. -/
theorem oneNeighbor_two_simple_roots (r ε : D) (e H : Series) (z : D)
    (h : IsHalfCore (oneRatio r ε e) H z)
    (hc : ∀ n, res (coeff n H)=
      (Polynomial.X^2+Polynomial.X : Polynomial F₂).coeff n) :
    ∃ a b : D, res a=0 ∧ res b=1 ∧ a ≠ b ∧
      (∀ x : D, reval H x=0 ↔ x=a ∨ x=b) ∧
      (∀ x : D, reval H x=0 → deriv (qeval H) (x:ℚ_[2]) ≠ 0) :=
  restricted_two_simple_roots (oneNeighbor_restricted r ε e H z h) hc

/-- The two genuine residue maps modulo two agree. -/
lemma res_eq_red (x : D) : res x=red x := by
  have hz : res x=0 ↔ red x=0 :=
    (res_zero_iff_norm_lt_one x).trans (red_zero_iff_norm_lt_one x).symm
  rcases binary_value (res x) with h0 | h1
  · rw [h0, hz.mp h0]
  · rcases binary_value (red x) with g0 | g1
    · have hb := hz.mpr g0
      rw [h1] at hb
      norm_num at hb
    · rw [h1,g1]

/-- A finite two-coefficient condition finishes an entire infinite one-neighbor core.
The quadratic and every higher residue coefficient are derived, not supplied. -/
theorem oneNeighbor_split_of_first_coeffs (r ε : D) (e H : Series) (z : D)
    (hr : red r=1) (hε : red ε=1) (he : coeff 0 e=1)
    (h : IsHalfCore (oneRatio r ε e) H z)
    (h0 : red (coeff 0 H)=0) (h1 : red (coeff 1 H)=1) :
    ∃ a b : D, res a=0 ∧ res b=1 ∧ a ≠ b ∧
      (∀ x : D, reval H x=0 ↔ x=a ∨ x=b) ∧
      (∀ x : D, reval H x=0 → deriv (qeval H) (x:ℚ_[2]) ≠ 0) := by
  apply oneNeighbor_two_simple_roots r ε e H z h
  intro n
  rw [res_eq_red]
  have hlo := oneNeighbor_lastOdd r ε e H z hr hε he h
  rcases n with _ | n
  · simpa using h0
  rcases n with _ | n
  · simpa using h1
  rcases n with _ | n
  · simpa [Polynomial.coeff_X] using hlo.1
  · have hn : n+1+1+1>2 := by omega
    rw [hlo.2 _ hn]
    simp [Polynomial.coeff_X, show n+1+1+1 ≠ 2 by omega]

/-- Coefficientwise precision, not just agreement of integer values, survives evaluation. -/
theorem reval_congr_of_coeff_congr {f g : Series} (hf : Restricted f)
    (hg : Restricted g) (k : ℕ)
    (hc : ∀ n, redPow k (coeff n f)=redPow k (coeff n g)) :
    ∀ x : D, redPow k (reval f x)=redPow k (reval g x) := by
  intro x
  have hf' := hasSum_redPow_reval hf k x
  have hg' := hasSum_redPow_reval hg k x
  simp_rw [hc] at hf'
  exact hf'.unique hg'

/-- An arbitrary congruent restricted tail preserves the residue decision for all Hasse jets. -/
theorem rjet_congr_of_coeff_congr {f g : Series} (hf : Restricted f)
    (hg : Restricted g) (k : ℕ)
    (hc : ∀ n, redPow k (coeff n f)=redPow k (coeff n g)) (d : ℕ) :
    ∀ x : D, redPow k (rjet d f x)=redPow k (rjet d g x) := by
  apply reval_congr_of_coeff_congr (restricted_hasseSeries hf d)
    (restricted_hasseSeries hg d) k
  intro n
  simp only [coeff_hasseSeries, map_mul, hc]

end Komorebi.Euler
