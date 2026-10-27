module
public import Euler.CubicUnitObstruction
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

lemma cubicCritical_discriminant_mod16_zero (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (x:D)
    (hx:CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2])) :
    redPow 4 (cubicJetDiscriminant a b c u R hR)=0 := by
  obtain ⟨z,hz⟩:=cubicCritical_discriminant_divisible a b c u R hR x hx
  have h16:redPow 4 (16:D)=0 := by rw [map_ofNat];decide
  rw [hz]
  simp only [map_mul,h16,zero_mul]

/-- A finite residue test at the unique inflection address controls the infinite core. -/
theorem cubicCore_no_critical_of_jet_residue (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R) (p:Polynomial (ZMod 16))
    (hp:∀n,redPow 4 (coeff n (cubicCoreSeries a b c (u:D) R))=p.coeff n)
    (ht:∀y:ZMod 16,(Polynomial.hasseDeriv 2 p).eval y=0 →
      4*((Polynomial.hasseDeriv 1 p).eval y)^3+
        27*((Polynomial.hasseDeriv 3 p).eval y)*(p.eval y)^2≠0)
    (x:D) : ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2]) := by
  intro hx
  let ρ:=cubicInflectionPoint c u R hR
  have hc:=cubicInflection_rjet_two a b c u R hR
  have hcmod:=congrArg (redPow 4) hc
  rw [rjet_residue_polynomial (cubicCore_restricted a b c (u:D) hR) 4 p hp 2,
    map_zero] at hcmod
  have hd:=cubicCritical_discriminant_mod16_zero a b c u R hR x hx
  dsimp only [cubicJetDiscriminant] at hd
  simp only [map_add,map_mul,map_pow,map_ofNat] at hd
  rw [rjet_residue_polynomial (cubicCore_restricted a b c (u:D) hR) 4 p hp 1,
    rjet_residue_polynomial (cubicCore_restricted a b c (u:D) hR) 4 p hp 3,
    reval_residue_polynomial (cubicCore_restricted a b c (u:D) hR) 4 p hp] at hd
  exact ht (redPow 4 ρ) hcmod hd

def cubic161B3Residue : Polynomial (ZMod 16) :=
  Polynomial.C 12+Polynomial.C 5*Polynomial.X+Polynomial.C 10*Polynomial.X^2+
    Polynomial.C 11*Polynomial.X^3+Polynomial.C 8*Polynomial.X^4

/-- Only a residue-shape certificate; Euler-index-to-coefficient verification is separate. -/
theorem cubic161B3_residue_test (y:ZMod 16) :
    (Polynomial.hasseDeriv 2 cubic161B3Residue).eval y=0 →
      4*((Polynomial.hasseDeriv 1 cubic161B3Residue).eval y)^3+
        27*((Polynomial.hasseDeriv 3 cubic161B3Residue).eval y)*
          (cubic161B3Residue.eval y)^2≠0 := by
  have h1 : Polynomial.hasseDeriv 1 cubic161B3Residue =
      Polynomial.C 5+Polynomial.C 4*Polynomial.X+Polynomial.X^2 := by
    ext n
    rcases n with _ | _ | _ | _ | _ | n <;>
      norm_num [cubic161B3Residue,Polynomial.hasseDeriv_coeff,Nat.choose,Polynomial.coeff_X] <;>
      first | decide | omega
  have h2 : Polynomial.hasseDeriv 2 cubic161B3Residue =
      Polynomial.C 10+Polynomial.X := by
    ext n
    rcases n with _ | _ | _ | _ | _ | n <;>
      norm_num [cubic161B3Residue,Polynomial.hasseDeriv_coeff,Nat.choose,Polynomial.coeff_X] <;>
      decide
  have h3 : Polynomial.hasseDeriv 3 cubic161B3Residue =Polynomial.C 11 := by
    ext n
    rcases n with _ | _ | _ | _ | _ | n <;>
      norm_num [cubic161B3Residue,Polynomial.hasseDeriv_coeff,Nat.choose,Polynomial.coeff_X]
    decide
  rw [h1,h2,h3]
  simp only [cubic161B3Residue,Polynomial.eval_add,Polynomial.eval_mul,
    Polynomial.eval_pow,Polynomial.eval_C,Polynomial.eval_X]
  revert y
  decide +kernel


/-- The certified shape excludes repeated roots of any infinite core with that full reduction. -/
theorem cubicCore_B3_shape_no_critical (a b c:D) (u:Dˣ) (R:Series)
    (hR:Restricted R)
    (hp:∀n,redPow 4 (coeff n (cubicCoreSeries a b c (u:D) R))=
      cubic161B3Residue.coeff n) (x:D) :
    ¬CriticalZero (qeval (cubicCoreSeries a b c (u:D) R)) (x:ℚ_[2]) :=
  cubicCore_no_critical_of_jet_residue a b c u R hR cubic161B3Residue hp
    cubic161B3_residue_test x

end Komorebi.Euler
