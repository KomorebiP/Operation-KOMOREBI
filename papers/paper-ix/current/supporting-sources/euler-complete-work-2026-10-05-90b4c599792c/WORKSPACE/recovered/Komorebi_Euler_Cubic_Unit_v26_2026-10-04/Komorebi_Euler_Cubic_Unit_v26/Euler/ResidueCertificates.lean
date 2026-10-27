module
public import Euler.Dyadic
public import Mathlib.Algebra.Polynomial.Taylor
public import Mathlib.Algebra.Polynomial.AlgebraMap
public import Mathlib.Algebra.Polynomial.Div
@[expose] public section
set_option linter.unusedSimpArgs false
namespace Komorebi.Euler
open Polynomial
set_option maxRecDepth 10000
set_option maxHeartbeats 4000000

/-- The complete finite certificate is reduced by the kernel, not native code. -/
theorem cubic161_mod8_no_triple :
    ∀ t y : ZMod 8,
    ¬ (4+(2+6*t)*y+6*y^2+y^3=0 ∧
        2+6*t+12*y+3*y^2=0 ∧ 6+3*y=0) := by
  decide +kernel

theorem cubic161_mod2_no_triple :
    ∀ y : ZMod 2, ¬ (y^3+y=0 ∧ 3*y^2+1=0 ∧ 3*y=0) := by
  decide +kernel

theorem quadratic514_left_rootfree :
    ∀ y : ZMod 4, y^2+2=0 → False := by
  decide +kernel

theorem quadratic514_right_rootfree :
    ∀ y : ZMod 4, 3*y^2+2=0 → False := by
  decide +kernel

theorem quadratic514_split_mod2 :
    ∀ y : ZMod 2, y^2+y=0 ∧ 2*y+1=1 := by
  decide +kernel

/-- Both original 514 quadratic templates are root-free whenever t is odd. -/
theorem quadratic514_templates_rootfree :
    ∀ t y : ZMod 4, (t=1 ∨ t=3) →
      y^2+3*(1+t)*y+2 ≠ 0 ∧ 3*y^2+3*(1+t)*y+2 ≠ 0 := by
  decide +kernel

noncomputable section

def TripleJetZero (p : Polynomial D) (x : D) : Prop :=
  ∀ n : Fin 3, (hasseDeriv n.val p).eval x=0

/-- Hasse vanishing is genuine polynomial multiplicity, not a formal label. -/
theorem tripleJetZero_iff_cube_dvd (p : Polynomial D) (x : D) :
    TripleJetZero p x ↔ (X-C x)^3 ∣ p := by
  rw [X_sub_C_pow_dvd_iff, X_pow_dvd_iff]
  constructor
  · intro h n hn
    have hcoef := h ⟨n,hn⟩
    simpa only [← taylor_coeff, taylor_apply] using hcoef
  · intro h n
    have hcoef := h n.val n.isLt
    simpa only [← taylor_coeff, taylor_apply] using hcoef

/-- Evaluation of Hasse jets commutes with any ring-hom reduction. -/
lemma map_hasse_eval {R S : Type*} [CommRing R] [CommRing S]
    (f : R →+* S) (p : Polynomial R) (n : ℕ) (x : R) :
    f ((hasseDeriv n p).eval x) =
      (hasseDeriv n (p.map f)).eval (f x) := by
  rw [hasseDeriv_map, eval_map, eval₂_at_apply]

/-- General soundness of a finite residue triple-jet certificate. -/
theorem residue_no_triple {S : Type*} [CommRing S]
    (f : D →+* S) (p : Polynomial D) (Q : Polynomial S)
    (hmap : p.map f=Q)
    (hcert : ∀ y : S, ¬ ∀ n : Fin 3, (hasseDeriv n.val Q).eval y=0) :
    ∀ x : D, ¬ TripleJetZero p x := by
  intro x hx
  apply hcert (f x)
  intro n
  have h := congrArg f (hx n)
  rw [map_zero, map_hasse_eval, hmap] at h
  exact h

/-- The third residue class in the terminal-161 non-triple certificate. -/
def model161 (t : ZMod 8) : Polynomial (ZMod 8) :=
  C 4 + monomial 1 (2+6*t) + monomial 2 6 + monomial 3 1

lemma model161_jets (t y : ZMod 8) :
    (hasseDeriv 0 (model161 t)).eval y = 4+(2+6*t)*y+6*y^2+y^3 ∧
    (hasseDeriv 1 (model161 t)).eval y = 2+6*t+12*y+3*y^2 ∧
    (hasseDeriv 2 (model161 t)).eval y = 6+3*y := by
  simp only [model161, map_add, hasseDeriv_monomial, hasseDeriv_C,
    eval_add, eval_monomial]
  norm_num [hasseDeriv_zero', hasseDeriv_C 2 (4 : ZMod 8) (by decide)]
  ring

lemma model161_certificate (t : ZMod 8) :
    ∀ y, ¬ ∀ n : Fin 3, (hasseDeriv n.val (model161 t)).eval y=0 := by
  intro y h
  obtain ⟨h0,h1,h2⟩ := model161_jets t y
  apply cubic161_mod8_no_triple t y
  exact ⟨h0.symm.trans (h ⟨0,by decide⟩),
    h1.symm.trans (h ⟨1,by decide⟩), h2.symm.trans (h ⟨2,by decide⟩)⟩

/-- All polynomials with the certified terminal-161 eight-bit residue are
free of triple roots over the actual dyadic integers. -/
theorem terminal161_mod8_no_cube (p : Polynomial D) (t : ZMod 8)
    (hp : p.map red8=model161 t) :
    ∀ x : D, ¬ (X-C x)^3 ∣ p := by
  intro x hx
  apply residue_no_triple red8 p (model161 t) hp (model161_certificate t) x
  exact (tripleJetZero_iff_cube_dvd p x).mpr hx

/-- The second terminal-161 class uses only the residue Y^3+Y. -/
theorem terminal161_mod2_no_cube (p : Polynomial D)
    (hp : p.map red=(X^3+X : Polynomial F₂)) :
    ∀ x : D, ¬ (X-C x)^3 ∣ p := by
  apply fun x hx => residue_no_triple red p (X^3+X) hp ?_ x
    ((tripleJetZero_iff_cube_dvd p x).mpr hx)
  intro y h
  have h0 := h ⟨0,by decide⟩
  have h1 := h ⟨1,by decide⟩
  have h2 := h ⟨2,by decide⟩
  have hX : (X^3+X : Polynomial F₂)=monomial 3 1+monomial 1 1 := by simp only [← C_mul_X_pow_eq_monomial, C_1, one_mul, pow_one]
  rw [hX] at h0 h1 h2
  norm_num [hasseDeriv_monomial] at h0 h1 h2
  exact cubic161_mod2_no_triple y ⟨by simpa using h0, by simpa using h1,
    by simpa using h2⟩

/-- Root-free conclusions for arbitrary polynomial tails with the certified
514 residues. The construction of the Euler-to-polynomial bridge is separate. -/
theorem terminal514_rootfree (p : Polynomial D) (t u : ZMod 4)
    (ht : t=1 ∨ t=3) (hu : u=1 ∨ u=3)
    (hp : p.map red4=C u*X^2+C (3*(1+t))*X+C 2) :
    ∀ x : D, p.eval x ≠ 0 := by
  intro x hx
  have h := congrArg red4 hx
  rw [map_zero, ← eval₂_at_apply, ← eval_map, hp] at h
  simp only [eval_add, eval_mul, eval_C, eval_pow, eval_X] at h
  rcases hu with rfl | rfl
  · exact (quadratic514_templates_rootfree t (red4 x) ht).1 (by simpa using h)
  · exact (quadratic514_templates_rootfree t (red4 x) ht).2 h

end
end Komorebi.Euler
