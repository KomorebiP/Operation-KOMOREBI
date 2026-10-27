module
public import PolynomialPadicLift
public import Mathlib.NumberTheory.Padics.RingHoms

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPadicUnique
open Komorebi.PolynomialObstruction Komorebi.PolynomialDigitBridge
open Komorebi.PolynomialLiftCounts Komorebi.PolynomialSmoothCounts
open Komorebi.PolynomialPadicLift

variable {d e : ℕ}

/-- Equality in the actual residue quotient is equivalent to p-adic divisibility. -/
theorem toZModPow_eq_iff_dvd_sub (p n : ℕ) [Fact (Nat.Prime p)]
    (a b : ℤ_[p]) :
    PadicInt.toZModPow n a = PadicInt.toZModPow n b ↔
      (p : ℤ_[p])^n ∣ a - b := by
  rw [← sub_eq_zero, ← map_sub, ← RingHom.mem_ker,
    PadicInt.ker_toZModPow, Ideal.mem_span_singleton]

/-- Integer divisibility is faithfully detected inside the p-adic integers. -/
theorem int_pow_dvd_iff (p n : ℕ) [Fact (Nat.Prime p)] (z : ℤ) :
    (p : ℤ)^n ∣ z ↔ (p : ℤ_[p])^n ∣ (z : ℤ_[p]) := by
  have h := toZModPow_eq_iff_dvd_sub p n (z : ℤ_[p]) 0
  simpa only [map_intCast, map_zero, sub_zero, ZMod.intCast_zmod_eq_zero_iff_dvd,
    Nat.cast_pow] using h

/-- Canonical integer representatives of an arbitrary p-adic vector modulo p^n. -/
def truncInt (p n : ℕ) [Fact (Nat.Prime p)] (a : Fin d → ℤ_[p]) : Fin d → ℤ :=
  fun i => ((PadicInt.toZModPow n (a i)).val : ℤ)

/-- The canonical integer representative retains exactly the requested precision. -/
theorem truncInt_precision (p n : ℕ) [Fact (Nat.Prime p)]
    (a : Fin d → ℤ_[p]) (i : Fin d) :
    (p : ℤ_[p])^n ∣ a i - (truncInt p n a i : ℤ_[p]) := by
  apply (toZModPow_eq_iff_dvd_sub p n _ _).mp
  simp [truncInt]

/-- Evaluation in every residue quotient commutes with canonical truncation. -/
theorem truncInt_eval_residue (p n : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (a : Fin d → ℤ_[p]) (i : Fin e) :
    (evalSystem F (truncInt p n a) i : ZMod (p^n)) =
      PadicInt.toZModPow n (padicEval p F a i) := by
  have h := MvPolynomial.hom_eval₂ (F i) (Int.castRingHom ℤ_[p])
    (PadicInt.toZModPow n) a
  rw [padicEval, h]
  change (Int.castRingHom (ZMod (p^n))) (MvPolynomial.eval (truncInt p n a) (F i)) = _
  rw [MvPolynomial.eval₂_comp]
  congr 1
  · ext z
    simp
  · funext k
    simp [truncInt]

/-- An exact p-adic polynomial root gives genuine integer roots at every finite precision. -/
theorem truncInt_root (p n : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (a : Fin d → ℤ_[p])
    (ha : ∀ i, padicEval p F a i = 0) :
    ∀ i, (p : ℤ)^n ∣ evalSystem F (truncInt p n a) i := by
  intro i
  have h := truncInt_eval_residue p n F a i
  rw [ha i, map_zero] at h
  simpa only [ZMod.intCast_zmod_eq_zero_iff_dvd, Nat.cast_pow] using h

/-- An exact root in an integer residue ball produces an actual next-level lift. -/
def rootResidueLift (p n : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (a : Fin d → ℤ_[p]) (ha : ∀ i, padicEval p F a i = 0)
    (hax : ∀ i, (p : ℤ_[p])^n ∣ a i - (x i : ℤ_[p])) : ActualLifts p n F x := by
  refine ⟨⟨fun i => PadicInt.toZModPow (n+1) (a i), ?_⟩, ?_⟩
  · intro i
    apply (int_pow_dvd_iff p n _).mpr
    have hc := dvd_trans (pow_dvd_pow (p : ℤ_[p]) (Nat.le_succ n))
      (truncInt_precision p (n+1) a i)
    have h := dvd_sub (hax i) hc
    simpa only [Int.cast_sub, sub_sub_sub_cancel_left, truncInt] using h
  · exact truncInt_root p (n+1) F a ha

/-- In the square smooth case, any two exact roots over a lower integer root
have the same next residue. This uses the checked count of actual lift classes. -/
theorem root_next_residue_eq (p n : ℕ) [Fact (Nat.Prime p)] (hn : 1 ≤ n)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^n ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ i, padicEval p F a i = 0) (hb : ∀ i, padicEval p F b i = 0)
    (hax : ∀ i, (p : ℤ_[p])^n ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p])^n ∣ b i - (x i : ℤ_[p])) :
    ∀ i, PadicInt.toZModPow (n+1) (a i) = PadicInt.toZModPow (n+1) (b i) := by
  have hcard : Nat.card (ActualLifts p n F x) = 1 := by
    simpa only [Nat.sub_self, pow_zero] using smooth_lift_card p n hn F x hx hJ
  let : Subsingleton (ActualLifts p n F x) := (Nat.card_eq_one_iff_unique.mp hcard).1
  have h := Subsingleton.elim (rootResidueLift p n F x a ha hax)
    (rootResidueLift p n F x b hb hbx)
  intro i
  exact congrFun (congrArg (fun y : ActualLifts p n F x => y.val.val) h) i

/-- Arbitrary exact roots in the same smooth square residue ball coincide.
No chosen tower, agreement with a tower limit, or root uniqueness is assumed. -/
theorem padic_root_unique (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (ha : ∀ i, padicEval p F a i = 0) (hb : ∀ i, padicEval p F b i = 0)
    (hax : ∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p])^L ∣ b i - (x i : ℤ_[p])) : a = b := by
  have hab : ∀ n i, (p : ℤ_[p])^(L+n) ∣ a i - b i := by
    intro n
    induction n with
    | zero =>
        intro i
        simpa only [Nat.add_zero, sub_sub_sub_cancel_right] using dvd_sub (hax i) (hbx i)
    | succ n ih =>
        let y := truncInt p (L+n) a
        have hay : ∀ i, (p : ℤ_[p])^(L+n) ∣ a i - (y i : ℤ_[p]) :=
          truncInt_precision p (L+n) a
        have hby : ∀ i, (p : ℤ_[p])^(L+n) ∣ b i - (y i : ℤ_[p]) := by
          intro i
          simpa only [sub_sub_sub_cancel_left] using dvd_sub (hay i) (ih i)
        have hyx : ∀ i, (p : ℤ) ∣ y i - x i := by
          intro i
          have hlow := dvd_trans (pow_dvd_pow (p : ℤ_[p]) (Nat.le_add_right L n)) (hay i)
          have hdiff : (p : ℤ_[p])^L ∣ ((y i - x i : ℤ) : ℤ_[p]) := by
            simpa only [Int.cast_sub, sub_sub_sub_cancel_left] using dvd_sub (hax i) hlow
          exact dvd_trans (by simpa only [pow_one] using pow_dvd_pow (p : ℤ) hL)
            ((int_pow_dvd_iff p L _).mpr hdiff)
        have hyJ : Function.Surjective (digitJacobian p F y) := by
          rw [Komorebi.PolynomialSurjectiveStep.digitJacobian_eq p F x y hyx]
          exact hJ
        have heq := root_next_residue_eq p (L+n) (by omega) F y
          (truncInt_root p (L+n) F a ha) hyJ a b ha hb hay hby
        intro i
        simpa only [Nat.add_assoc] using
          (toZModPow_eq_iff_dvd_sub p (L+n+1) (a i) (b i)).mp (heq i)
  funext i
  apply PadicInt.ext_of_toZModPow.mp
  intro n
  apply (toZModPow_eq_iff_dvd_sub p n _ _).mpr
  exact dvd_trans (pow_dvd_pow (p : ℤ_[p]) (Nat.le_add_left n L)) (hab n i)

/-- A square system with surjective actual reduced Jacobian has exactly one
p-adic root in the prescribed lower residue class. -/
theorem exists_unique_padic_root (p L : ℕ) [Fact (Nat.Prime p)] (hL : 1 ≤ L)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (p : ℤ)^L ∣ evalSystem F x i)
    (hJ : Function.Surjective (digitJacobian p F x)) :
    ∃! a : Fin d → ℤ_[p],
      (∀ i, MvPolynomial.eval₂ (Int.castRingHom ℤ_[p]) a (F i) = 0) ∧
      (∀ i, (p : ℤ_[p])^L ∣ a i - (x i : ℤ_[p])) := by
  obtain ⟨a, ha, hax⟩ := exists_padic_root p L hL F x hx hJ
  refine ⟨a, ⟨ha, hax⟩, ?_⟩
  intro b hb
  exact padic_root_unique p L hL F x hJ b a hb.1 ha hb.2 hax

#print axioms toZModPow_eq_iff_dvd_sub
#print axioms int_pow_dvd_iff
#print axioms truncInt
#print axioms truncInt_precision
#print axioms truncInt_eval_residue
#print axioms truncInt_root
#print axioms rootResidueLift
#print axioms root_next_residue_eq
#print axioms padic_root_unique
#print axioms exists_unique_padic_root

end Komorebi.PolynomialPadicUnique
