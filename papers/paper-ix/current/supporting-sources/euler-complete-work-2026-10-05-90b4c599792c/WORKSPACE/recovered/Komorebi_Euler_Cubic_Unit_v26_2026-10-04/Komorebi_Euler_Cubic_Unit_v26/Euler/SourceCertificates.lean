module
public import Euler.SourceRows
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

/-- An actual finite Newton-source polynomial, before reduction. -/
def sourceNewtonPolynomial (Q : ℕ) : Polynomial D :=
  ∑ q ∈ Finset.range Q, Polynomial.C (sourceTap q) * descPochhammer D q

/-- Divisibility of every omitted tap, not an unverified truncation heuristic. -/
lemma sourceTap_redPow_zero (P Q q : ℕ) (hP : P ≤ 2*Q) (hq : Q ≤ q) :
    redPow P (sourceTap q)=0 := by
  have hpq : P ≤ 2*q := by omega
  obtain ⟨m, hm⟩ := Nat.exists_eq_add_of_le hpq
  have hpow : (4:D)^q = (2:D)^P * (2:D)^m := by
    rw [show (4:D)=(2:D)^2 by norm_num, ← pow_mul, hm, pow_add]
  rw [sourceTap, hpow, mul_assoc, map_mul, map_pow]
  have hz : (redPow P (2:D))^P=0 := by
    change (redPow P ((2:ℕ):D))^P=0
    rw [map_natCast, ← Nat.cast_pow]
    exact ZMod.natCast_self _
  rw [hz, zero_mul]

/-- Complete residue certificate for the numerator, including every omitted coefficient. -/
theorem sourceNumerator_residue_certificate (P Q : ℕ) (hP : P ≤ 2*Q) (n : ℕ) :
    redPow P (coeff n sourceNumerator) =
      ((sourceNewtonPolynomial Q).map (redPow P)).coeff n := by
  have hs := summable_sourceTap_weight (fun q => (descPochhammer D q).coeff n)
  have hm := hs.hasSum.map (redPow P) (continuous_redPow P)
  have ht : HasSum (fun q => redPow P (sourceTap q*(descPochhammer D q).coeff n))
      (∑ q ∈ Finset.range Q, redPow P (sourceTap q*(descPochhammer D q).coeff n)) := by
    apply hasSum_sum_of_ne_finset_zero
    intro q hq
    have hle : Q ≤ q := by simpa only [Finset.mem_range, not_lt] using hq
    rw [map_mul,sourceTap_redPow_zero P Q q hP hle,zero_mul]
  have h := hm.unique ht
  simpa [sourceNewtonPolynomial, Polynomial.coeff_map, Polynomial.coeff_sum,
    Polynomial.coeff_C_mul, Function.comp_def, coeff_sourceNumerator] using h

lemma sourceTap_one : sourceTap 1=4 := by
  apply Subtype.ext
  rw [sourceTap_coe]
  change (8:ℚ_[2])^1/(1+1).factorial=(4:ℚ_[2])
  norm_num

/-- Actual source numerator reduction modulo eight. -/
lemma sourceNumerator_mod8 :
    PowerSeries.map red8 sourceNumerator = 1+C (4:ZMod 8)*X := by
  ext n
  have h := sourceNumerator_residue_certificate 3 2 (by omega) n
  change red8 (coeff n sourceNumerator) = _
  rw [h]
  have h4 : redPow 3 (4:D)=(4:ZMod 8) := map_natCast _ 4
  simp [h4, eq_comm, sourceNewtonPolynomial, Finset.sum_range_succ, sourceTap_one,
    descPochhammer_zero, descPochhammer_one, Polynomial.coeff_add,
    Polynomial.coeff_one, Polynomial.coeff_C_mul, Polynomial.coeff_X,
    PowerSeries.coeff_one, PowerSeries.coeff_X, coeff_C_mul]

/-- The source itself has a complete, not point-sampled, mod-eight polynomial. -/
theorem eulerSource_mod8 :
    PowerSeries.map red8 eulerSource =
      1+C (2:ZMod 8)*X+C (4:ZMod 8)*X^2 := by
  have hn := congrArg (PowerSeries.map red8) eulerSource_identity
  rw [map_mul,sourceNumerator_mod8] at hn
  have hlin : PowerSeries.map red8 (1+C (2:D)*X)=1+C (2:ZMod 8)*X := by
    have h2 : red8 (2:D)=(2:ZMod 8) := map_natCast _ 2
    simp [h2]
  rw [hlin] at hn
  have hi := congrArg (PowerSeries.map red8) sourceOddInverse_identity
  rw [map_mul,hlin,map_one] at hi
  have hp : (1+C (2:ZMod 8)*X)*
      (1+C (2:ZMod 8)*X+C (4:ZMod 8)*X^2)=1+C (4:ZMod 8)*X := by
    have h8 : (8:PowerSeries (ZMod 8))=0 := by
      have hn := map_natCast (C : ZMod 8 →+* PowerSeries (ZMod 8)) 8
      rw [show ((8:ℕ):ZMod 8)=0 from ZMod.natCast_self 8, map_zero] at hn
      exact hn.symm
    have h4 : C (4:ZMod 8)=(4:PowerSeries (ZMod 8)) := map_natCast _ 4
    have h2 : C (2:ZMod 8)=(2:PowerSeries (ZMod 8)) := map_natCast _ 2
    rw [h4,h2]
    linear_combination (X^2+X^3)*h8
  calc
    _ = PowerSeries.map red8 sourceOddInverse *
      ((1+C (2:ZMod 8)*X)*PowerSeries.map red8 eulerSource) := by
        rw [← mul_assoc, mul_comm (PowerSeries.map red8 sourceOddInverse), hi, one_mul]
    _ = _ := by
      rw [hn,← hp,← mul_assoc,mul_comm (PowerSeries.map red8 sourceOddInverse),hi,one_mul]


/-- The explicit residue polynomial of the actual infinite source. -/
def sourceResidue8 : Polynomial (ZMod 8) :=
  1+Polynomial.C 2*Polynomial.X+Polynomial.C 4*Polynomial.X^2

lemma eulerSource_mod8_coeff (n : ℕ) :
    red8 (coeff n eulerSource)=sourceResidue8.coeff n := by
  have h := congrArg (coeff n) eulerSource_mod8
  simpa [sourceResidue8,Polynomial.coeff_add,Polynomial.coeff_C_mul,
    Polynomial.coeff_one,Polynomial.coeff_X,Polynomial.coeff_X_pow,
    PowerSeries.coeff_one,PowerSeries.coeff_X,PowerSeries.coeff_X_pow,coeff_C_mul,
    eq_comm] using h

theorem eulerSource_reval_mod8 (x : D) :
    red8 (reval eulerSource x)=1+2*red8 x+4*(red8 x)^2 := by
  have h := reval_residue_polynomial eulerSource_restricted 3 sourceResidue8
    eulerSource_mod8_coeff x
  simpa [sourceResidue8] using h

/-- First evaluated Hasse jet of the actual source, not a sampled polynomial. -/
theorem eulerSource_first_jet_mod8 (x : D) : red8 (rjet 1 eulerSource x)=2 := by
  have h := rjet_residue_polynomial eulerSource_restricted 3 sourceResidue8
    eulerSource_mod8_coeff 1 x
  have hp : Polynomial.hasseDeriv 1 sourceResidue8=Polynomial.C (2:ZMod 8) := by
    have h4 : Polynomial.C (4:ZMod 8)=(4:Polynomial (ZMod 8)) := map_natCast _ 4
    have h8 : (8:Polynomial (ZMod 8))=0 := by
      have hn := map_natCast (Polynomial.C : ZMod 8 →+* Polynomial (ZMod 8)) 8
      rw [show ((8:ℕ):ZMod 8)=0 from ZMod.natCast_self 8, map_zero] at hn
      exact hn.symm
    simp [sourceResidue8]
    rw [h4]
    calc
      _ = (8:Polynomial (ZMod 8))*Polynomial.X := by ring
      _ = 0 := by rw [h8,zero_mul]
  rw [hp] at h
  simpa using h

/-- The analytically evaluated Euler source has no critical point on the dyadic disc. -/
theorem eulerSource_deriv_ne_zero (x : D) :
    deriv (qeval eulerSource) (x:ℚ_[2])≠0 := by
  rw [deriv_qeval eulerSource_restricted]
  intro hx
  have hz : rjet 1 eulerSource x=0 := PadicInt.coe_eq_zero.mp hx
  have h:=eulerSource_first_jet_mod8 x
  rw [hz,map_zero] at h
  contradiction

end Komorebi.Euler
