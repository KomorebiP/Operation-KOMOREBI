import Komorebi.SufficientResolution.ChangingConsistency
import Komorebi.SufficientResolution.InexactToleranceCertificates

/-!
# Certificates based on an available, uncertain forward operator

The finite record contains only the available operator C, observed data and
allowances. Bounds against the unknown true A and its identifiable source are
separate mathematical premises. The code cannot infer those premises from a fit.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.OperatorCertificates

open OperatorUncertainty ChangingDiscrepancy ChangingConsistency
open DiscrepancyRule InexactDiscrepancy InexactToleranceCertificates
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

/-- All operational checks use C. The truth of its error allowance is not a field
that a fitting certificate can establish. -/
def Certified (C : G →L[ℝ] V) (v : V) (eta delta M tau kappa : ℝ) (x : G) : Prop :=
  (‖v‖ ≤ tau*effectiveNoise eta delta M ∧ ‖x‖ ≤ kappa) ∨
  Nonempty (PositiveCertificate C v (effectiveNoise eta delta M) tau kappa x)

 theorem certified_near (C : G →L[ℝ] V) (v : V) (eta delta M tau kappa : ℝ) (x : G)
    (hc : Certified C v eta delta M tau kappa x) :
    NearAccepted C v (effectiveNoise eta delta M) tau kappa x := by
  unfold Certified at hc
  rcases hc with hs | hp
  · exact small_data_certificate C v x (effectiveNoise eta delta M) tau kappa hs.1 hs.2
  · exact certificate_sound C v (effectiveNoise eta delta M) tau kappa x (Classical.choice hp)

 theorem certified_norm (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta M tau kappa : ℝ) (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M)
    (he : ‖A p-v‖ ≤ eta) (hc : Certified C v eta delta M tau kappa x) :
    ‖x‖ ≤ ‖p‖+kappa :=
  near_norm_control A C p x v eta delta M tau kappa hd hM he
    (certified_near C v eta delta M tau kappa x hc)

 theorem certified_true_residual (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta M tau kappa : ℝ) (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M)
    (he : ‖A p-v‖ ≤ eta) (hc : Certified C v eta delta M tau kappa x) :
    ‖A x-A p‖ ≤ ‖A‖*kappa+(tau+1)*effectiveNoise eta delta M :=
  ChangingDiscrepancy.near_true_residual A C p x v eta delta M tau kappa hd hM he
    (certified_near C v eta delta M tau kappa x hc)

 theorem certified_source_rate (A C : G →L[ℝ] V) (w v : V) (x : G)
    (eta delta M tau kappa : ℝ) (hd : ‖C-A‖ ≤ delta) (hM : ‖A.adjoint w‖ ≤ M)
    (he : ‖A (A.adjoint w)-v‖ ≤ eta) (hc : Certified C v eta delta M tau kappa x) :
    ‖x-A.adjoint w‖^2 ≤ 2*kappa^2+4*‖w‖*(tau+1)*effectiveNoise eta delta M :=
  near_source_condition_rate A C w x v eta delta M tau kappa hd hM he
    (certified_near C v eta delta M tau kappa x hc)

 theorem certified_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (eta delta kappa : ι → ℝ)
    (v : ι → V) (x : ι → G) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hc : ∀ i, Certified (C i) (v i) (eta i) (delta i) M tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) :=
  projected_consistent A f C eta delta kappa v x g M tau hM hd he
    (fun i => certified_near (C i) (v i) (eta i) (delta i) M tau (kappa i) (x i) (hc i))
    heta hdelta hkappa

 theorem certified_error_limit {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (eta delta kappa : ι → ℝ)
    (v : ι → V) (x : ι → G) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hc : ∀ i, Certified (C i) (v i) (eta i) (delta i) M tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => ‖x i-g‖) f (𝓝 ‖A.ker.starProjection g‖) :=
  source_error_limit A f C eta delta kappa v x g M tau hM hd he
    (fun i => certified_near (C i) (v i) (eta i) (delta i) M tau (kappa i) (x i) (hc i))
    heta hdelta hkappa

 theorem selected_source_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (eta delta : ι → ℝ) (v : ι → V) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (heff : ∀ i, 0 < effectiveNoise (eta i) (delta i) M) (htau : 1 < tau)
    (feasible : ∀ i, ∃ p : G, ‖C i p-v i‖ ≤ effectiveNoise (eta i) (delta i) M)
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => selectedSource (C i) (v i)
      (effectiveNoise (eta i) (delta i) M) tau (heff i) htau (feasible i))
      f (𝓝 (A.kerᗮ.starProjection g)) := by
  apply projected_consistent A f C eta delta (fun _ => 0) v _ g M tau hM hd he _
    heta hdelta tendsto_const_nhds
  intro i
  exact exact_is_near (C i) (v i) (effectiveNoise (eta i) (delta i) M) tau _
    (selectedSource_accepted (C i) (v i) (effectiveNoise (eta i) (delta i) M)
      tau (heff i) htau (feasible i))

omit [CompleteSpace V] in
 theorem inflated_feasibility (A C : G →L[ℝ] V) (g : G) (v : V)
    (eta delta M : ℝ) (hd : ‖C-A‖ ≤ delta)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M) (he : ‖A g-v‖ ≤ eta) :
    ∃ p : G, ‖C p-v‖ ≤ effectiveNoise eta delta M :=
  ⟨A.kerᗮ.starProjection g, projection_effective_noise A C g v eta delta M hd hM he⟩

 theorem selected_from_allowances_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (eta delta : ι → ℝ) (v : ι → V) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (heff : ∀ i, 0 < effectiveNoise (eta i) (delta i) M) (htau : 1 < tau)
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => selectedSource (C i) (v i)
      (effectiveNoise (eta i) (delta i) M) tau (heff i) htau
      (inflated_feasibility A (C i) g (v i) (eta i) (delta i) M (hd i) hM (he i)))
      f (𝓝 (A.kerᗮ.starProjection g)) :=
  selected_source_consistent f A C eta delta v g M tau hM hd he heff htau
    (fun i => inflated_feasibility A (C i) g (v i) (eta i) (delta i) M (hd i) hM (he i))
    heta hdelta

end Komorebi.SufficientResolution.OperatorCertificates
