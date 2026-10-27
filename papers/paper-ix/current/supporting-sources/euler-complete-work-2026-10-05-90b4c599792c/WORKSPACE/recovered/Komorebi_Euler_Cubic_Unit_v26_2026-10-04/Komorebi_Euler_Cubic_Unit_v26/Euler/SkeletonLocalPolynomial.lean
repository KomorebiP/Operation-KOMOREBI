module
public import Euler.SkeletonArithmetic
public import Euler.PacketIntegerSlopes
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open Polynomial

/-- Each nonzero integer offset is split into its exact power of two and odd part. -/
def skeletonPlusFactor (k n : ℕ) : Polynomial D :=
  C (skeletonOddPart n:D)+C ((2:D)^(k-padicValNat 2 n))*X

def skeletonMinusFactor (k n : ℕ) : Polynomial D :=
  C (-(skeletonOddPart n:D))+C ((2:D)^(k-padicValNat 2 n))*X

lemma skeletonPlusFactor_scaled (k n : ℕ) (h : padicValNat 2 n≤k) :
    C ((2:D)^(padicValNat 2 n))*skeletonPlusFactor k n=
      C (n:D)+C ((2:D)^k)*X := by
  unfold skeletonPlusFactor
  rw [mul_add,← C_mul,← mul_assoc,← C_mul,← pow_add,Nat.add_sub_of_le h]
  have hh : (2:D)^(padicValNat 2 n)*(skeletonOddPart n:D)=(n:D) := by
    have hc := congrArg (fun t:ℕ => (t:D)) (skeletonOddPart_factor n)
    push_cast at hc
    simpa only [mul_comm] using hc
  rw [hh]

lemma skeletonMinusFactor_scaled (k n : ℕ) (h : padicValNat 2 n≤k) :
    C ((2:D)^(padicValNat 2 n))*skeletonMinusFactor k n=
      C (-(n:D))+C ((2:D)^k)*X := by
  unfold skeletonMinusFactor
  rw [mul_add,← C_mul,← mul_assoc,← C_mul,← pow_add,Nat.add_sub_of_le h]
  have hh : (2:D)^(padicValNat 2 n)*(skeletonOddPart n:D)=(n:D) := by
    have hc := congrArg (fun t:ℕ => (t:D)) (skeletonOddPart_factor n)
    push_cast at hc
    simpa only [mul_comm] using hc
  rw [mul_neg,hh]

lemma skeletonPlusFactor_red (k n : ℕ) (hn : 0<n) (hk : n<2^k) :
    (skeletonPlusFactor k n).map red=1 := by
  have hv := skeletonVal_lt_of_lt_pow n k hn hk
  have hz : red ((2:D)^(k-padicValNat 2 n))=0 := by
    simp [show k-padicValNat 2 n≠0 by omega]
  unfold skeletonPlusFactor
  rw [Polynomial.map_add,Polynomial.map_C,Polynomial.map_mul,Polynomial.map_C,
    Polynomial.map_X,skeletonOddPart_red n hn,hz,C_0,zero_mul,add_zero,C_1]

lemma skeletonMinusFactor_red (k n : ℕ) (hn : 0<n) (hk : n<2^k) :
    (skeletonMinusFactor k n).map red=1 := by
  have hv := skeletonVal_lt_of_lt_pow n k hn hk
  have hz : red ((2:D)^(k-padicValNat 2 n))=0 := by
    simp [show k-padicValNat 2 n≠0 by omega]
  unfold skeletonMinusFactor
  rw [Polynomial.map_add,Polynomial.map_C,Polynomial.map_mul,Polynomial.map_C,
    Polynomial.map_X,map_neg,skeletonOddPart_red n hn,hz,C_0,zero_mul,add_zero]
  rw [show (-1:F₂)=1 by decide,C_1]

/-- The odd companion of the paired factorial packet, in the local coordinate. -/
def skeletonOddCompanion (j i k : ℕ) : Polynomial D :=
  ∏ l ∈ Finset.range j,
    (C (2*(i:D)-((2*l+1:ℕ):D))+C ((2:D)^(k+1))*X)

/-- Constructed integral polynomial carrying every nonvanishing local factor. -/
def skeletonLocalUnit (j i k : ℕ) : Polynomial D :=
  (∏ n ∈ Finset.range i,skeletonPlusFactor k (n+1))*
  (∏ n ∈ Finset.range (j-1-i),skeletonMinusFactor k (n+1))*
  skeletonOddCompanion j i k

lemma skeletonOddCompanion_red (j i k : ℕ) :
    (skeletonOddCompanion j i k).map red=1 := by
  simp only [skeletonOddCompanion,Polynomial.map_prod]
  have hh (l:ℕ) :
      Polynomial.map red (C (2*(i:D)-((2*l+1:ℕ):D))+C ((2:D)^(k+1))*X)=1 := by
    simp only [Polynomial.map_add,Polynomial.map_C,Polynomial.map_mul,
      Polynomial.map_X,map_pow,eulerPacket_odd_factor_red]
    simp
  simp_rw [hh]
  simp

lemma skeletonLocalUnit_red (j i k : ℕ) (hi : i<2^k) (hj : j-1-i<2^k) :
    (skeletonLocalUnit j i k).map red=1 := by
  unfold skeletonLocalUnit
  rw [Polynomial.map_mul,Polynomial.map_mul,skeletonOddCompanion_red,
    Polynomial.map_prod,Polynomial.map_prod]
  have hp : (∏ n ∈ Finset.range i,Polynomial.map red (skeletonPlusFactor k (n+1)))=1 := by
    apply Finset.prod_eq_one
    intro n hn
    exact skeletonPlusFactor_red k (n+1) (by omega)
      (by have := Finset.mem_range.mp hn;omega)
  have hm : (∏ n ∈ Finset.range (j-1-i),Polynomial.map red (skeletonMinusFactor k (n+1)))=1 := by
    apply Finset.prod_eq_one
    intro n hn
    exact skeletonMinusFactor_red k (n+1) (by omega)
      (by have := Finset.mem_range.mp hn;omega)
  rw [hp,hm]
  simp

/-- Exact isolated-root factorization before powers of two are removed. -/
lemma finite_skeleton_split {R : Type*} [CommRing R] (j i : ℕ) (hi : i<j) (x : R) :
    (∏ l ∈ Finset.range j,(x-(l:R)))=
      (∏ n ∈ Finset.range i,(x-(i:R)+((n+1:ℕ):R)))*(x-(i:R))*
      (∏ n ∈ Finset.range (j-1-i),(x-(i:R)-((n+1:ℕ):R))) := by
  have hj : j=(i+1)+(j-1-i) := by omega
  calc
    _ = (∏ l ∈ Finset.range (i+1),(x-(l:R)))*
        (∏ n ∈ Finset.range (j-1-i),(x-((i+1+n:ℕ):R))) := by
      nth_rw 1 [hj]
      rw [Finset.prod_range_add]
    _ = (∏ l ∈ Finset.range i,(x-(l:R)))*(x-(i:R))*
        (∏ n ∈ Finset.range (j-1-i),(x-((i+1+n:ℕ):R))) := by
      rw [Finset.prod_range_succ]
    _ = _ := by
      have hleft : (∏ l ∈ Finset.range i,(x-(l:R)))=
          ∏ n ∈ Finset.range i,(x-(i:R)+((n+1:ℕ):R)) := by
        rw [← Finset.prod_range_reflect (fun l => x-(l:R)) i]
        apply Finset.prod_congr rfl
        intro n hn
        have hni : n < i := Finset.mem_range.mp hn
        rw [Nat.cast_sub (by omega),Nat.cast_sub (by omega)]
        push_cast
        ring
      rw [hleft]
      congr 1
      apply Finset.prod_congr rfl
      intro n _
      push_cast
      ring


lemma skeletonPlusProduct_eval (n k : ℕ) (hn : n<2^k) (y : D) :
    (∏ h ∈ Finset.range n,(((h+1:ℕ):D)+(2:D)^k*y))=
      (2:D)^(padicValNat 2 n.factorial)*
        (∏ h ∈ Finset.range n,(skeletonPlusFactor k (h+1)).eval y) := by
  have hh (h:ℕ) (hh: h∈Finset.range n) :
      ((h+1:ℕ):D)+(2:D)^k*y=
      (2:D)^(padicValNat 2 (h+1))*(skeletonPlusFactor k (h+1)).eval y := by
    have hv : padicValNat 2 (h+1)≤k := le_of_lt (skeletonVal_lt_of_lt_pow
      (h+1) k (by omega) (by have := Finset.mem_range.mp hh;omega))
    have he := congrArg (Polynomial.eval y) (skeletonPlusFactor_scaled k (h+1) hv)
    simpa only [Polynomial.eval_mul,Polynomial.eval_add,Polynomial.eval_C,Polynomial.eval_X] using he.symm
  rw [Finset.prod_congr rfl hh,Finset.prod_mul_distrib,Finset.prod_pow_eq_pow_sum,
    skeletonVal_factorial_sum]

lemma skeletonMinusProduct_eval (n k : ℕ) (hn : n<2^k) (y : D) :
    (∏ h ∈ Finset.range n,(-((h+1:ℕ):D)+(2:D)^k*y))=
      (2:D)^(padicValNat 2 n.factorial)*
        (∏ h ∈ Finset.range n,(skeletonMinusFactor k (h+1)).eval y) := by
  have hh (h:ℕ) (hh: h∈Finset.range n) :
      -((h+1:ℕ):D)+(2:D)^k*y=
      (2:D)^(padicValNat 2 (h+1))*(skeletonMinusFactor k (h+1)).eval y := by
    have hv : padicValNat 2 (h+1)≤k := le_of_lt (skeletonVal_lt_of_lt_pow
      (h+1) k (by omega) (by have := Finset.mem_range.mp hh;omega))
    have he := congrArg (Polynomial.eval y) (skeletonMinusFactor_scaled k (h+1) hv)
    simpa only [Polynomial.eval_mul,Polynomial.eval_add,Polynomial.eval_C,Polynomial.eval_X] using he.symm
  rw [Finset.prod_congr rfl hh,Finset.prod_mul_distrib,Finset.prod_pow_eq_pow_sum,
    skeletonVal_factorial_sum]

/-- Exact all-row local factorization of the original paired factorial packet. -/
theorem eulerPacket_local_factorization (j i k : ℕ) (hi : i < j)
    (hik : i<2^k) (hjk : j-1-i<2^k) (y : D) :
    (eulerPacket j).eval ((i:D)+(2:D)^k*y)=
      (2:D)^(k+skeletonSlope j i)*y*(skeletonLocalUnit j i k).eval y := by
  rw [eulerPacket_eval,Finset.prod_mul_distrib,finite_skeleton_split j i hi]
  have hp : (∏ n ∈ Finset.range i,
      (((i:D)+(2:D)^k*y)-(i:D)+((n+1:ℕ):D)))=
      ∏ n ∈ Finset.range i,(((n+1:ℕ):D)+(2:D)^k*y) := by
    apply Finset.prod_congr rfl
    intro n _
    ring
  have hm : (∏ n ∈ Finset.range (j-1-i),
      (((i:D)+(2:D)^k*y)-(i:D)-((n+1:ℕ):D)))=
      ∏ n ∈ Finset.range (j-1-i),(-((n+1:ℕ):D)+(2:D)^k*y) := by
    apply Finset.prod_congr rfl
    intro n _
    ring
  have ho : (∏ l ∈ Finset.range j,
      (2*((i:D)+(2:D)^k*y)-((2*l+1:ℕ):D)))=(skeletonOddCompanion j i k).eval y := by
    simp only [skeletonOddCompanion,Polynomial.eval_prod,Polynomial.eval_add,
      Polynomial.eval_mul,Polynomial.eval_C,Polynomial.eval_X]
    apply Finset.prod_congr rfl
    intro l _
    rw [pow_succ]
    ring
  rw [hp,hm,ho,skeletonPlusProduct_eval i k hik,skeletonMinusProduct_eval (j-1-i) k hjk]
  simp only [skeletonLocalUnit,Polynomial.eval_mul,Polynomial.eval_prod,skeletonSlope,pow_add]
  ring

/-- Canonical separating depth discharges every divisibility hypothesis. -/
theorem eulerPacket_canonical_factorization (j i : ℕ) (hi : i < j) (y : D) :
    (eulerPacket j).eval ((i:D)+(2:D)^(skeletonDepth j i)*y)=
      (2:D)^(skeletonContent j i)*y*
        (skeletonLocalUnit j i (skeletonDepth j i)).eval y :=
  eulerPacket_local_factorization j i (skeletonDepth j i) hi
    (skeletonDepth_bounds j i).1 (skeletonDepth_bounds j i).2 y

end Komorebi.Euler
