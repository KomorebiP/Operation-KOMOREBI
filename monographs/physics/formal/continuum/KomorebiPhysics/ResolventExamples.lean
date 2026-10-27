module
public import KomorebiPhysics.NonreducingPacket
public import KomorebiPhysics.ResolventParameters

/-! Exact nonzero certificates in an infinite-dimensional model whose
Hamiltonian is already proved self-adjoint and unbounded. No finite cutoff
or floating-point test supplies any assertion in this module. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResolventExamples
open BoundedSpectral ResolventDomain NonreducingPacket UnboundedExamples
open HarmonicSurrogates DiagonalResolvents
open scoped lp

/-- The actual infinite-space harmonic resolvent. -/
def R (η : ℝ) : Space →L[ℂ] Space := (harmonicCertificate η).op

def P : Space →L[ℂ] Space := packet harmonicEigenvalue

def B : Space →L[ℂ] Space := generatorCommutator harmonicEigenvalue

theorem P_idempotent (x : Space) : P (P x) = P x := packet_idempotent harmonicEigenvalue x

theorem P_selfAdjoint (x y : Space) : inner ℂ (P x) y = inner ℂ x (P y) :=
  packet_selfAdjoint harmonicEigenvalue x y

theorem P_domain (x : harmonic.domain) : P x ∈ harmonic.domain :=
  packet_preserves harmonicEigenvalue x

theorem B_norm : ‖B‖ = 12/25 := by
  rw [B, generatorCommutator_norm]
  norm_num [harmonicEigenvalue]

theorem B_on_basis : B (lp.single 2 1 1) = (-12/25 : ℂ) • lp.single 2 0 1 := by
  change (((12/25 : ℂ) * ((harmonicEigenvalue 0 : ℂ) - harmonicEigenvalue 1)) • planeSkew)
    (lp.single 2 1 1) = _
  rw [smul_apply, planeSkew_single_one]
  norm_num [harmonicEigenvalue]

theorem B_ne_zero : B ≠ 0 := by
  intro h
  have hn := B_norm
  rw [h, norm_zero] at hn
  norm_num at hn

theorem exact_resolvent_certificate (η : ℝ) : commutator (R η) P = -(R η * B * R η) :=
  (harmonicCertificate η).commutator_identity (boundedCommutator harmonicEigenvalue)

theorem resolvent_certificate_bound (η : ℝ) :
    ‖commutator (R η) P‖ ≤ ‖R η‖ ^ 2 * (12/25) := by
  have h := (harmonicCertificate η).commutator_norm_bound (boundedCommutator harmonicEigenvalue)
  change ‖commutator (R η) P‖ ≤ ‖R η‖ ^ 2 * ‖B‖ at h
  simpa only [B_norm] using h

theorem nonreal_bound (η : ℝ) (hη : η ≠ 0) :
    ‖commutator (R η) P‖ ≤ (12/25) / η ^ 2 := by
  have h := imaginary_axis_commutator_bound η hη (harmonicCertificate η)
    (boundedCommutator harmonicEigenvalue) (DiagonalDomain.symmetric harmonicEigenvalue)
  change ‖commutator (R η) P‖ ≤ ‖B‖ / η ^ 2 at h
  simpa only [B_norm] using h

/-- The positive harmonic gap is exactly one between the two mixed modes. -/
theorem reciprocal_gap (η : ℝ) :
    resolventSymbol η 0 - resolventSymbol η 1 =
      (HarmonicSurrogates.denominator η 0 * HarmonicSurrogates.denominator η 1)⁻¹ := by
  rw [resolventSymbol_apply, resolventSymbol_apply]
  have h0 := HarmonicSurrogates.denominator_ne_zero η 0
  have h1 := HarmonicSurrogates.denominator_ne_zero η 1
  field_simp
  norm_num [HarmonicSurrogates.denominator, harmonicEigenvalue]

/-- This is an exact operator norm, for every real eta, not only an upper bound. -/
theorem exact_norm (η : ℝ) :
    ‖commutator (R η) P‖ = (12/25 : ℝ) /
      (Real.sqrt ((1/4 : ℝ) + η ^ 2) * Real.sqrt ((9/4 : ℝ) + η ^ 2)) := by
  change ‖commutator (diagonal (resolventSymbol η)) (packet harmonicEigenvalue)‖ = _
  rw [diagonal_commutator_norm, reciprocal_gap, norm_inv, norm_mul,
    HarmonicSurrogates.denominator_norm, HarmonicSurrogates.denominator_norm]
  norm_num [harmonicEigenvalue, div_eq_mul_inv]

theorem zero_parameter_norm : ‖commutator (R 0) P‖ = 16/25 := by
  change ‖commutator (diagonal (resolventSymbol 0)) (packet harmonicEigenvalue)‖ = _
  rw [diagonal_commutator_norm]
  norm_num [resolventSymbol_apply, HarmonicSurrogates.denominator, harmonicEigenvalue]

theorem zero_parameter_on_basis :
    commutator (R 0) P (lp.single 2 1 1) = (16/25 : ℂ) • lp.single 2 0 1 := by
  change commutator (diagonal (resolventSymbol 0)) (packet harmonicEigenvalue) _ = _
  rw [diagonal_commutator, smul_apply, planeSkew_single_one]
  norm_num [resolventSymbol_apply, HarmonicSurrogates.denominator, harmonicEigenvalue]

theorem packet_does_not_reduce :
    ¬ ∀ x : harmonic.domain, harmonic (restrict harmonic P P_domain x) = P (harmonic x) := by
  intro h
  have hc := (harmonicCertificate 0).commutator_zero_of_action_commutes P_domain h
  have hn := zero_parameter_norm
  change commutator (R 0) P = 0 at hc
  rw [hc, norm_zero] at hn
  norm_num at hn

theorem resolvent_commutator_nonzero (η : ℝ) : commutator (R η) P ≠ 0 := by
  intro h
  have hp := (harmonicCertificate η).action_commutes_of_commutator_zero h
  exact packet_does_not_reduce hp

/-- The sign of the negative R B R product is detected on a nonzero basis vector. -/
theorem wrong_sign_rejected : commutator (R 0) P ≠ R 0 * B * R 0 := by
  intro h
  have hh := exact_resolvent_certificate 0
  rw [← h] at hh
  have hz : commutator (R 0) P = 0 := by
    have ha : (2 : ℂ) • commutator (R 0) P = 0 := by
      rw [two_smul]
      exact eq_neg_iff_add_eq_zero.mp hh
    exact (smul_eq_zero.mp ha).resolve_left (by norm_num)
  exact resolvent_commutator_nonzero 0 hz

/-- Dropping eta != 0 would turn the source bound into a false zero bound. -/
theorem zero_parameter_bound_rejected :
    ¬ ‖commutator (R 0) P‖ ≤ ‖B‖ / (0 : ℝ) ^ 2 := by
  rw [zero_parameter_norm]
  norm_num

/-- Both resolvent factors are required by the certificate. -/
theorem omitted_factor_rejected : commutator (R 0) P ≠ -(R 0 * B) := by
  intro h
  have hh := congrArg (fun A : Space →L[ℂ] Space => (A (lp.single 2 1 1)) 0) h
  rw [zero_parameter_on_basis] at hh
  change ((16/25 : ℂ) * 1) = -(R 0 (B (lp.single 2 1 1)) 0) at hh
  rw [B_on_basis, map_smul] at hh
  change ((16/25 : ℂ) * 1) = -((-12/25 : ℂ) * (diagonal (resolventSymbol 0) (lp.single 2 0 1) 0)) at hh
  norm_num [diagonal_apply, resolventSymbol_apply, HarmonicSurrogates.denominator, harmonicEigenvalue] at hh


/-- A nonreal parameter witness, with an exact complex output. -/
theorem unit_parameter_on_basis :
    commutator (R 1) P (lp.single 2 1 1) =
      ((-48/1625 : ℂ) + (384/1625) * Complex.I) • lp.single 2 0 1 := by
  change commutator (diagonal (resolventSymbol 1)) (packet harmonicEigenvalue) _ = _
  rw [diagonal_commutator, smul_apply, planeSkew_single_one]
  congr 1
  apply Complex.ext <;>
    norm_num [resolventSymbol_apply, HarmonicSurrogates.denominator, harmonicEigenvalue,
      Complex.inv_def, Complex.normSq_apply, Complex.mul_re, Complex.mul_im, map_ofNat, map_div₀]

/-- The infinite-space operator norm has a rational squared value at eta=1. -/
theorem unit_parameter_norm_sq : ‖commutator (R 1) P‖ ^ 2 = 2304/40625 := by
  rw [exact_norm, div_pow, mul_pow,
    Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 1/4 + 1^2),
    Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 9/4 + 1^2)]
  norm_num

/-- The true nonreal bound holds for the same nonzero packet. -/
theorem unit_parameter_bound : ‖commutator (R 1) P‖ ≤ 12/25 := by
  simpa using nonreal_bound 1 (by norm_num)

end ResolventExamples
end KomorebiPhysics
