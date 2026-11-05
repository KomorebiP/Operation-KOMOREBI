/-
Copyright (c) 2026 Komorebi P.
Released under the MIT license.
Authors: Komorebi P.
-/
import KomorebiPaperIII.ContinuousPacketJets
import Mathlib.Analysis.InnerProductSpace.Projection.Basic

set_option autoImplicit false
noncomputable section
open scoped BigOperators
open Komorebi.PaperIII.PacketCoordinates

namespace Komorebi.PaperIII.JetNorm

universe u v w i j
variable {K : Type u} [NontriviallyNormedField K]
variable {X : Type v} {Y : Type w}
variable [NormedAddCommGroup X] [NormedSpace K X]
variable [NormedAddCommGroup Y] [NormedSpace K Y]
variable {I : Type i} {J : Type j} [Fintype I] [Fintype J] {n : ℕ}

/-- The product bound on the literal packet ranges, including zero projectors. -/
theorem continuousPacketJet_norm_le_prod
    (P : System K X I) (Q : System K Y J)
    (hP : ∀ a, Continuous (P.projector a))
    (hQ : ∀ b, Continuous (Q.projector b))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) :
    ‖continuousPacketJet P Q hQ B gamma alpha‖ ≤
      ‖Q.continuousProjector hQ gamma‖ * ‖B‖ *
        ∏ k, ‖P.continuousProjector hP (alpha k)‖ := by
  apply ContinuousMultilinearMap.opNorm_le_bound
    (mul_nonneg (mul_nonneg (norm_nonneg _) (norm_nonneg _))
      (Finset.prod_nonneg (fun k _ => norm_nonneg _)))
  intro xs
  have hfactor (k : Fin n) :
      ‖xs k‖ ≤ ‖P.continuousProjector hP (alpha k)‖ * ‖xs k‖ := by
    have h := (P.continuousProjector hP (alpha k)).le_opNorm (xs k : X)
    simpa only [System.continuousProjector_apply, System.projector_range_self,
      Submodule.norm_coe] using h
  have hprod : (∏ k, ‖xs k‖) ≤
      ∏ k, (‖P.continuousProjector hP (alpha k)‖ * ‖xs k‖) :=
    Finset.prod_le_prod (fun k _ => norm_nonneg _) (fun k _ => hfactor k)
  change ‖Q.continuousProjector hQ gamma (B (fun k => (xs k : X)))‖ ≤ _
  calc
    _ ≤ ‖Q.continuousProjector hQ gamma‖ * ‖B (fun k => (xs k : X))‖ :=
      (Q.continuousProjector hQ gamma).le_opNorm _
    _ ≤ ‖Q.continuousProjector hQ gamma‖ * (‖B‖ * ∏ k, ‖xs k‖) := by
      exact mul_le_mul_of_nonneg_left (B.le_opNorm _) (norm_nonneg _)
    _ ≤ ‖Q.continuousProjector hQ gamma‖ *
        (‖B‖ * ∏ k, (‖P.continuousProjector hP (alpha k)‖ * ‖xs k‖)) := by
      exact mul_le_mul_of_nonneg_left
        (mul_le_mul_of_nonneg_left hprod (norm_nonneg _)) (norm_nonneg _)
    _ = _ := by rw [Finset.prod_mul_distrib]; ring

/-- The same product bound for the existing iterated-derivative packet jet. -/
theorem iteratedPacketJet_norm_le_prod
    (P : System K X I) (Q : System K Y J)
    (hP : ∀ a, Continuous (P.projector a))
    (hQ : ∀ b, Continuous (Q.projector b))
    (f : X → Y) (x : X) (gamma : J) (alpha : Fin n → I) :
    ‖iteratedPacketJet P Q hQ f n x gamma alpha‖ ≤
      ‖Q.continuousProjector hQ gamma‖ * ‖iteratedFDeriv K n f x‖ *
        ∏ k, ‖P.continuousProjector hP (alpha k)‖ :=
  continuousPacketJet_norm_le_prod P Q hP hQ (iteratedFDeriv K n f x) gamma alpha

/-- A contractive output projector gives the sharp unit-factor estimate. -/
theorem continuousPacketJet_norm_le_of_contractive
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I)
    (hcontract : ‖Q.continuousProjector hQ gamma‖ ≤ 1) :
    ‖continuousPacketJet P Q hQ B gamma alpha‖ ≤ ‖B‖ := by
  calc
    _ ≤ ‖Q.continuousProjector hQ gamma‖ * ‖B‖ :=
      continuousPacketJet_norm_le P Q hQ B gamma alpha
    _ ≤ 1 * ‖B‖ := mul_le_mul_of_nonneg_right hcontract (norm_nonneg _)
    _ = _ := one_mul _

theorem iteratedPacketJet_norm_le_of_contractive
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (f : X → Y) (x : X) (gamma : J) (alpha : Fin n → I)
    (hcontract : ‖Q.continuousProjector hQ gamma‖ ≤ 1) :
    ‖iteratedPacketJet P Q hQ f n x gamma alpha‖ ≤ ‖iteratedFDeriv K n f x‖ :=
  continuousPacketJet_norm_le_of_contractive P Q hQ
    (iteratedFDeriv K n f x) gamma alpha hcontract

theorem continuousPacketJet_eq_zero_of_output_zero
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) (hzero : Q.projector gamma = 0) :
    continuousPacketJet P Q hQ B gamma alpha = 0 := by
  ext xs
  simp only [continuousPacketJet_apply_coe, hzero, LinearMap.zero_apply,
    zero_apply, Submodule.coe_zero]

theorem continuousPacketJet_eq_zero_of_input_zero
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) (k : Fin n)
    (hzero : P.projector (alpha k) = 0) :
    continuousPacketJet P Q hQ B gamma alpha = 0 := by
  apply ContinuousMultilinearMap.ext
  intro xs
  have hx : xs k = 0 := by
    apply Subtype.ext
    have h := P.projector_range_self (alpha k) (xs k)
    simpa only [hzero, LinearMap.zero_apply, Submodule.coe_zero] using h.symm
  exact (continuousPacketJet P Q hQ B gamma alpha).map_coord_zero k hx

section Hilbert
variable {𝕜 : Type*} [RCLike 𝕜]
variable {E : Type*} {F : Type*}
variable [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable [NormedAddCommGroup F] [InnerProductSpace 𝕜 F]

/-- An actual orthogonal output projection satisfies the Hilbert norm corollary. -/
theorem continuousPacketJet_norm_le_orthogonal
    (P : System 𝕜 E I) (Q : System 𝕜 F J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (B : ContinuousMultilinearMap 𝕜 (fun (_ : Fin n) => E) F)
    (gamma : J) (alpha : Fin n → I)
    (V : Submodule 𝕜 F) [V.HasOrthogonalProjection]
    (horth : Q.continuousProjector hQ gamma = V.starProjection) :
    ‖continuousPacketJet P Q hQ B gamma alpha‖ ≤ ‖B‖ := by
  apply continuousPacketJet_norm_le_of_contractive P Q hQ B gamma alpha
  rw [horth]
  exact V.starProjection_norm_le

theorem iteratedPacketJet_norm_le_orthogonal
    (P : System 𝕜 E I) (Q : System 𝕜 F J)
    (hQ : ∀ b, Continuous (Q.projector b))
    (f : E → F) (x : E) (gamma : J) (alpha : Fin n → I)
    (V : Submodule 𝕜 F) [V.HasOrthogonalProjection]
    (horth : Q.continuousProjector hQ gamma = V.starProjection) :
    ‖iteratedPacketJet P Q hQ f n x gamma alpha‖ ≤ ‖iteratedFDeriv 𝕜 n f x‖ :=
  continuousPacketJet_norm_le_orthogonal P Q hQ
    (iteratedFDeriv 𝕜 n f x) gamma alpha V horth

theorem continuousProjector_norm_eq_one_of_orthogonal
    (Q : System 𝕜 F J) (hQ : ∀ b, Continuous (Q.projector b))
    (gamma : J) (V : Submodule 𝕜 F) [V.HasOrthogonalProjection]
    (horth : Q.continuousProjector hQ gamma = V.starProjection) (hne : V ≠ ⊥) :
    ‖Q.continuousProjector hQ gamma‖ = 1 := by
  rw [horth]
  exact V.norm_starProjection hne

end Hilbert
end Komorebi.PaperIII.JetNorm
