/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIII.MultilinearPacketJets
import KomorebiPaperIII.BoundedPacketJetNorm
import Mathlib.Analysis.Calculus.ContDiff.Defs

/-!
# Continuous jets on the actual packet ranges

The submodule ranges carry their inherited norms. Continuity of each projector
upgrades the previously constructed coordinate equivalence to a continuous
linear equivalence and makes the ranges closed. The range jet forgets literally
to the algebraic packet jet, has its own operator norm, and specializes to
mathlib's iterated Frechet derivative. No Taylor or composition formula is
assumed or asserted by that specialization.
-/

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Komorebi.PaperIII.PacketCoordinates
universe u v w x y
variable {K : Type u} [NontriviallyNormedField K]
variable {X : Type v} {Y : Type w}
variable [NormedAddCommGroup X] [NormedSpace K X]
variable [NormedAddCommGroup Y] [NormedSpace K Y]
variable {I : Type x} {J : Type y} [Fintype I] [Fintype J]

namespace System

/-- A bounded projector with the exact underlying algebraic map. -/
def continuousProjector (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) (i : I) : X →L[K] X :=
  ⟨P.projector i, hP i⟩

@[simp] theorem continuousProjector_apply (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) (i : I) (x : X) :
    P.continuousProjector hP i x = P.projector i x := rfl

/-- Every continuous projector has a closed range, identified with its fixed set. -/
theorem range_isClosed (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) (i : I) :
    IsClosed (LinearMap.range (P.projector i) : Set X) := by
  have hset : (LinearMap.range (P.projector i) : Set X) =
      {x : X | P.projector i x = x} := by
    ext x
    exact P.mem_range_iff_fixed i x
  rw [hset]
  exact isClosed_eq (hP i) continuous_id

/-- The actual finite packet coordinate equivalence is continuous in both directions. -/
def continuousCoordinateEquiv (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) : X ≃L[K] P.Coordinates :=
  { P.coordinateEquiv with
    continuous_toFun := continuous_pi (fun i => (hP i).subtype_mk _)
    continuous_invFun := by
      change Continuous (fun z : P.Coordinates => ∑ i, (z i : X))
      exact continuous_finsetSum _
        (fun i _ => continuous_subtype_val.comp (continuous_apply i)) }

@[simp] theorem continuousCoordinateEquiv_apply (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) (x : X) :
    P.continuousCoordinateEquiv hP x = P.analysis x := rfl

@[simp] theorem continuousCoordinateEquiv_symm_apply (P : System K X I)
    (hP : ∀ i, Continuous (P.projector i)) (z : P.Coordinates) :
    (P.continuousCoordinateEquiv hP).symm z = P.synthesis z := rfl

end System

variable {n : Nat}

/-- The continuous packet jet has the literal input ranges and output range. -/
def continuousPacketJet (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) :
    ContinuousMultilinearMap K
      (fun k : Fin n => LinearMap.range (P.projector (alpha k)))
      (LinearMap.range (Q.projector gamma)) :=
  ((Q.continuousProjector hQ gamma).compContinuousMultilinearMap
    (B.compContinuousLinearMap (fun k =>
      (LinearMap.range (P.projector (alpha k))).subtypeL))).codRestrict
    (LinearMap.range (Q.projector gamma))
    (by
      intro xs
      refine ⟨B (fun k => (xs k : X)), ?_⟩
      rfl)

@[simp] theorem continuousPacketJet_apply_coe
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I)
    (xs : (k : Fin n) → LinearMap.range (P.projector (alpha k))) :
    (continuousPacketJet P Q hQ B gamma alpha xs : Y) =
      Q.projector gamma (B (fun k => (xs k : X))) := rfl

/-- Forgetting continuity gives exactly the previously defined algebraic jet. -/
@[simp] theorem continuousPacketJet_toMultilinearMap
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) :
    (continuousPacketJet P Q hQ B gamma alpha).toMultilinearMap =
      packetJet P Q B.toMultilinearMap gamma alpha := rfl

/-- Restriction to the actual input ranges introduces no input projection factors. -/
theorem continuousPacketJet_norm_le
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (gamma : J) (alpha : Fin n → I) :
    ‖continuousPacketJet P Q hQ B gamma alpha‖ ≤
      ‖Q.continuousProjector hQ gamma‖ * ‖B‖ := by
  apply ContinuousMultilinearMap.opNorm_le_bound
    (mul_nonneg (norm_nonneg _) (norm_nonneg _))
  intro xs
  change ‖Q.continuousProjector hQ gamma (B (fun k => (xs k : X)))‖ ≤
    (‖Q.continuousProjector hQ gamma‖ * ‖B‖) * ∏ k, ‖xs k‖
  calc
    _ ≤ ‖Q.continuousProjector hQ gamma‖ *
        ‖B (fun k => (xs k : X))‖ :=
      (Q.continuousProjector hQ gamma).le_opNorm _
    _ ≤ ‖Q.continuousProjector hQ gamma‖ *
        (‖B‖ * ∏ k, ‖(xs k : X)‖) :=
      mul_le_mul_of_nonneg_left (B.le_opNorm _) (norm_nonneg _)
    _ = _ := by simp only [mul_assoc]; rfl

/-- Continuous range jets reconstruct the given continuous multilinear map. -/
theorem continuous_multilinear_packet_reconstruction
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j))
    (B : ContinuousMultilinearMap K (fun (_ : Fin n) => X) Y)
    (h : Fin n → X) :
    B h = ∑ gamma : J, ∑ alpha : Fin n → I,
      (continuousPacketJet P Q hQ B gamma alpha
        (fun k => P.analysis (h k) (alpha k)) : Y) :=
  multilinear_packet_reconstruction P Q B.toMultilinearMap h

/-- A packet jet of mathlib's actual chosen iterated Frechet derivative. -/
def iteratedPacketJet (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j)) (f : X → Y)
    (n : Nat) (x : X) (gamma : J) (alpha : Fin n → I) :=
  continuousPacketJet P Q hQ (iteratedFDeriv K n f x) gamma alpha

@[simp] theorem iteratedPacketJet_apply_coe
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j)) (f : X → Y)
    (n : Nat) (x : X) (gamma : J) (alpha : Fin n → I)
    (xs : (k : Fin n) → LinearMap.range (P.projector (alpha k))) :
    (iteratedPacketJet P Q hQ f n x gamma alpha xs : Y) =
      Q.projector gamma (iteratedFDeriv K n f x (fun k => (xs k : X))) := rfl

/-- Exact reconstruction of each chosen iterated Frechet derivative, including order zero.
This identity does not assert differentiability of an arbitrary supplied function. -/
theorem iteratedFDeriv_packet_reconstruction
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j)) (f : X → Y)
    (n : Nat) (x : X) (h : Fin n → X) :
    iteratedFDeriv K n f x h = ∑ gamma : J, ∑ alpha : Fin n → I,
      (iteratedPacketJet P Q hQ f n x gamma alpha
        (fun k => P.analysis (h k) (alpha k)) : Y) :=
  continuous_multilinear_packet_reconstruction P Q hQ (iteratedFDeriv K n f x) h

/-- The norm estimate applies to the actual iterated derivative range jet. -/
theorem iteratedPacketJet_norm_le
    (P : System K X I) (Q : System K Y J)
    (hQ : ∀ j, Continuous (Q.projector j)) (f : X → Y)
    (n : Nat) (x : X) (gamma : J) (alpha : Fin n → I) :
    ‖iteratedPacketJet P Q hQ f n x gamma alpha‖ ≤
      ‖Q.continuousProjector hQ gamma‖ * ‖iteratedFDeriv K n f x‖ :=
  continuousPacketJet_norm_le P Q hQ (iteratedFDeriv K n f x) gamma alpha

end Komorebi.PaperIII.PacketCoordinates
