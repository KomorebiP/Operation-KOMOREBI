module
public import ConjectureExamples
open KomorebiPaperIX
open NishibuchiCompletion GlobalEulerBoundary
set_option autoImplicit false
example (p m j : ℕ) [Fact p.Prime]
    (hmpos:0<m) (hj:j<m*p) (h:m∣p-1 ∨ m=2) :
    (∀ n, ((generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero)
      j (m*p*n):ℚ):ℚ_[p]) ∈ PadicInt.subring p) ∧
    ∀ r:ℕ, 0<r → ∃ n0:ℕ, 0<n0 ∧ n0≤r ∧ ∀ n:ℕ, n0≤n →
      precision p (r:ℤ)
        (generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j
          (m*p*n+Nat.lcm 2 (p-1)*p^r)-
         generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j (m*p*n)) :=
  conjecture_3_9 p m j hmpos hj h
#print KomorebiPaperIX.NishibuchiCompletion.conjecture_3_9
#print KomorebiPaperIX.DyadicFourCongruences.normalized_bound
#print axioms KomorebiPaperIX.NishibuchiCompletion.conjecture_3_9
#print axioms KomorebiPaperIX.DyadicFourCongruences.normalized_bound
