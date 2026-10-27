import CrossRadixPrimitiveSpectralAlgebra
import Mathlib.NumberTheory.ArithmeticFunction.Moebius

noncomputable section
open scoped BigOperators ArithmeticFunction.Moebius
open ArithmeticFunction

namespace KomorebiCrossRadix

variable {T : ℕ}

local instance propDecidableMobius (p : Prop) : Decidable p := Classical.propDecidable p

/-- Width indicator for an arbitrary positive integer label. For labels dividing `T`, this is a canonical width vector. -/
def rawWidthVec (g : ℕ) : DivCoord T :=
  fun x => if g ∣ x.1 then 1 else 0

lemma rawWidthVec_dividx (g : DivIdx T) : rawWidthVec g.1 = widthVec g := by
  funext x
  rfl

lemma sum_mu_divisors (n : ℕ) :
    (∑ d ∈ n.divisors, ((μ d : ℤ) : ℂ)) = if n = 1 then 1 else 0 := by
  have h := congrArg (fun f : ArithmeticFunction ℂ => f n)
    (show ((↑ArithmeticFunction.zeta : ArithmeticFunction ℂ) *
      (↑ArithmeticFunction.moebius : ArithmeticFunction ℂ)) = 1 from
      coe_zeta_mul_coe_moebius)
  rw [coe_zeta_mul_apply] at h
  simpa [ArithmeticFunction.one_apply] using h

lemma filter_divisors_of_dvd {n Q : ℕ} (hn : n ≠ 0) (hQ : Q ≠ 0) (hnQ : n ∣ Q) :
    Q.divisors.filter (fun r => r ∣ n) = n.divisors := by
  ext r
  simp only [Finset.mem_filter]
  rw [Nat.mem_divisors, Nat.mem_divisors]
  constructor
  · rintro ⟨⟨_, _⟩, hrn⟩
    exact ⟨hrn, hn⟩
  · rintro ⟨hrn, _⟩
    exact ⟨⟨dvd_trans hrn hnQ, hQ⟩, hrn⟩

lemma sum_mu_dvd_indicator {n Q : ℕ} (hn : n ≠ 0) (hQ : Q ≠ 0) (hnQ : n ∣ Q) :
    (∑ r ∈ Q.divisors, (((μ r : ℤ) : ℂ) * if r ∣ n then 1 else 0)) =
      if n = 1 then 1 else 0 := by
  simp_rw [mul_ite, mul_one, mul_zero]
  rw [← Finset.sum_filter]
  rw [filter_divisors_of_dvd hn hQ hnQ]
  exact sum_mu_divisors n

/-- Möbius inversion: a primitive shell is an explicit signed sum of width indicators. -/
lemma shellVec_mobius_width (hT : 0 < T) (c : DivIdx T) :
    shellVec c =
      ∑ r ∈ (T / c.1).divisors,
        (((μ r : ℤ) : ℂ) • rawWidthVec (T := T) (c.1 * r)) := by
  funext x
  have hcT : c.1 ∣ T := (Nat.mem_divisors.mp c.2).1
  have hxT : x.1 ∣ T := (Nat.mem_divisors.mp x.2).1
  have hcpos : 0 < c.1 := Nat.pos_of_dvd_of_pos hcT hT
  have hxpos : 0 < x.1 := Nat.pos_of_dvd_of_pos hxT hT
  have hQpos : 0 < T / c.1 := Nat.div_pos (Nat.le_of_dvd hT hcT) hcpos
  by_cases hcx : c.1 ∣ x.1
  · have hnpos : 0 < x.1 / c.1 := Nat.div_pos (Nat.le_of_dvd hxpos hcx) hcpos
    have hnQ : x.1 / c.1 ∣ T / c.1 :=
      (Nat.div_dvd_div_iff_right hcx hcT).mpr hxT
    have hq1 : x.1 / c.1 = 1 ↔ x = c := by
      constructor
      · intro hq
        apply Subtype.ext
        calc
          x.1 = c.1 * (x.1 / c.1) := (Nat.mul_div_cancel' hcx).symm
          _ = c.1 := by simp [hq]
      · intro hxc
        subst x
        exact Nat.div_self hcpos
    have hdvd (r : ℕ) : c.1 * r ∣ x.1 ↔ r ∣ x.1 / c.1 := by
      exact (Nat.dvd_div_iff_mul_dvd hcx).symm
    rw [Finset.sum_apply]
    simp_rw [Pi.smul_apply, smul_eq_mul, rawWidthVec, hdvd]
    rw [sum_mu_dvd_indicator hnpos.ne' hQpos.ne' hnQ]
    by_cases hxc : x = c
    · have hn1 : x.1 / c.1 = 1 := hq1.mpr hxc
      rw [shellVec, ite_eq_left hxc, ite_eq_left hn1]
    · have hn1 : x.1 / c.1 ≠ 1 := fun h => hxc (hq1.mp h)
      rw [shellVec, ite_eq_right hxc, ite_eq_right hn1]
  · have hmul (r : ℕ) : ¬ c.1 * r ∣ x.1 := by
      intro hr
      exact hcx (dvd_trans (Nat.dvd_mul_right c.1 r) hr)
    have hxc : x ≠ c := by
      intro h
      subst x
      exact hcx (dvd_refl c.1)
    rw [Finset.sum_apply]
    simp [shellVec, hxc, Pi.smul_apply, smul_eq_mul, rawWidthVec, hmul]

/-- Operator version of Möbius inversion. -/
lemma shellEnd_mobius_width (hT : 0 < T) (c : DivIdx T) :
    shellEnd c =
      ∑ r ∈ (T / c.1).divisors,
        (((μ r : ℤ) : ℂ) • diagOp (rawWidthVec (T := T) (c.1 * r))) := by
  change diagOp (shellVec c) = _
  rw [shellVec_mobius_width hT c]
  simp

/-- Principal upper set corresponding to a canonical width. -/
def principalUpper (g : DivIdx T) : Set (DivIdx T) :=
  {c | g.1 ∣ c.1}

lemma widthVec_eq_indicator_principalUpper (g : DivIdx T) :
    widthVec g = indicatorVec (principalUpper g) := by
  funext c
  by_cases h : g.1 ∣ c.1 <;> simp [widthVec, indicatorVec, principalUpper, h]

section PositivePeriod

variable (hT : 0 < T)
include hT

lemma principalUpper_lcm (g h : DivIdx T) :
    principalUpper (lcmIdx hT g h) = principalUpper g ∩ principalUpper h := by
  ext c
  simp [principalUpper, lcmIdx, Nat.lcm_dvd_iff]

end PositivePeriod

/-- Canonical widths are exactly the principal-upper-set idempotents inside the full Boolean idempotent algebra. -/
lemma width_activeSet (g : DivIdx T) :
    activeSet (widthVec g) = principalUpper g := by
  ext c
  by_cases h : g.1 ∣ c.1 <;> simp [activeSet, widthVec, principalUpper, h]

end KomorebiCrossRadix

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Primitive shell vectors are the standard coordinate basis. -/
def shellBasis : Module.Basis (DivIdx T) ℂ (DivCoord T) :=
  Pi.basisFun ℂ (DivIdx T)

lemma shellBasis_apply (c : DivIdx T) : shellBasis c = shellVec c := by
  funext x
  change (Pi.basisFun ℂ (DivIdx T) c) x = shellVec c x
  rw [Pi.basisFun_apply]
  by_cases h : x = c
  · subst x
    simp [shellVec]
  · simp [shellVec, h]

/-- Primitive shell operators form a basis of the concrete diagonal projector algebra. -/
def shellOperatorBasis : Module.Basis (DivIdx T) ℂ (ProjectorAlg T) :=
  (shellBasis (T := T)).map (diagEquiv (T := T))

lemma shellOperatorBasis_apply (c : DivIdx T) :
    (shellOperatorBasis c : ProjectorAlg T).1 = shellEnd c := by
  rw [shellOperatorBasis, Module.Basis.map_apply, shellBasis_apply]
  rfl

end KomorebiCrossRadix
