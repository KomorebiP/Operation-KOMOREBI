module
public import DyadicFourCongruences
public import Theorem75
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.NishibuchiCompletion
open Mahler GlobalEulerBoundary AllResidueEuler PowerSeries

/-- Literal degree-indexed coefficients of the unnormalized generalized Euler series. -/
def generalizedEuler (N:ℕ) (hN:N≠0) (j d:ℕ) : ℚ :=
  EGF.decode (unnormalizedSeries N hN j) d

theorem generalizedEuler_at_packet (N:ℕ) (hN:N≠0) (j n:ℕ) :
    generalizedEuler N hN j (N*n) = Congruential.unnormalized N j n :=
  decode_unnormalized N hN j n

/-- The series is connected to the author's defining reciprocal identity, not just named after it. -/
theorem original_generating_identity (N:ℕ) (hN:N≠0) (j:ℕ) (hj:j<N) :
    unnormalizedSeries N hN j * ExponentialSection.originalSection N j = X^j := by
  have H := ExponentialSection.original_section_inverse_identity N hN j hj
  have hfac : (j.factorial:ℚ)≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
  change C (j.factorial:ℚ) * ExponentialSection.expandedPacket N hN j * _ = _
  rw [mul_assoc,H]
  rw [←mul_assoc,←map_mul]
  have he : (j.factorial:ℚ)*(1/(j.factorial:ℚ))=1 := by field_simp
  rw [he,map_one,one_mul]

variable (p:ℕ) [Fact p.Prime]

/-- Conjecture 3.9 uses q=lcm(2,p-1), including its exceptional dyadic case. -/
def displacementFactor : ℕ := Nat.lcm 2 (p-1)

omit [Fact p.Prime] in
/-- On the divisor branch, the author's packet step is a multiple of the basic Fermat step. -/
theorem packet_step_factor (m:ℕ) (hm:m∣p-1) (hmpos:0<m) :
    displacementFactor p / m = (displacementFactor p / (p-1))*((p-1)/m) := by
  have hq : (p-1)*(displacementFactor p/(p-1))=displacementFactor p :=
    Nat.mul_div_cancel' (Nat.dvd_lcm_right 2 (p-1))
  have hm' : m*((p-1)/m)=p-1 := Nat.mul_div_cancel' hm
  calc
    displacementFactor p / m = ((p-1)*(displacementFactor p/(p-1)))/m := by rw [hq]
    _ = (m*((displacementFactor p/(p-1))*((p-1)/m)))/m := by
      apply congrArg (fun x:ℕ => x/m)
      calc
        _ = (m*((p-1)/m))*(displacementFactor p/(p-1)) := by rw [hm']
        _ = _ := by ring
    _ = _ := Nat.mul_div_right _ hmpos

/-- Explicit prime-power period on the divisor branch, using actual higher differences. -/
theorem divisor_period (m j r n:ℕ) (hm:m∣p-1) (hmpos:0<m) (hj:j<m*p)
    (hr:0<r) (hn:r≤m*n) :
    precision p (r:ℤ)
      (Congruential.unnormalized (m*p) j (n+p^(r-1)*(displacementFactor p/m))-
       Congruential.unnormalized (m*p) j n) := by
  let f := unnormalizedLift p m j hm hmpos hj
  have H := PeriodFromDifferences.prime_power_period p f (displacementFactor p/m) n r hr ?_
  · apply StandardWindowPrecision.rational_precision_of_divisibility p
      (f (n+p^(r-1)*(displacementFactor p/m))-f n)
    · simp only [f,PadicInt.coe_sub,unnormalizedLift_coe,Rat.cast_sub]
    · exact H
  · intro k
    rw [packet_step_factor p m hm hmpos]
    exact dvd_trans (pow_dvd_pow _ (min_le_min_left k hn))
      (global_unnormalized_bound p m j (displacementFactor p/(p-1)) k n hm hmpos hj)

/-- The only case outside m | p-1 allowed by the original conjecture is p=2,m=2. -/
theorem allowed_parameters (m:ℕ) (h:m∣p-1 ∨ m=2) : m∣p-1 ∨ (p=2 ∧ m=2) := by
  rcases h with hm|rfl
  · exact Or.inl hm
  · by_cases hp:p=2
    · exact Or.inr ⟨hp,rfl⟩
    · left
      have ho := (Fact.out:p.Prime).odd_of_ne_two hp
      obtain ⟨k,hk⟩ := ho
      use k
      omega

omit [Fact p.Prime] in
/-- All allowed parameters have the author's integral packet displacement. -/
theorem modulus_divides_displacement (m:ℕ) (h:m∣p-1 ∨ m=2) :
    m∣displacementFactor p := by
  rcases h with hm|rfl
  · exact dvd_trans hm (Nat.dvd_lcm_right 2 (p-1))
  · exact Nat.dvd_lcm_left 2 (p-1)

omit [Fact p.Prime] in
/-- The original conjecture's degree displacement is exactly the proved packet displacement. -/
theorem original_degree_shift (m n r:ℕ) (h:m∣p-1 ∨ m=2) (hr:0<r) :
    m*p*(n+p^(r-1)*(displacementFactor p/m)) =
      m*p*n+displacementFactor p*p^r := by
  have hq := Nat.mul_div_cancel' (modulus_divides_displacement p m h)
  have hp : p^r=p^(r-1)*p := by rw [←pow_succ,Nat.sub_add_cancel (by omega : 1≤r)]
  calc
    _ = m*p*n+(m*(displacementFactor p/m))*(p^(r-1)*p) := by ring
    _ = _ := by rw [hq,hp]

/-- Every coefficient in every parameter family allowed by Conjecture 3.9 is p-integral. -/
theorem full_integrality (m j n:ℕ) (hmpos:0<m) (hj:j<m*p) (h:m∣p-1 ∨ m=2) :
    ((Congruential.unnormalized (m*p) j n:ℚ):ℚ_[p]) ∈ PadicInt.subring p := by
  rcases allowed_parameters p m h with hm|⟨rfl,rfl⟩
  · exact unnormalized_integral p m j n hm hmpos hj
  · exact DyadicFourCongruences.unnormalized_integral j n hj

/-- The conjecture's actual lcm displacement, for all allowed primes and residues.
The explicit sufficient threshold is n>=r; no optimal-start or least-period claim. -/
theorem full_period_packet (m j r n:ℕ) (hmpos:0<m) (hj:j<m*p)
    (h:m∣p-1 ∨ m=2) (hr:0<r) (hn:r≤n) :
    precision p (r:ℤ)
      (Congruential.unnormalized (m*p) j (n+p^(r-1)*(displacementFactor p/m))-
       Congruential.unnormalized (m*p) j n) := by
  rcases allowed_parameters p m h with hm|⟨rfl,rfl⟩
  · apply divisor_period p m j r n hm hmpos hj hr
    exact le_trans hn (Nat.le_mul_of_pos_left n hmpos)
  · simpa [displacementFactor] using DyadicFourCongruences.dyadic_period_precision j r n hj hr hn

/-- Literal degree-indexed congruence in the original external formulation. -/
theorem full_period_degree (m j r n:ℕ) (hmpos:0<m) (hj:j<m*p)
    (h:m∣p-1 ∨ m=2) (hr:0<r) (hn:r≤n) :
    precision p (r:ℤ)
      (generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j
        (m*p*n+displacementFactor p*p^r)-
       generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j (m*p*n)) := by
  rw [←original_degree_shift p m n r h hr,generalizedEuler_at_packet,generalizedEuler_at_packet]
  exact full_period_packet p m j r n hmpos hj h hr hn

/-- Nishibuchi Conjecture 3.9: both integrality and eventual periodicity, with n0=r. -/
theorem conjecture_3_9 (m j:ℕ) (hmpos:0<m) (hj:j<m*p) (h:m∣p-1 ∨ m=2) :
    (∀n, ((generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero)
      j (m*p*n):ℚ):ℚ_[p]) ∈ PadicInt.subring p) ∧
    ∀r:ℕ, 0<r → ∃n0:ℕ, 0<n0 ∧ n0≤r ∧ ∀n:ℕ, n0≤n →
      precision p (r:ℤ)
        (generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j
          (m*p*n+displacementFactor p*p^r)-
         generalizedEuler (m*p) (Nat.mul_ne_zero hmpos.ne' (Fact.out:p.Prime).ne_zero) j (m*p*n)) := by
  constructor
  · intro n
    rw [generalizedEuler_at_packet]
    exact full_integrality p m j n hmpos hj h
  · intro r hr
    exact ⟨r,hr,le_rfl,fun n hn => full_period_degree p m j r n hmpos hj h hr hn⟩

end KomorebiPaperIX.NishibuchiCompletion
