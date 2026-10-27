module
public import Euler.FourScaledSeries
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

/-- Direct center chart, without division by a lower-root unit:
2F = w + X*(upper chart + lower Hasse tail). -/
def IsDirectHalfCore (A T F : Series) (w:D) : Prop :=
  C (2:D)*F=C w+X*(A+T)

lemma directHalfCore_coeff (A T F:Series) (w:D)
    (h:IsDirectHalfCore A T F w) (n:ℕ) :
    2*coeff (n+2) F=coeff (n+1) A+coeff (n+1) T := by
  have hc:=congrArg (coeff (n+2)) h
  simpa only [coeff_C_mul,map_add,coeff_C,show n+2=(n+1)+1 by omega,
    coeff_succ_X_mul,Nat.add_eq_zero_iff,Nat.one_ne_zero,and_false,ite_false,zero_add] using hc

/-- Exact coefficients when one nearest factor survives. The lower Hasse tail
is retained independently; it is not replaced by a constant. -/
theorem directOne_coeff (e t F:Series) (w ε:D)
    (h:IsDirectHalfCore ((1+C (2*ε)*X)*rescale (4:D) e) (rescale (4:D) t) F w)
    (n:ℕ) :
    coeff (n+2) F=(4:D)^n*(2*(coeff (n+1) e+coeff (n+1) t)+ε*coeff n e) := by
  apply cancel_two
  rw [directHalfCore_coeff _ _ _ _ h]
  have he:=oneRatio_coeff (1:D) ε e n
  simp only [oneRatio,map_one,one_mul] at he
  rw [he,coeff_rescale,pow_succ]
  ring

/-- Exact coefficients when the two nearest factors are symmetric. -/
theorem directTwo_coeff (e t F:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w)
    (n:ℕ) :
    coeff (n+3) F=2*(4:D)^n*(4*(coeff (n+2) e+coeff (n+2) t)-coeff n e) := by
  apply cancel_two
  have hc:=directHalfCore_coeff _ _ _ _ h (n+1)
  have he:=twoRatio_coeff (1:D) e n
  simp only [twoRatio,map_one,one_mul] at he
  rw [show n+1+2=n+3 by omega,show n+1+1=n+2 by omega,he,coeff_rescale] at hc
  rw [hc,pow_add]
  norm_num
  ring

lemma directTwo_coeff_two (e t F:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w) :
    coeff 2 F=2*(coeff 1 e+coeff 1 t) := by
  apply cancel_two
  rw [directHalfCore_coeff _ _ _ _ h 0]
  have he : coeff 1 ((1-C (4:D)*X^2)*rescale (4:D) e)=4*coeff 1 e := by
    simp only [sub_mul,one_mul,mul_assoc,map_sub,coeff_C_mul,coeff_rescale]
    rw [coeff_X_pow_mul']
    norm_num
  rw [he,coeff_rescale]
  norm_num
  ring

theorem directOne_lastOdd (e t F:Series) (w ε:D)
    (he:red (coeff 0 e)=1) (hε:red ε=1)
    (h:IsDirectHalfCore ((1+C (2*ε)*X)*rescale (4:D) e) (rescale (4:D) t) F w) :
    LastOdd F 2 := by
  constructor
  · rw [directOne_coeff _ _ _ _ _ h 0]
    have he0 : red (constantCoeff e)=1 := by simpa using he
    simp [he0,hε]
  · intro n hn
    obtain ⟨m,rfl⟩:=Nat.exists_eq_add_of_le (show 2≤n by omega)
    rw [show 2+m=m+2 by omega,directOne_coeff _ _ _ _ _ h]
    simp [show m≠0 by omega]

lemma directTwo_high_even (e t F:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w) :
    ∀n, 2≤n → red (coeff n F)=0 := by
  intro n hn
  by_cases he:n=2
  · subst n
    rw [directTwo_coeff_two _ _ _ _ h]
    simp
  · obtain ⟨m,rfl⟩:=Nat.exists_eq_add_of_le (show 3≤n by omega)
    rw [show 3+m=m+3 by omega,directTwo_coeff _ _ _ _ h]
    simp

lemma directTwo_divided_coeff (e t F K:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w)
    (hK:C (2:D)*K=F) (n:ℕ) :
    coeff (n+3) K=(4:D)^n*(4*(coeff (n+2) e+coeff (n+2) t)-coeff n e) := by
  apply cancel_two
  have hc:=congrArg (coeff (n+3)) hK
  rw [coeff_C_mul,directTwo_coeff _ _ _ _ h] at hc
  simpa only [mul_assoc] using hc

theorem directTwo_divided_lastOdd (e t F K:Series) (w:D)
    (he:red (coeff 0 e)=1)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w)
    (hK:C (2:D)*K=F) : LastOdd K 3 := by
  constructor
  · rw [directTwo_divided_coeff _ _ _ _ _ h hK 0]
    have he0 : red (constantCoeff e)=1 := by simpa using he
    simp [he0]
  · intro n hn
    obtain ⟨m,rfl⟩:=Nat.exists_eq_add_of_le (show 3≤n by omega)
    rw [show 3+m=m+3 by omega,directTwo_divided_coeff _ _ _ _ _ h hK]
    simp [show m≠0 by omega]

/-- The coefficient identities also prove convergence independently of the Euler construction. -/
lemma directOne_restricted (e t F:Series) (w ε:D)
    (h:IsDirectHalfCore ((1+C (2*ε)*X)*rescale (4:D) e) (rescale (4:D) t) F w) :
    Restricted F := by
  exact restricted_of_four_tail F 2
    (fun n => 2*(coeff (n+1) e+coeff (n+1) t)+ε*coeff n e)
    (directOne_coeff _ _ _ _ _ h)

lemma directTwo_restricted (e t F:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w) :
    Restricted F := by
  apply restricted_of_four_tail F 3
    (fun n => 2*(4*(coeff (n+2) e+coeff (n+2) t)-coeff n e))
  intro n
  rw [directTwo_coeff _ _ _ _ h]
  ring

lemma directTwo_divided_restricted (e t F K:Series) (w:D)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w)
    (hK:C (2:D)*K=F) : Restricted K := by
  exact restricted_of_four_tail K 3
    (fun n => 4*(coeff (n+2) e+coeff (n+2) t)-coeff n e)
    (directTwo_divided_coeff _ _ _ _ _ h hK)

/-- One and only one extra division can uncover the cubic. -/
theorem directTwo_dichotomy (e t F:Series) (w:D)
    (he:red (coeff 0 e)=1)
    (h:IsDirectHalfCore ((1-C (4:D)*X^2)*rescale (4:D) e) (rescale (4:D) t) F w) :
    LastOdd F 0 ∨ LastOdd F 1 ∨
      ∃K:Series, C (2:D)*K=F ∧ Restricted K ∧ LastOdd K 3 := by
  have high:=directTwo_high_even _ _ _ _ h
  by_cases h1:red (coeff 1 F)=0
  · by_cases h0:red (coeff 0 F)=0
    · obtain ⟨K,hK⟩:=divide_even_series F (by
        intro n
        rcases n with _ | _ | n
        · exact h0
        · exact h1
        · exact high _ (by omega))
      exact Or.inr (Or.inr ⟨K,hK,directTwo_divided_restricted _ _ _ _ _ h hK,
        directTwo_divided_lastOdd _ _ _ _ _ he h hK⟩)
    · exact Or.inl ⟨red_not_zero_eq_one _ h0,by
        intro n hn
        by_cases heq:n=1
        · simpa [heq] using h1
        · exact high n (by omega)⟩
  · exact Or.inr (Or.inl ⟨red_not_zero_eq_one _ h1,fun n hn=>high n (by omega)⟩)

end Komorebi.Euler
