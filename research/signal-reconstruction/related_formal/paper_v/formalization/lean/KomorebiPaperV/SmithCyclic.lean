import KomorebiPaperV.SmithAction
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic

/-! Author: Komorebi P. The cyclic Smith action on the full projective line. -/
namespace KomorebiPaperV.SmithCyclic
open KomorebiPaperV.SmithAction

noncomputable def omega (N : ℕ) : ℂ := Complex.exp (2 * Real.pi * Complex.I / N)

theorem omega_ne_zero (N : ℕ) : omega N ≠ 0 := Complex.exp_ne_zero _

theorem omega_pow (N : ℕ) (hN : 0 < N) : omega N ^ N = 1 := by
  rw [omega, ← Complex.exp_nat_mul]
  have hNc : (N : ℂ) ≠ 0 := by exact_mod_cast hN.ne'
  have he : (N : ℂ) * (2 * Real.pi * Complex.I / N) = 2 * Real.pi * Complex.I := by
    field_simp
  rw [he, Complex.exp_two_pi_mul_I]

theorem omega_two : omega 2 = -1 := by
  unfold omega
  convert Complex.exp_pi_mul_I using 1; congr 1; ring

abbrev Point := {p : ℂ × ℂ // p ≠ 0}

def same (p q : Point) : Prop := ∃ c : ℂ, c ≠ 0 ∧ q.val = (c * p.val.1, c * p.val.2)

noncomputable def pointSetoid : Setoid Point where
  r := same
  iseqv := {
    refl := by intro p; exact ⟨1, one_ne_zero, by simp⟩
    symm := by
      rintro p q ⟨c, hc, hq⟩
      refine ⟨c⁻¹, inv_ne_zero hc, ?_⟩
      rw [hq]
      simp [hc]
    trans := by
      rintro p q r ⟨c, hc, hq⟩ ⟨d, hd, hr⟩
      exact ⟨d*c, mul_ne_zero hd hc, by rw [hr, hq]; simp [mul_assoc]⟩ }

abbrev Projective := Quotient pointSetoid

noncomputable def pointAction (a : ℂ) (ha : a ≠ 0) (p : Point) : Point :=
  ⟨action a p.val, action_nonzero a ha p.val p.property⟩

theorem action_respects_scaling (a : ℂ) (ha : a ≠ 0) (p q : Point) (h : same p q) :
    same (pointAction a ha p) (pointAction a ha q) := by
  obtain ⟨c, hc, hq⟩ := h
  refine ⟨c, hc, ?_⟩
  change action a q.val = _
  rw [hq, action_scale]
  rfl

noncomputable def projectiveAction (a : ℂ) (ha : a ≠ 0) : Projective → Projective :=
  Quotient.map (pointAction a ha) (action_respects_scaling a ha)

theorem projective_mul (a b : ℂ) (ha : a ≠ 0) (hb : b ≠ 0) (p : Projective) :
    projectiveAction a ha (projectiveAction b hb p) =
      projectiveAction (a*b) (mul_ne_zero ha hb) p := by
  induction p using Quotient.inductionOn with
  | h p =>
    apply congrArg Quotient.mk''
    apply Subtype.ext
    exact action_mul a b p.val

theorem projective_one (p : Projective) : projectiveAction 1 one_ne_zero p = p := by
  induction p using Quotient.inductionOn with
  | h p =>
    apply congrArg Quotient.mk''
    apply Subtype.ext
    exact action_one p.val

noncomputable def cyclicAction (N k : ℕ) : Projective → Projective :=
  projectiveAction (omega N ^ k) (pow_ne_zero _ (omega_ne_zero N))

theorem cyclic_zero (N : ℕ) (p : Projective) : cyclicAction N 0 p = p := by
  exact projective_one p

theorem cyclic_composition (N : ℕ) (hN : 0 < N) (k l : ℕ) (p : Projective) :
    cyclicAction N k (cyclicAction N l p) = cyclicAction N ((k+l)%N) p := by
  unfold cyclicAction
  rw [projective_mul]
  have he : omega N ^ k * omega N ^ l = omega N ^ ((k+l)%N) := by
    rw [← pow_add, pow_eq_pow_mod (k+l) (omega_pow N hN)]
  congr 1

/-- Conjugacy with reflection-coordinate rotation, before taking the quotient. -/
theorem cayley_conjugacy (a : ℂ) (p : ℂ × ℂ) :
    ((action a p).1 - (action a p).2, (action a p).1 + (action a p).2) =
      (a * (p.1-p.2), p.1+p.2) := by
  apply Prod.ext <;> dsimp [action] <;> ring

theorem cyclic_chart (N k : ℕ) (z : ℂ) :
    (action (omega N ^ k) (z,1)).1 / (action (omega N ^ k) (z,1)).2 =
      ((1+omega N ^ k)*z+(1-omega N ^ k)) /
      ((1-omega N ^ k)*z+(1+omega N ^ k)) := homogeneous_chart _ _

theorem two_phase_swap (p : ℂ × ℂ) : action (omega 2 ^ 1) p = (p.2,p.1) := by
  rw [pow_one, omega_two, half_turn]

theorem two_phase_impedance_admittance (z : ℂ) (hz : z ≠ 0) :
    denominator (omega 2 ^ 1) z ≠ 0 ∧ mobius (omega 2 ^ 1) z = z⁻¹ := by
  rw [pow_one, omega_two]
  exact finite_half_turn z hz

end KomorebiPaperV.SmithCyclic
