import Mathlib.NumberTheory.Padics.PadicVal.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

noncomputable section
open scoped BigOperators

namespace KomorebiCrossRadix

/-- A zero-safe arithmetic replacement for the statement `v_p(z) ≥ k`.
Unlike `padicValInt`, this gives zero infinite depth automatically. -/
def PadicDepth (p k : ℕ) (z : ℤ) : Prop := (p : ℤ) ^ k ∣ z

/-- Integer coefficient vector for polynomial jets through degree `d`. -/
abbrev IntJet (d : ℕ) := Fin (d + 1) → ℤ

/-- The contribution from input jet `j` to output jet `q` under `X ↦ mX+r`. -/
def affineJetTerm {d : ℕ} (a : IntJet d) (m r : ℕ)
    (q j : Fin (d + 1)) : ℤ :=
  if _h : q.val ≤ j.val then
    a j * (Nat.choose j.val q.val : ℤ) * (m : ℤ) ^ q.val * (r : ℤ) ^ (j.val - q.val)
  else 0

/-- The exact integer jet coefficient obtained by summing all source contributions. -/
def affineJetCoeff {d : ℕ} (a : IntJet d) (m r : ℕ)
    (q : Fin (d + 1)) : ℤ :=
  ∑ j : Fin (d + 1), affineJetTerm a m r q j


/-- Prime-power depths add under multiplication. -/
theorem PadicDepth.mul {p ka kb : ℕ} {x y : ℤ}
    (hx : PadicDepth p ka x) (hy : PadicDepth p kb y) :
    PadicDepth p (ka + kb) (x * y) := by
  rcases hx with ⟨u, rfl⟩
  rcases hy with ⟨v, rfl⟩
  refine ⟨u * v, ?_⟩
  simp only [pow_add]
  ring

/-- Prime-power depth scales linearly under ordinary powers. -/
theorem PadicDepth.pow {p k : ℕ} {x : ℤ}
    (hx : PadicDepth p k x) (n : ℕ) :
    PadicDepth p (n * k) (x ^ n) := by
  rcases hx with ⟨u, rfl⟩
  refine ⟨u ^ n, ?_⟩
  rw [mul_pow]
  rw [Nat.mul_comm n k, pow_mul]

/-- Exact termwise tropical weight rule for a nonzero source position `q ≤ j`.
Any certified depths of the source coefficient, binomial coefficient, radix,
and translation parameter add with their natural multiplicities. -/
theorem PadicDepth_affineJetTerm
    {d p va vc vm vr m r : ℕ} (a : IntJet d)
    (q j : Fin (d + 1)) (hqj : q.val ≤ j.val)
    (ha : PadicDepth p va (a j))
    (hc : PadicDepth p vc (Nat.choose j.val q.val : ℤ))
    (hm : PadicDepth p vm (m : ℤ))
    (hr : PadicDepth p vr (r : ℤ)) :
    PadicDepth p
      (va + vc + q.val * vm + (j.val - q.val) * vr)
      (affineJetTerm a m r q j) := by
  simp only [affineJetTerm, hqj, ↓reduceDIte]
  have h1 := PadicDepth.mul ha hc
  have h2 := PadicDepth.pow hm q.val
  have h3 := PadicDepth.pow hr (j.val - q.val)
  have h12 := PadicDepth.mul h1 h2
  have h123 := PadicDepth.mul h12 h3
  simpa [Nat.add_assoc] using h123

/-- Nonarchimedean/tropical core: any common prime-power divisibility depth of all
source contributions survives their sum. Strict improvement is precisely the
cancellation surplus that this lower bound intentionally does not erase. -/
theorem PadicDepth_affineJetCoeff_of_terms
    {d p k m r : ℕ} (a : IntJet d) (q : Fin (d + 1))
    (hterms : ∀ j : Fin (d + 1), PadicDepth p k (affineJetTerm a m r q j)) :
    PadicDepth p k (affineJetCoeff a m r q) := by
  unfold PadicDepth affineJetCoeff
  exact Finset.dvd_sum fun j _ => hterms j

/-- Valuation-form corollary for a nonzero output coefficient. -/
theorem padicValInt_affineJetCoeff_ge
    {d p k m r : ℕ} [Fact p.Prime]
    (a : IntJet d) (q : Fin (d + 1))
    (hterms : ∀ j : Fin (d + 1), PadicDepth p k (affineJetTerm a m r q j))
    (hout : affineJetCoeff a m r q ≠ 0) :
    k ≤ padicValInt p (affineJetCoeff a m r q) := by
  have hdvd := PadicDepth_affineJetCoeff_of_terms a q hterms
  have hor := (padicValInt_dvd_iff (p := p) k (affineJetCoeff a m r q)).mp hdvd
  exact hor.resolve_left hout

/-- Exact cancellation is stronger than every finite divisibility depth. -/
theorem PadicDepth_all_of_affineJetCoeff_eq_zero
    {d p m r : ℕ} (a : IntJet d) (q : Fin (d + 1))
    (hz : affineJetCoeff a m r q = 0) :
    ∀ k : ℕ, PadicDepth p k (affineJetCoeff a m r q) := by
  intro k
  rw [hz]
  exact dvd_zero _


/-- Exact finite witness that cancellation surplus can be strict: two 2-adic
units can sum to an element of depth five. -/
theorem strict_cancellation_surplus_example :
    PadicDepth 2 5 (25 - 57 : ℤ) ∧
      ¬ PadicDepth 2 1 (25 : ℤ) ∧
      ¬ PadicDepth 2 1 (-57 : ℤ) := by
  norm_num [PadicDepth]

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.PadicDepth_affineJetTerm
#print axioms KomorebiCrossRadix.PadicDepth_affineJetCoeff_of_terms
#print axioms KomorebiCrossRadix.padicValInt_affineJetCoeff_ge
#print axioms KomorebiCrossRadix.strict_cancellation_surplus_example
