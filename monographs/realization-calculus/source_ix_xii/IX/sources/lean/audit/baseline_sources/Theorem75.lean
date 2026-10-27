module
public import AllResidueEuler
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.Theorem75
open AllResidueEuler GlobalEulerBoundary Mahler
variable (p : ℕ) [Fact p.Prime]

/-- Paper IX, Theorem 7.5, for the literal original rational coefficient functions.
The first conjunct asserts integrality of j! C_(mp,j)(n). The second is the all-residue
saturated higher-difference estimate. The third is the corrected normalized estimate.
Zero differences are included through the definition of precision. The result is valid
for every prime and every natural step multiplier, hence in particular for the paper's
odd primes and positive multipliers. No weighted or Dwork hypothesis is assumed. -/
theorem global_finite_difference (m j u k n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) :
    (((Congruential.unnormalized (m*p) j n : ℚ):ℚ_[p]) ∈ PadicInt.subring p) ∧
    precision p ((min k (m*n):ℕ):ℤ)
      (difference (u*((p-1)/m)) k (Congruential.unnormalized (m*p) j) n) ∧
    precision p (((min k (m*n):ℕ):ℤ)-(padicValNat p j.factorial:ℤ))
      (difference (u*((p-1)/m)) k (Congruential.coeff (m*p) j) n) :=
  ⟨unnormalized_integral p m j n hm hmpos hj,
    global_unnormalized_precision p m j u k n hm hmpos hj,
    global_normalized_precision p m j u k n hm hmpos hj⟩

/-- The classical sufficient threshold is an actual all-row consequence, not a finite test. -/
theorem precision_at_threshold (m j u r n : ℕ)
    (hm : m∣p-1) (hmpos : 0<m) (hj : j<m*p) (hn : r≤m*n) :
    precision p (r:ℤ)
      (difference (u*((p-1)/m)) r (Congruential.unnormalized (m*p) j) n) := by
  simpa only [min_eq_left hn] using
    global_unnormalized_precision p m j u r n hm hmpos hj

end KomorebiPaperIX.Theorem75
