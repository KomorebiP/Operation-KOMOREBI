module
public import Euler.ResidueCertificates
public import Mathlib.NumberTheory.Padics.Hensel
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open Polynomial

lemma red_zero_iff_norm_lt_one (x : D) : red x=0 ↔ ‖x‖<1 := by
  rw [red_eq_zero_iff, PadicInt.norm_lt_one_iff_dvd]
  norm_num
  rfl

lemma red_ne_zero_norm_one (x : D) (h : red x ≠ 0) : ‖x‖=1 := by
  apply le_antisymm (PadicInt.norm_le_one x)
  apply le_of_not_gt
  intro hn
  exact h ((red_zero_iff_norm_lt_one x).mpr hn)

lemma same_residue_iff_norm_sub_lt_one (x y : D) : red x=red y ↔ ‖x-y‖<1 := by
  rw [← red_zero_iff_norm_lt_one]
  simp only [map_sub, sub_eq_zero]

lemma map_eval {S : Type*} [CommRing S] (f : D →+* S) (p : Polynomial D) (x : D) :
    f (p.eval x) = (p.map f).eval (f x) := by
  rw [Polynomial.eval_map, eval₂_at_apply]

/-- Hensel existence, uniqueness in the residue ball, and nonzero derivative,
with all objects living in the actual 2-adic integers. -/
theorem hensel_simple_residue (p : Polynomial D) (a : D)
    (hval : red (p.eval a)=0) (hder : red (p.derivative.eval a) ≠ 0) :
    ∃ z : D, p.eval z=0 ∧ red z=red a ∧ p.derivative.eval z ≠ 0 ∧
      ∀ w : D, p.eval w=0 → red w=red a → w=z := by
  have hnorm : ‖p.eval a‖<‖p.derivative.eval a‖^2 := by
    rw [red_ne_zero_norm_one _ hder, one_pow]
    exact (red_zero_iff_norm_lt_one _).mp hval
  have hh := hensels_lemma (p:=2) (F:=p) (a:=a) (by
    simpa only [coe_aeval_eq_eval] using hnorm)
  simp only [coe_aeval_eq_eval] at hh
  obtain ⟨z,hz,hza,hdz,hu⟩ := hh
  have ha1 := red_ne_zero_norm_one _ hder
  refine ⟨z,hz,?_,?_,?_⟩
  · exact (same_residue_iff_norm_sub_lt_one z a).mpr (by simpa [ha1] using hza)
  · intro hzero
    rw [hzero, norm_zero, ha1] at hdz
    norm_num at hdz
  · intro w hw hwa
    apply hu w hw
    rw [ha1]
    exact (same_residue_iff_norm_sub_lt_one w a).mp hwa

/-- A binary-squarefree reduction excludes all multiple polynomial roots. -/
theorem no_critical_root_of_residue (p : Polynomial D)
    (h : ∀ y : F₂, (p.map red).eval y=0 →
      (p.map red).derivative.eval y ≠ 0) :
    ∀ x : D, p.eval x=0 → p.derivative.eval x ≠ 0 := by
  intro x hx hd
  have hv : (p.map red).eval (red x)=0 := by rw [← map_eval, hx, map_zero]
  have hdv : (p.map red).derivative.eval (red x)=0 := by
    rw [derivative_map, ← map_eval, hd, map_zero]
  exact h (red x) hv hdv

/-- Complete polynomial version of the two-root certificate used at 514:
every dyadic polynomial with reduction X^2+X has exactly one simple root in
each residue class, regardless of its higher integral coefficients. -/
theorem two_simple_roots_of_reduction (p : Polynomial D)
    (hp : p.map red=(X^2+X : Polynomial F₂)) :
    ∃ a b : D, red a=0 ∧ red b=1 ∧ a ≠ b ∧
      (∀ x : D, p.eval x=0 ↔ x=a ∨ x=b) ∧
      (∀ x : D, p.eval x=0 → p.derivative.eval x ≠ 0) := by
  have hval (x : D) : red (p.eval x)=0 := by
    rw [map_eval, hp]
    simpa using (quadratic514_split_mod2 (red x)).1
  have hder (x : D) : red (p.derivative.eval x)=1 := by
    rw [map_eval, ← derivative_map, hp]
    have ht : (2:F₂)=0 := by decide +kernel
    norm_num [ht]
    exact Or.inl ht
  obtain ⟨a,ha,hra,hda,hua⟩ := hensel_simple_residue p 0 (hval 0) (by rw [hder]; decide)
  obtain ⟨b,hb,hrb,hdb,hub⟩ := hensel_simple_residue p 1 (hval 1) (by rw [hder]; decide)
  simp only [map_zero] at hra
  simp only [map_one] at hrb
  refine ⟨a,b,hra,hrb,?_,?_,?_⟩
  · intro hab
    have hc := congrArg red hab
    rw [hra,hrb] at hc
    norm_num at hc
  · intro x
    constructor
    · intro hx
      rcases binary_value (red x) with h0 | h1
      · exact Or.inl (hua x hx (by simpa using h0))
      · exact Or.inr (hub x hx (by simpa using h1))
    · rintro (rfl | rfl)
      · exact ha
      · exact hb
  · intro x hx hdx
    have hz := hder x
    rw [hdx,map_zero] at hz
    norm_num at hz

end Komorebi.Euler
