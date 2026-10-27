import KomorebiPaperVI.Algebra

/-! Author: Komorebi P. All pairwise difference identities for a nested projector tower. -/
namespace KomorebiPaperVI.MartingalePackets
open scoped BigOperators
variable {R : Type*} [Ring R]

def packet (P : ℕ → R) : ℕ → R
  | 0 => P 0
  | n+1 => P (n+1)-P n

theorem packet_product (P : ℕ → R) (h : ∀ i j, P i*P j=P (min i j)) (i j : ℕ) :
    packet P i*packet P j=if i=j then packet P j else 0 := by
  cases i with
  | zero =>
    cases j with
    | zero => simp [packet,h]
    | succ j => simp [packet,mul_sub,h]
  | succ i =>
    cases j with
    | zero => simp [packet,sub_mul,h]
    | succ j =>
      by_cases hij : i=j
      · subst j
        simp only [packet,sub_mul,mul_sub,h,Nat.min_self,ite_true,
          Nat.min_eq_left (Nat.le_succ i),Nat.min_eq_right (Nat.le_succ i)]
        abel
      · rcases lt_or_gt_of_ne hij with hij' | hji'
        · have h1 : i+1 ≤ j := hij'
          have h2 : i+1 ≤ j+1 := by omega
          have h3 : i ≤ j+1 := by omega
          simp [packet,sub_mul,mul_sub,h,Nat.min_eq_left h1,Nat.min_eq_left h2,
            Nat.min_eq_left h3,Nat.min_eq_left hij'.le,hij]
        · have h1 : j+1 ≤ i := hji'
          have h2 : j+1 ≤ i+1 := by omega
          have h3 : j ≤ i+1 := by omega
          simp [packet,sub_mul,mul_sub,h,Nat.min_eq_right h1,Nat.min_eq_right h2,
            Nat.min_eq_right h3,Nat.min_eq_right hji'.le,hij]

theorem packet_sum (P : ℕ → R) (n : ℕ) : ∑ j ∈ Finset.range (n+1), packet P j=P n := by
  induction n with
  | zero => simp [packet]
  | succ n ih => rw [Finset.sum_range_succ,ih,packet]; abel

end KomorebiPaperVI.MartingalePackets
