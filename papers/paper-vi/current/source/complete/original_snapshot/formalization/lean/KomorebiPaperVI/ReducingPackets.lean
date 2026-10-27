import KomorebiPaperVI.Semigroups

/-! Author: Komorebi P. From vanishing generator blocks to independent exponential evolution. -/
namespace KomorebiPaperVI.ReducingPackets
open KomorebiPaperVI.Semigroups
open scoped BigOperators
variable {R I : Type*} [Fintype I]

section Ring
variable [Ring R]

theorem generator_commutes (P : I → R) (hP : ∑ a, P a=1) (A : R)
    (h : ∀ b a, b≠a → P b*A*P a=0) (a : I) : P a*A=A*P a := by
  classical
  have hl : A*P a=P a*A*P a := by
    calc
      _ = (∑ b, P b)*A*P a := by rw [hP,one_mul]
      _ = ∑ b, P b*A*P a := by rw [Finset.sum_mul,Finset.sum_mul]
      _ = _ := Finset.sum_eq_single a (fun b _ hb => h b a hb) (by simp)
  have hr : P a*A=P a*A*P a := by
    calc
      _ = P a*A*(∑ b, P b) := by rw [hP,mul_one]
      _ = ∑ b, P a*A*P b := by rw [Finset.mul_sum]
      _ = _ := Finset.sum_eq_single a (fun b _ hb => h a b hb.symm) (by simp)
  exact hr.trans hl.symm

end Ring

section Exponential
variable [NormedRing R] [NormedAlgebra ℝ R] [CompleteSpace R]

theorem reducing_exponential (P : I → R) (hP : ∑ a, P a=1)
    (ho : ∀ b a, b≠a → P b*P a=0) (A : R)
    (h : ∀ b a, b≠a → P b*A*P a=0) (t : ℝ) (b a : I) (hba : b≠a) :
    P b*transfer A t*P a=0 := by
  rw [transfer_intertwining (P b) A A (generator_commutes P hP A h b) t,
    mul_assoc,ho b a hba,mul_zero]

theorem compressed_evolution (P : I → R) (hP : ∑ a, P a=1)
    (hi : ∀ a, P a*P a=P a) (A : R)
    (h : ∀ b a, b≠a → P b*A*P a=0) (t : ℝ) (a : I) :
    P a*transfer A t*P a=transfer (P a*A*P a) t*P a := by
  have hc := generator_commutes P hP A h a
  have he : P a*A=(P a*A*P a)*P a := by
    calc
      _ = A*(P a*P a) := by rw [hi, hc]
      _ = P a*A*P a := by rw [← mul_assoc,← hc]
      _ = _ := by rw [mul_assoc (P a*A),hi]
  rw [transfer_intertwining (P a) A (P a*A*P a) he t,mul_assoc,hi]

end Exponential
end KomorebiPaperVI.ReducingPackets
