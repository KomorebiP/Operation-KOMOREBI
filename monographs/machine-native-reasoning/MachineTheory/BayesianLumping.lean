import MachineTheory.Bayes
import Mathlib.Data.Setoid.Basic
import Mathlib.Data.Fintype.EquivFin

/-! Separate all-prior Bayesian updates are stronger than one chosen combined
transition/report schedule. Strictly positive likelihoods and a nontrivial retained
partition force the fine likelihood to be constant on retained fibres. -/
namespace Komorebi.MachineTheory
namespace BayesianLumping
open scoped BigOperators
open Instrument Bayes
noncomputable section
variable {X Z : Type*} [Fintype X] [Fintype Z] [DecidableEq X] [DecidableEq Z]

def twoPoint (x y : X) : X → ℝ := fun u => (basis x u + basis y u) / 2

omit [Fintype Z] [DecidableEq Z] in
theorem sum_twoPoint (f : X → ℝ) (x y : X) :
    (∑ u, f u * twoPoint x y u) = (f x + f y) / 2 := by
  simp only [twoPoint, ← mul_div_assoc, mul_add]
  rw [← Finset.sum_div, Finset.sum_add_distrib]
  simp [basis, mul_ite]

omit [Fintype Z] [DecidableEq Z] in
theorem twoPoint_dist (x y : X) : IsDist (twoPoint x y) := by
  constructor
  · intro u; unfold twoPoint basis; positivity
  · have h := sum_twoPoint (fun _ : X => (1 : ℝ)) x y
    norm_num [mass] at h ⊢
    exact h

omit [Fintype Z] [DecidableEq Z] in
theorem evidence_twoPoint (l : X → ℝ) (x y : X) :
    evidence (twoPoint x y) l = (l x + l y) / 2 := sum_twoPoint l x y

omit [Fintype Z] in
theorem push_twoPoint (π : X → Z) (x y : X) :
    push π (twoPoint x y) = twoPoint (π x) (π y) := by
  funext z
  have h := sum_twoPoint (fun u => if π u = z then (1 : ℝ) else 0) x y
  simpa [push, twoPoint, basis, ite_mul, eq_comm] using h

/-- The posterior mass of one of two distinct retained blocks. -/
theorem posterior_twoPoint (π : X → Z) (l : X → ℝ) (x y : X)
    (hxy : π x ≠ π y) :
    push π (update (twoPoint x y) l) (π x) = l x / (l x + l y) := by
  rw [show update (twoPoint x y) l = normalize (weights (twoPoint x y) l) from rfl,
    push_normalize]
  simp only [normalize, mass_push]
  change push π (weights (twoPoint x y) l) (π x) / evidence (twoPoint x y) l = _
  rw [evidence_twoPoint]
  have hn := sum_twoPoint (fun u => if π u = π x then l u else 0) x y
  have hn' : push π (weights (twoPoint x y) l) (π x) = l x / 2 := by
    simpa only [push, weights, ite_mul, zero_mul, ↓reduceIte, Ne.symm hxy, add_zero] using hn
  rw [hn']
  exact div_div_div_cancel_right₀ (by norm_num : (2 : ℝ) ≠ 0) _ _

/-- The coarse posterior is determined by the coarse prior. This deliberately
asks for all priors, not only one reachable family. -/
def UpdateDetermined (π : X → Z) (l : X → ℝ) : Prop :=
  ∀ p q, IsDist p → IsDist q → push π p = push π q →
    push π (update p l) = push π (update q l)

/-- Two attained blocks are essential. Positivity excludes degenerate zero-likelihood odds. -/
theorem likelihood_constant_on_fibres (π : X → Z) (l : X → ℝ)
    (hl : ∀ x, 0 < l x) (hnt : ∃ u v, π u ≠ π v)
    (hu : UpdateDetermined π l) : ∀ x y, π x = π y → l x = l y := by
  intro x y hxy
  obtain ⟨u,v,huv⟩ := hnt
  have hz : ∃ z, π x ≠ π z := by
    by_cases hx : π x = π u
    · exact ⟨v, fun hh => huv (hx.symm.trans hh)⟩
    · exact ⟨u,hx⟩
  obtain ⟨z,hxz⟩ := hz
  have hyz : π y ≠ π z := by simpa [← hxy] using hxz
  have hpush : push π (twoPoint x z) = push π (twoPoint y z) := by
    rw [push_twoPoint, push_twoPoint, hxy]
  have h := congrFun (hu _ _ (twoPoint_dist x z) (twoPoint_dist y z) hpush) (π x)
  rw [posterior_twoPoint π l x z hxz] at h
  rw [hxy, posterior_twoPoint π l y z hyz] at h
  have hxd : l x + l z ≠ 0 := ne_of_gt (add_pos (hl x) (hl z))
  have hyd : l y + l z ≠ 0 := ne_of_gt (add_pos (hl y) (hl z))
  have he := (div_eq_div_iff hxd hyd).mp h
  have hprod : (l x - l y) * l z = 0 := by nlinarith
  exact sub_eq_zero.mp ((mul_eq_zero.mp hprod).resolve_right (ne_of_gt (hl z)))

omit [DecidableEq X] in
/-- Grouping the numerator and denominator commutes with exact correction. -/
theorem update_commutes_of_factored (π : X → Z) (l : X → ℝ) (g : Z → ℝ)
    (hf : ∀ x, l x = g (π x)) (p : X → ℝ) :
    push π (update p l) = update (push π p) g := by
  have hw : push π (weights p l) = weights (push π p) g := by
    funext z
    simp only [push, weights, Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro x _
    split_ifs with hx
    · rw [hf x, hx]
    · simp
  change push π (normalize (weights p l)) = normalize (weights (push π p) g)
  rw [push_normalize, hw]

omit [DecidableEq X] in
theorem update_determined_of_factored (π : X → Z) (l : X → ℝ) (g : Z → ℝ)
    (hf : ∀ x, l x = g (π x)) : UpdateDetermined π l := by
  intro p q _ _ hpq
  rw [update_commutes_of_factored π l g hf p,
      update_commutes_of_factored π l g hf q, hpq]

/-- Core 3.5's Bayesian gate, with the coarse likelihood constructed on attained blocks. -/
theorem fixed_positive_coarse_iff (π : X → Z) (hπ : Function.Surjective π)
    (l : X → ℝ) (hl : ∀ x, 0 < l x) (hnt : ∃ u v, π u ≠ π v) :
    (∃ g : Z → ℝ, (∀ z, 0 < g z) ∧
      ∀ p, IsDist p → push π (update p l) = update (push π p) g) ↔
      (∀ x y, π x = π y → l x = l y) := by
  constructor
  · rintro ⟨g,_,hg⟩
    apply likelihood_constant_on_fibres π l hl hnt
    intro p q hp hq he
    rw [hg p hp, hg q hq, he]
  · intro h
    let g : Z → ℝ := fun z => l (Classical.choose (hπ z))
    have hf : ∀ x, l x = g (π x) :=
      fun x => h x _ (Classical.choose_spec (hπ (π x))).symm
    exact ⟨g,fun z => hl _,fun p _ => update_commutes_of_factored π l g hf p⟩

end
end BayesianLumping
end Komorebi.MachineTheory
