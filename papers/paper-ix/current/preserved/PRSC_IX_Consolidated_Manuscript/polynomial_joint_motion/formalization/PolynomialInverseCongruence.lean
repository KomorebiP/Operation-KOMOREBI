module
public import PolynomialPadicUnique

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialInverseCongruence
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
open Komorebi.PolynomialDigitBridge Komorebi.PolynomialPadicLift
open Komorebi.PolynomialPadicUnique Komorebi.PolynomialSurjectiveStep
variable {d e : ℕ}

/-- The actual square Jacobian recovers one further input digit from an output digit.
The modulus may be any positive integer. -/
theorem integer_inverse_congruence_step (q n : ℕ) (hq : 0 < q) (hn : 1 ≤ n)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (a b : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian q F a))
    (hab : ∀ i, (q : ℤ)^n ∣ b i - a i)
    (hF : ∀ i, (q : ℤ)^(n+1) ∣ evalSystem F b i - evalSystem F a i) :
    ∀ i, (q : ℤ)^(n+1) ∣ b i - a i := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  choose t ht using hab
  have hb : b = fun i => a i + (q : ℤ)^n * t i := by
    funext i
    linarith [ht i]
  have hdir : ∀ i, (q : ℤ) ∣ jacobian F a t i := by
    intro i
    have hrem := Komorebi.PolynomialTaylor.taylor_step_dvd (F i) a t q n hn
    rw [← hb] at hrem
    have hmul : (q : ℤ)^(n+1) ∣ (q : ℤ)^n * jacobian F a t i := by
      convert dvd_sub (hF i) hrem using 1
      · rfl
      · dsimp [evalSystem, jacobian, Komorebi.PolynomialTaylor.directional]
        ring
    rwa [pow_succ, mul_dvd_mul_iff_left
      (pow_ne_zero n (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hq)))] at hmul
  have hz : digitJacobian q F a (reduction q d t) = 0 := by
    rw [reduction_jacobian, reduction_zero_iff]
    exact hdir
  have hinj : Function.Injective (digitJacobian q F a) :=
    Finite.injective_iff_surjective.mpr hJ
  have htzero : reduction q d t = 0 := hinj (hz.trans (map_zero _).symm)
  have htdvd := (reduction_zero_iff q t).mp htzero
  intro i
  rw [ht i, pow_succ]
  exact mul_dvd_mul_left ((q : ℤ)^n) (htdvd i)

/-- A square smooth integer polynomial map reflects all congruence depths
inside a fixed residue class, also for positive composite moduli. -/
theorem integer_inverse_congruence (q N : ℕ) (hq : 0 < q)
    (F : Fin d → MvPolynomial (Fin d) ℤ) (a b : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian q F a))
    (hab : ∀ i, (q : ℤ) ∣ b i - a i)
    (hF : ∀ i, (q : ℤ)^N ∣ evalSystem F b i - evalSystem F a i) :
    ∀ i, (q : ℤ)^N ∣ b i - a i := by
  induction N with
  | zero => simp
  | succ N ih =>
    by_cases hN : N = 0
    · simpa only [hN, zero_add, pow_one] using hab
    · apply integer_inverse_congruence_step q N hq (by omega) F a b hJ
      · apply ih
        intro i
        exact (pow_dvd_pow (q : ℤ) (Nat.le_succ N)).trans (hF i)
      · exact hF

/-- Actual p-adic polynomial evaluation preserves every coordinate congruence. -/
theorem padicEval_congruent (p N : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin d) ℤ) (a b : Fin d → ℤ_[p])
    (hab : ∀ i, (p : ℤ_[p])^N ∣ a i - b i) :
    ∀ i, (p : ℤ_[p])^N ∣ padicEval p F a i - padicEval p F b i := by
  intro i
  apply (toZModPow_eq_iff_dvd_sub p N _ _).mp
  have ha := MvPolynomial.hom_eval₂ (F i) (Int.castRingHom ℤ_[p])
    (PadicInt.toZModPow N) a
  have hb := MvPolynomial.hom_eval₂ (F i) (Int.castRingHom ℤ_[p])
    (PadicInt.toZModPow N) b
  simp only [padicEval]
  rw [ha, hb]
  congr 1
  funext k
  exact (toZModPow_eq_iff_dvd_sub p N _ _).mpr (hab k)

/-- A square polynomial map with surjective actual reduced Jacobian reflects
all p-adic congruence depths in the residue ball of the integer base point. -/
theorem padic_inverse_congruence (p N : ℕ) [Fact (Nat.Prime p)]
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (hax : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p]) ∣ b i - (x i : ℤ_[p]))
    (hF : ∀ i, (p : ℤ_[p])^N ∣ padicEval p F a i - padicEval p F b i) :
    ∀ i, (p : ℤ_[p])^N ∣ a i - b i := by
  let y := truncInt p (N+1) a
  let z := truncInt p (N+1) b
  have hay : ∀ i, (p : ℤ_[p])^N ∣ a i - (y i : ℤ_[p]) := by
    intro i
    exact (pow_dvd_pow (p : ℤ_[p]) (Nat.le_succ N)).trans
      (truncInt_precision p (N+1) a i)
  have hbz : ∀ i, (p : ℤ_[p])^N ∣ b i - (z i : ℤ_[p]) := by
    intro i
    exact (pow_dvd_pow (p : ℤ_[p]) (Nat.le_succ N)).trans
      (truncInt_precision p (N+1) b i)
  have hyx : ∀ i, (p : ℤ) ∣ y i - x i := by
    intro i
    have hy1 : (p : ℤ_[p]) ∣ a i - (y i : ℤ_[p]) :=
      (dvd_pow_self (p : ℤ_[p]) (Nat.succ_ne_zero N)).trans
        (truncInt_precision p (N+1) a i)
    have hcast : (p : ℤ_[p])^1 ∣ ((y i - x i : ℤ) : ℤ_[p]) := by
      simpa only [pow_one, Int.cast_sub, sub_sub_sub_cancel_left] using dvd_sub (hax i) hy1
    simpa only [pow_one] using (int_pow_dvd_iff p 1 (y i-x i)).mpr hcast
  have hzx : ∀ i, (p : ℤ) ∣ z i - x i := by
    intro i
    have hz1 : (p : ℤ_[p]) ∣ b i - (z i : ℤ_[p]) :=
      (dvd_pow_self (p : ℤ_[p]) (Nat.succ_ne_zero N)).trans
        (truncInt_precision p (N+1) b i)
    have hcast : (p : ℤ_[p])^1 ∣ ((z i - x i : ℤ) : ℤ_[p]) := by
      simpa only [pow_one, Int.cast_sub, sub_sub_sub_cancel_left] using dvd_sub (hbx i) hz1
    simpa only [pow_one] using (int_pow_dvd_iff p 1 (z i-x i)).mpr hcast
  have hJy : Function.Surjective (digitJacobian p F y) := by
    rw [digitJacobian_eq p F x y hyx]
    exact hJ
  have hzy : ∀ i, (p : ℤ) ∣ z i - y i := by
    intro i
    simpa only [sub_sub_sub_cancel_right] using dvd_sub (hzx i) (hyx i)
  have hFy := padicEval_congruent p N F a (fun i => (y i : ℤ_[p])) hay
  have hFz := padicEval_congruent p N F b (fun i => (z i : ℤ_[p])) hbz
  have hFzy : ∀ i, (p : ℤ)^N ∣ evalSystem F z i - evalSystem F y i := by
    intro i
    apply (int_pow_dvd_iff p N _).mpr
    have h := dvd_sub (dvd_sub (hFy i) (hFz i)) (hF i)
    rw [padicEval_intCast, padicEval_intCast] at h
    convert h using 1
    push_cast
    ring
  have hzyN := integer_inverse_congruence p N (Fact.out : Nat.Prime p).pos F y z hJy hzy hFzy
  intro i
  have hyz : (p : ℤ_[p])^N ∣ (y i : ℤ_[p]) - (z i : ℤ_[p]) := by
    have h := (int_pow_dvd_iff p N _).mp (hzyN i)
    simpa only [Int.cast_sub, neg_sub] using dvd_neg.mpr h
  have h := dvd_add (dvd_sub (hay i) (hbz i)) hyz
  convert h using 1
  ring

/-- On a smooth square residue ball the input and output have exactly the
same congruences at every precision. -/
theorem padic_congruence_iff (p N : ℕ) [Fact (Nat.Prime p)]
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (hax : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p]) ∣ b i - (x i : ℤ_[p])) :
    (∀ i, (p : ℤ_[p])^N ∣ padicEval p F a i - padicEval p F b i) ↔
      (∀ i, (p : ℤ_[p])^N ∣ a i - b i) :=
  ⟨padic_inverse_congruence p N F x hJ a b hax hbx, padicEval_congruent p N F a b⟩

/-- The actual polynomial map is injective on its smooth square residue ball. -/
theorem padic_map_injective (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin d → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hJ : Function.Surjective (digitJacobian p F x))
    (a b : Fin d → ℤ_[p])
    (hax : ∀ i, (p : ℤ_[p]) ∣ a i - (x i : ℤ_[p]))
    (hbx : ∀ i, (p : ℤ_[p]) ∣ b i - (x i : ℤ_[p]))
    (hF : padicEval p F a = padicEval p F b) : a = b := by
  funext i
  apply PadicInt.ext_of_toZModPow.mp
  intro N
  apply (toZModPow_eq_iff_dvd_sub p N _ _).mpr
  exact padic_inverse_congruence p N F x hJ a b hax hbx (by simp only [hF, sub_self, dvd_zero, implies_true]) i

#print axioms integer_inverse_congruence_step
#print axioms integer_inverse_congruence
#print axioms padicEval_congruent
#print axioms padic_inverse_congruence
#print axioms padic_congruence_iff
#print axioms padic_map_injective

end Komorebi.PolynomialInverseCongruence
