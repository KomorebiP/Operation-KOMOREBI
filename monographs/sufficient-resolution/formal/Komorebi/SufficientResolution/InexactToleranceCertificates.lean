import Komorebi.SufficientResolution.InexactConsistency

/-!
# Squared finite certificates and allocation of discrepancy margins

Squared inequalities avoid numerical square roots. Their relation to the actual
Hilbert norms is proved, rather than substituting a new residual or a new metric.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.InexactToleranceCertificates

open TikhonovConstruction InexactResidual InexactDiscrepancy InexactConsistency
open Filter Topology

 theorem protected_window_iff (eta tau omega xi : ℝ) :
    eta+omega+xi ≤ tau*eta-omega-xi ↔ 2*(omega+xi) ≤ (tau-1)*eta := by
  constructor <;> intro h <;> nlinarith

 theorem protected_midpoint (eta tau omega xi : ℝ)
    (h : 2*(omega+xi) ≤ (tau-1)*eta) :
    eta+omega+xi ≤ ((tau+1)*eta)/2 ∧
      ((tau+1)*eta)/2 ≤ tau*eta-omega-xi := by
  constructor <;> nlinarith

 theorem protected_window_exists_iff (eta tau omega xi : ℝ) :
    (∃ measured : ℝ, eta+omega+xi ≤ measured ∧ measured ≤ tau*eta-omega-xi) ↔
      2*(omega+xi) ≤ (tau-1)*eta := by
  constructor
  · rintro ⟨m, hlo, hhi⟩
    exact (protected_window_iff eta tau omega xi).mp (hlo.trans hhi)
  · intro h
    exact ⟨_, protected_midpoint eta tau omega xi h⟩

 theorem relative_margins (eta tau omega xi measured c lo hi : ℝ)
    (he : 0 ≤ eta) (hb : omega+xi ≤ c*eta)
    (hl : 1+c ≤ lo) (hu : hi+c ≤ tau)
    (hml : lo*eta ≤ measured) (hmh : measured ≤ hi*eta) :
    eta+omega+xi ≤ measured ∧ measured ≤ tau*eta-omega-xi := by
  have hl' := mul_le_mul_of_nonneg_right hl he
  have hu' := mul_le_mul_of_nonneg_right hu he
  constructor <;> nlinarith

 theorem squared_enclosure_iff (d measured omega : ℝ)
    (hd : 0 ≤ d) (hm : 0 ≤ measured) (ho : 0 ≤ omega) :
    |measured-d| ≤ omega ↔
      (max 0 (measured-omega))^2 ≤ d^2 ∧ d^2 ≤ (measured+omega)^2 := by
  constructor
  · intro h
    obtain ⟨h1,h2⟩ := abs_le.mp h
    constructor
    · apply (sq_le_sq₀ (le_max_left _ _) hd).mpr
      exact max_le hd (by linarith)
    · apply (sq_le_sq₀ hd (add_nonneg hm ho)).mpr
      linarith
  · rintro ⟨hl,hu⟩
    have h1 : max 0 (measured-omega) ≤ d :=
      (sq_le_sq₀ (le_max_left _ _) hd).mp hl
    have h2 : d ≤ measured+omega :=
      (sq_le_sq₀ hd (add_nonneg hm ho)).mp hu
    have h3 := le_max_right 0 (measured-omega)
    apply abs_le.mpr
    constructor <;> linarith

 theorem squared_image_budget (lam rho xi : ℝ)
    (hl : 0 < lam) (hr : 0 ≤ rho) (hi : 0 ≤ xi)
    (hs : rho^2 ≤ 4*lam*xi^2) : rho ≤ 2*Real.sqrt lam*xi := by
  apply (sq_le_sq₀ hr (by positivity)).mp
  have he : (2*Real.sqrt lam*xi)^2 = 4*lam*xi^2 := by
    rw [mul_pow, mul_pow, Real.sq_sqrt hl.le]; ring
  rw [he]
  exact hs

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- A finite certificate whose scalar comparisons use only squares, products and order.
The true data-noise allowance is a separate assumption, not a field established here. -/
structure PositiveCertificate (v : V) (eta tau kappa : ℝ) (x : G) where
  lam : ℝ
  positive : 0 < lam
  rho : ℝ
  xi : ℝ
  measured : ℝ
  omega : ℝ
  rho_nonneg : 0 ≤ rho
  xi_nonneg : 0 ≤ xi
  kappa_nonneg : 0 ≤ kappa
  measured_nonneg : 0 ≤ measured
  omega_nonneg : 0 ≤ omega
  normal_squared : ‖normalResidual A lam v x‖^2 ≤ rho^2
  source_squared : rho^2 ≤ (lam*kappa)^2
  image_squared : rho^2 ≤ 4*lam*xi^2
  measured_lower_squared : (max 0 (measured-omega))^2 ≤ ‖A x-v‖^2
  measured_upper_squared : ‖A x-v‖^2 ≤ (measured+omega)^2
  protected_lower : eta+omega+xi ≤ measured
  protected_upper : measured ≤ tau*eta-omega-xi

 theorem certificate_sound (v : V) (eta tau kappa : ℝ) (x : G)
    (cert : PositiveCertificate A v eta tau kappa x) :
    NearAccepted A v eta tau kappa x := by
  have hn : ‖normalResidual A cert.lam v x‖ ≤ cert.rho :=
    (sq_le_sq₀ (norm_nonneg _) cert.rho_nonneg).mp cert.normal_squared
  have hs : cert.rho ≤ cert.lam*kappa :=
    (sq_le_sq₀ cert.rho_nonneg (mul_nonneg cert.positive.le cert.kappa_nonneg)).mp
      cert.source_squared
  have hi := squared_image_budget cert.lam cert.rho cert.xi cert.positive
    cert.rho_nonneg cert.xi_nonneg cert.image_squared
  have hm := (squared_enclosure_iff ‖A x-v‖ cert.measured cert.omega
    (norm_nonneg _) cert.measured_nonneg cert.omega_nonneg).mpr
      ⟨cert.measured_lower_squared, cert.measured_upper_squared⟩
  exact measured_certificate A cert.lam cert.positive v x eta tau kappa
    cert.measured cert.omega cert.xi (hn.trans hs) (hn.trans hi) hm
    cert.protected_lower cert.protected_upper

 theorem certificate_consistent {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (cert : ∀ i, PositiveCertificate A (v i) (eta i) tau (kappa i) (x i))
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) :=
  near_consistent A f eta kappa v x g tau hnoise
    (fun i => certificate_sound A (v i) (eta i) tau (kappa i) (x i) (cert i)) heta hkappa

 theorem certificate_error_limit {ι : Type*} (f : Filter ι)
    (eta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (cert : ∀ i, PositiveCertificate A (v i) (eta i) tau (kappa i) (x i))
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (heta : Tendsto eta f (𝓝 0)) (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => ‖x i-g‖) f (𝓝 ‖A.ker.starProjection g‖) :=
  near_error_norm_limit A f eta kappa v x g tau hnoise
    (fun i => certificate_sound A (v i) (eta i) tau (kappa i) (x i) (cert i)) heta hkappa

/-- An inexact evaluation of the normal residual can be enclosed separately. -/
 theorem normal_evaluation_envelope (lam : ℝ) (v : V) (x rhat : G)
    (nu rhohat : ℝ) (herr : ‖normalResidual A lam v x-rhat‖ ≤ nu)
    (hhat : ‖rhat‖ ≤ rhohat) : ‖normalResidual A lam v x‖ ≤ rhohat+nu := by
  calc
    _ ≤ ‖normalResidual A lam v x-rhat‖+‖rhat‖ := norm_le_norm_sub_add _ _
    _ ≤ nu+rhohat := add_le_add herr hhat
    _ = _ := add_comm _ _

 theorem uncertain_normal_certificate (lam : ℝ) (hl : 0 < lam) (v : V) (x rhat : G)
    (eta tau kappa measured omega xi nu rhohat : ℝ)
    (herr : ‖normalResidual A lam v x-rhat‖ ≤ nu) (hhat : ‖rhat‖ ≤ rhohat)
    (hs : rhohat+nu ≤ lam*kappa) (hi : rhohat+nu ≤ 2*Real.sqrt lam*xi)
    (hmeas : |measured-‖A x-v‖| ≤ omega)
    (hlo : eta+omega+xi ≤ measured) (hhi : measured ≤ tau*eta-omega-xi) :
    NearAccepted A v eta tau kappa x := by
  have h := normal_evaluation_envelope A lam v x rhat nu rhohat herr hhat
  exact measured_certificate A lam hl v x eta tau kappa measured omega xi
    (h.trans hs) (h.trans hi) hmeas hlo hhi

end Komorebi.SufficientResolution.InexactToleranceCertificates
