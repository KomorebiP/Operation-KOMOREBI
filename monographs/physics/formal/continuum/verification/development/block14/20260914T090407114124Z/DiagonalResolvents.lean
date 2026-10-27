module
public import KomorebiPhysics.ResolventBounds
public import KomorebiPhysics.HarmonicSurrogates

/-! Genuine nonreal resolvents for every real diagonal sequence on its maximal
l2 domain. The certificate is constructed from multipliers, not postulated.
The earlier harmonic imaginary-axis construction remains unchanged. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DiagonalResolvents
open BoundedSpectral ResolventDomain
open scoped lp

variable (eig : ℕ → ℝ) (z : ℂ) (hz : z.im ≠ 0)

def denominator (n : ℕ) : ℂ := (eig n : ℂ) - z

theorem denominator_im (n : ℕ) : (denominator eig z n).im = -z.im := by
  simp [denominator]

include hz in
theorem denominator_ne_zero (n : ℕ) : denominator eig z n ≠ 0 := by
  intro h
  have hi := congrArg Complex.im h
  rw [denominator_im] at hi
  exact hz (neg_eq_zero.mp hi)

theorem denominator_lower (n : ℕ) : |z.im| ≤ ‖denominator eig z n‖ := by
  simpa only [denominator_im, abs_neg] using Complex.abs_im_le_norm (denominator eig z n)

include hz in
theorem inverse_bound (n : ℕ) : ‖(denominator eig z n)⁻¹‖ ≤ |z.im|⁻¹ := by
  rw [norm_inv]
  exact inv_anti₀ (abs_pos.mpr hz) (denominator_lower eig z n)

def symbol : Symbol := ofBound (fun n => (denominator eig z n)⁻¹) |z.im|⁻¹
  (inverse_bound eig z hz)

def resolvent : Space →L[ℂ] Space := diagonal (symbol eig z hz)

theorem resolvent_apply (x : Space) (n : ℕ) :
    resolvent eig z hz x n = (denominator eig z n)⁻¹ * x n := rfl

include hz in
theorem weighted_inverse (n : ℕ) :
    (eig n : ℂ) * (denominator eig z n)⁻¹ = 1 + z * (denominator eig z n)⁻¹ := by
  have hd := denominator_ne_zero eig z hz n
  unfold denominator at hd ⊢
  field_simp [hd]
  ring

/-- Weighted square summability is proved by x+z R_z x being a genuine l2 vector. -/
theorem range_mem (x : Space) : resolvent eig z hz x ∈ (DiagonalDomain.operator eig).domain := by
  change Memℓp (fun n => (eig n : ℂ) * resolvent eig z hz x n) 2
  have he : (fun n => (eig n : ℂ) * resolvent eig z hz x n) =
      (fun n => (x + z • resolvent eig z hz x) n) := by
    funext n
    change (eig n : ℂ) * ((denominator eig z n)⁻¹ * x n) =
      x n + z * ((denominator eig z n)⁻¹ * x n)
    rw [← mul_assoc, weighted_inverse eig z hz n]
    ring
  rw [he]
  exact lp.memℓp _

theorem right_inverse (x : Space) :
    shifted (DiagonalDomain.operator eig) z ⟨resolvent eig z hz x, range_mem eig z hz x⟩ = x := by
  apply lp.ext
  funext n
  change (eig n : ℂ) * ((denominator eig z n)⁻¹ * x n) -
    z * ((denominator eig z n)⁻¹ * x n) = x n
  rw [← sub_mul, ← mul_assoc]
  change denominator eig z n * (denominator eig z n)⁻¹ * x n = x n
  rw [mul_inv_cancel₀ (denominator_ne_zero eig z hz n), one_mul]

theorem left_inverse (x : (DiagonalDomain.operator eig).domain) :
    resolvent eig z hz (shifted (DiagonalDomain.operator eig) z x) = x := by
  apply lp.ext
  funext n
  change (denominator eig z n)⁻¹ * ((eig n : ℂ) * (x : Space) n - z * (x : Space) n) = (x : Space) n
  rw [← sub_mul, ← mul_assoc]
  change (denominator eig z n)⁻¹ * denominator eig z n * (x : Space) n = (x : Space) n
  rw [inv_mul_cancel₀ (denominator_ne_zero eig z hz n), one_mul]

def certificate : Certificate (DiagonalDomain.operator eig) z where
  op := resolvent eig z hz
  range_mem := range_mem eig z hz
  right_inverse := right_inverse eig z hz
  left_inverse := left_inverse eig z hz

theorem norm_bound : ‖resolvent eig z hz‖ ≤ |z.im|⁻¹ :=
  (certificate eig z hz).nonreal_norm_bound (DiagonalDomain.symmetric eig) hz

/-- The older positive-gap model also permits eta=0. No nonreal norm formula
is asserted at that zero parameter. -/
def harmonicCertificate (η : ℝ) :
    Certificate UnboundedExamples.harmonic ((η : ℂ) * Complex.I) where
  op := diagonal (HarmonicSurrogates.resolventSymbol η)
  range_mem := HarmonicSurrogates.resolvent_mem_domain η
  right_inverse := HarmonicSurrogates.resolvent_right_inverse η
  left_inverse := HarmonicSurrogates.resolvent_left_inverse η

theorem harmonic_agrees (η : ℝ) (hη : η ≠ 0) :
    resolvent UnboundedExamples.harmonicEigenvalue ((η : ℂ) * Complex.I)
      (by simpa using hη) = (harmonicCertificate η).op :=
  (certificate UnboundedExamples.harmonicEigenvalue ((η : ℂ) * Complex.I)
      (by simpa using hη)).unique (harmonicCertificate η)

theorem packet_commutator {P : Space →L[ℂ] Space}
    (B : BoundedCommutator (DiagonalDomain.operator eig) P) :
    commutator (resolvent eig z hz) P =
      -(resolvent eig z hz * B.bound * resolvent eig z hz) :=
  (certificate eig z hz).commutator_identity B

theorem packet_norm_bound {P : Space →L[ℂ] Space}
    (B : BoundedCommutator (DiagonalDomain.operator eig) P) :
    ‖commutator (resolvent eig z hz) P‖ ≤ ‖B.bound‖ / z.im ^ 2 :=
  (certificate eig z hz).nonreal_commutator_bound B (DiagonalDomain.symmetric eig) hz

end DiagonalResolvents
end KomorebiPhysics
