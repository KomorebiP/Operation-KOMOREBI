module
public import Euler.SourceRows
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open Polynomial

/-- The actual paired factorial-lane polynomial used by the Euler row residual. -/
def eulerPacket (q : ℕ) : Polynomial D :=
  ∏ i ∈ Finset.range q, (X-C (i:D))*(C (2:D)*X-C ((2*i+1:ℕ):D))

@[simp] lemma eulerPacket_zero : eulerPacket 0=1 := by simp [eulerPacket]

lemma eulerPacket_succ (q : ℕ) :
    eulerPacket (q+1)=eulerPacket q*(X-C (q:D))*(C (2:D)*X-C ((2*q+1:ℕ):D)) := by
  rw [eulerPacket,Finset.prod_range_succ]
  exact (mul_assoc _ _ _).symm

lemma eulerPacket_eval (q : ℕ) (x : D) :
    (eulerPacket q).eval x=
      ∏ i ∈ Finset.range q, (x-(i:D))*(2*x-((2*i+1:ℕ):D)) := by
  simp only [eulerPacket,eval_prod,eval_mul,eval_sub,eval_X,eval_C]

/-- Exact packet multiplication under a shifted row coordinate. -/
theorem eulerPacket_block (a b : ℕ) (x : D) :
    (eulerPacket (a+b)).eval x=(eulerPacket a).eval x*(eulerPacket b).eval (x-(a:D)) := by
  rw [eulerPacket_eval,Finset.prod_range_add,eulerPacket_eval,eulerPacket_eval]
  congr 1
  apply Finset.prod_congr rfl
  intro i _
  push_cast
  ring

/-- A finite row kills every packet beyond its nonnegative offset. -/
theorem eulerPacket_eval_nat_zero (q n : ℕ) (h : n<q) :
    (eulerPacket q).eval (n:D)=0 := by
  rw [eulerPacket_eval]
  apply Finset.prod_eq_zero (Finset.mem_range.mpr h)
  simp

/-- Pairing even and odd factorial lanes gives the exact packet normalization. -/
theorem eulerPacket_desc_factorial (q : ℕ) (x : D) :
    (descPochhammer D (2*q)).eval (2*x)=(2:D)^q*(eulerPacket q).eval x := by
  induction q with
  | zero => simp [descPochhammer_zero]
  | succ q ih =>
    rw [show 2*(q+1)=2*q+1+1 by omega,descPochhammer_succ_right,
      descPochhammer_succ_right,eulerPacket_succ]
    simp only [eval_mul,eval_sub,eval_X,eval_C,eval_natCast]
    rw [ih,pow_succ]
    push_cast
    ring

/-- Finite original-offset sums are unchanged by adjoining vanishing packets. -/
theorem eulerPacket_finite_support (n Q : ℕ) (hQ : n<Q) (w : ℕ → D) :
    (∑ q ∈ Finset.range Q, w q*(eulerPacket q).eval (n:D)) =
      ∑ q ∈ Finset.range (n+1), w q*(eulerPacket q).eval (n:D) := by
  symm
  apply Finset.sum_subset (Finset.range_mono (by omega))
  intro q _ hq
  have hn : n+1≤q := by simpa only [Finset.mem_range,not_lt] using hq
  have h : n<q := by omega
  rw [eulerPacket_eval_nat_zero q n h,mul_zero]

/-- Denominator-cleared Euler source sequence, the actual object annihilated by three taps. -/
def weightedSourceRow (n : ℕ) : D :=
  ((n:D)+1)*(2*(n:D)+1)*reval eulerSource (n:D)

lemma weightedSourceRow_identity (n : ℕ) :
    8*weightedSourceRow n=(9:D)^(n+1)-1 := by
  simpa only [weightedSourceRow,← mul_assoc] using eulerSource_integer_identity n

/-- The exact three-tap annihilator of the actual weighted source is (xi-1)(xi-9). -/
theorem weightedSourceRow_three_taps (n : ℕ) :
    weightedSourceRow (n+2)-10*weightedSourceRow (n+1)+9*weightedSourceRow n=0 := by
  have h0:=weightedSourceRow_identity n
  have h1:=weightedSourceRow_identity (n+1)
  have h2:=weightedSourceRow_identity (n+2)
  have hpow1 : (9:D)^(n+1+1)=(9:D)^(n+1)*9 := pow_succ _ _
  have hpow2 : (9:D)^(n+2+1)=(9:D)^(n+1)*9*9 := by
    rw [show n+2+1=(n+1+1)+1 by omega,pow_succ,pow_succ]
  rw [hpow1] at h1
  rw [hpow2] at h2
  apply mul_left_cancel₀ (show (8:D)≠0 by norm_num)
  linear_combination h2-10*h1+9*h0

end Komorebi.Euler
