module
public import PolynomialInverseCongruence
public import PolynomialLocalSurjective
public import Mathlib.Topology.Homeomorph.Lemmas

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialLocalInverse
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialPadicLift Komorebi.PolynomialInverseCongruence
open Komorebi.PolynomialLocalSurjective

variable {d e : ℕ}

/-- The actual polynomial evaluation restricted to its input and output residue balls. -/
def ballMap (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    residueBall p L x → residueBall p L (evalSystem F x) := fun a =>
  ⟨padicEval p F a.val, by
    intro i
    simpa only [padicEval_intCast] using
      padicEval_congruent p L F a.val (fun k => (x k : ℤ_[p])) a.property i⟩

theorem continuous_ballMap (p L : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    Continuous (ballMap p L F x) := by
  apply Continuous.subtype_mk
  exact (continuous_pi (continuous_padicEval p F)).comp continuous_subtype_val

theorem ballMap_bijective (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    Function.Bijective (ballMap p L F x) := by
  constructor
  · intro a b hab
    apply Subtype.ext
    apply padic_map_injective p F x hJ a.val b.val
    · intro i
      exact ((by simpa only [pow_one] using pow_dvd_pow (p : ℤ_[p]) hL) :
      (p : ℤ_[p]) ∣ (p : ℤ_[p])^L).trans
        (a.property i)
    · intro i
      exact ((by simpa only [pow_one] using pow_dvd_pow (p : ℤ_[p]) hL) :
      (p : ℤ_[p]) ∣ (p : ℤ_[p])^L).trans
        (b.property i)
    · exact congrArg Subtype.val hab
  · intro t
    obtain ⟨a, ha, hax⟩ := exists_padic_preimage p L hL F x hJ t.val t.property
    exact ⟨⟨a, hax⟩, Subtype.ext ha⟩

/-- Smooth square polynomial evaluation is a homeomorphism of the complete residue balls. -/
def localHomeomorph (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    residueBall p L x ≃ₜ residueBall p L (evalSystem F x) := by
  letI : CompactSpace (residueBall p L x) :=
    isCompact_iff_compactSpace.mp (isCompact_residueBall p L x)
  let f := Equiv.ofBijective (ballMap p L F x) (ballMap_bijective p L hL F x hJ)
  exact Continuous.homeoOfEquivCompactToT2 (f := f) (continuous_ballMap p L F x)

theorem localHomeomorph_apply (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x)) (a : residueBall p L x) :
    (localHomeomorph p L hL F x hJ a).val = padicEval p F a.val := rfl

theorem localHomeomorph_symm_eval (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (t : residueBall p L (evalSystem F x)) :
    padicEval p F ((localHomeomorph p L hL F x hJ).symm t).val = t.val := by
  exact congrArg Subtype.val ((localHomeomorph p L hL F x hJ).apply_symm_apply t)

theorem localHomeomorph_symm_congruent (p L N : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (t u : residueBall p L (evalSystem F x))
    (htu : ∀ i, (p : ℤ_[p])^N ∣ t.val i - u.val i) :
    ∀ i, (p : ℤ_[p])^N ∣
      ((localHomeomorph p L hL F x hJ).symm t).val i -
      ((localHomeomorph p L hL F x hJ).symm u).val i := by
  apply padic_inverse_congruence p N F x hJ
  · intro i
    exact ((by simpa only [pow_one] using pow_dvd_pow (p : ℤ_[p]) hL) :
      (p : ℤ_[p]) ∣ (p : ℤ_[p])^L).trans
      (((localHomeomorph p L hL F x hJ).symm t).property i)
  · intro i
    exact ((by simpa only [pow_one] using pow_dvd_pow (p : ℤ_[p]) hL) :
      (p : ℤ_[p]) ∣ (p : ℤ_[p])^L).trans
      (((localHomeomorph p L hL F x hJ).symm u).property i)
  · simpa only [localHomeomorph_symm_eval] using htu

#print axioms ballMap
#print axioms continuous_ballMap
#print axioms ballMap_bijective
#print axioms localHomeomorph
#print axioms localHomeomorph_apply
#print axioms localHomeomorph_symm_eval
#print axioms localHomeomorph_symm_congruent

end Komorebi.PolynomialLocalInverse
