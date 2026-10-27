/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.

SECTION 17 CANDIDATE. NOT COMPILED IN THIS CHECKPOINT.
This file is NOT imported by PaperIIIContinuation or counted in the accepted
Lean declaration census. Do not describe its statements as kernel checked.
-/
import KomorebiPaperIII.PacketCoordinates
import Mathlib.LinearAlgebra.Multilinear.Basic

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Komorebi.PaperIII.PacketCoordinates
universe u v w x y z
variable {R : Type u} [Semiring R]
variable {M : Type v} {N : Type w}
variable [AddCommMonoid M] [Module R M]
variable [AddCommMonoid N] [Module R N]
variable {I : Type x} {J : Type y} [Fintype I] [Fintype J]
variable {n : Nat}

/-- A finite resolution of the identity is already enough for the full
    multilinear expansion. Idempotence and pairwise annihilation are NOT used
    in this identity: they are needed later to make packet coordinates into
    an actual independent direct-sum representation. -/
theorem reconstruction_from_resolutions
    (Ps : I → M →ₗ[R] M) (Qs : J → N →ₗ[R] N)
    (hPs : ∑ i : I, Ps i = LinearMap.id)
    (hQs : ∑ j : J, Qs j = LinearMap.id)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (h : Fin n → M) :
    B h = ∑ gamma : J, ∑ alpha : Fin n → I,
      Qs gamma (B (fun k => Ps (alpha k) (h k))) := by
  classical
  have hslot (k : Fin n) : (∑ i : I, Ps i (h k)) = h k := by
    simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
      LinearMap.congr_fun hPs (h k)
  have hout : (∑ gamma : J, Qs gamma (B h)) = B h := by
    simpa only [LinearMap.sum_apply, LinearMap.id_apply] using
      LinearMap.congr_fun hQs (B h)
  have hinput : B h = ∑ alpha : Fin n → I,
      B (fun k => Ps (alpha k) (h k)) := by
    calc
      B h = B (fun k => ∑ i : I, Ps i (h k)) := by
        congr 1
        funext k
        exact (hslot k).symm
      _ = ∑ alpha : Fin n → I,
          B (fun k => Ps (alpha k) (h k)) := by
        exact B.map_sum (fun (k : Fin n) (i : I) => Ps i (h k))
  calc
    B h = ∑ gamma : J, Qs gamma (B h) := hout.symm
    _ = ∑ gamma : J,
          Qs gamma (∑ alpha : Fin n → I,
            B (fun k => Ps (alpha k) (h k))) := by rw [hinput]
    _ = ∑ gamma : J, ∑ alpha : Fin n → I,
          Qs gamma (B (fun k => Ps (alpha k) (h k))) := by
          simp only [map_sum]

/-- A labelled packet jet extended to the ambient slots; no range certificate
    and no pre-established coordinate equivalence is assumed. -/
def ambientJet (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (gamma : J) (alpha : Fin n → I) :
    MultilinearMap R (fun (_ : Fin n) => M) N :=
  (Q.projector gamma).compMultilinearMap
    (B.compLinearMap (fun k => P.projector (alpha k)))

@[simp] theorem ambientJet_apply (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (gamma : J) (alpha : Fin n → I) (h : Fin n → M) :
    ambientJet P Q B gamma alpha h =
      Q.projector gamma (B (fun k => P.projector (alpha k) (h k))) := rfl

/-- The manuscript's packet jet is literally defined on the actual input
    projector ranges and has the actual output projector range as codomain. -/
def packetJet (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (gamma : J) (alpha : Fin n → I) :
    MultilinearMap R
      (fun k : Fin n => LinearMap.range (P.projector (alpha k)))
      (LinearMap.range (Q.projector gamma)) :=
  ((Q.projector gamma).compMultilinearMap
    (B.compLinearMap (fun k =>
      (LinearMap.range (P.projector (alpha k))).subtype))).codRestrict
    (LinearMap.range (Q.projector gamma))
    (by
      intro xs
      refine ⟨B (fun k => (xs k : M)), ?_⟩
      rfl)

/-- Evaluate a genuine range-to-range block, then coerce its output to N. -/
@[simp] theorem packetJet_apply_coe (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (gamma : J) (alpha : Fin n → I)
    (xs : (k : Fin n) → LinearMap.range (P.projector (alpha k))) :
    (packetJet P Q B gamma alpha xs : N) =
      Q.projector gamma (B (fun k => (xs k : M))) := rfl

/-- Input reconstruction by expanding every argument using completeness;
    this also works when B is not symmetric and n = 0. -/
theorem multilinear_input_expansion (P : System R M I)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (h : Fin n → M) :
    B h = ∑ alpha : Fin n → I,
      B (fun k => P.projector (alpha k) (h k)) := by
  classical
  have hslot (k : Fin n) :
      (∑ i : I, P.projector i (h k)) = h k := by
    simpa only [P.synthesis_apply, P.analysis_apply] using
      P.synthesis_analysis (h k)
  calc
    B h = B (fun k => ∑ i : I, P.projector i (h k)) := by
      congr 1
      funext k
      exact (hslot k).symm
    _ = ∑ alpha : Fin n → I,
        B (fun k => P.projector (alpha k) (h k)) := by
      exact B.map_sum (fun (k : Fin n) (i : I) => P.projector i (h k))

/-- The input-output packet reconstruction identity, with no independent
    splitting certificate. In particular it applies to each continuous
    Frechet derivative, after forgetting continuity. -/
theorem multilinear_packet_reconstruction
    (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (h : Fin n → M) :
    B h = ∑ gamma : J, ∑ alpha : Fin n → I,
      (packetJet P Q B gamma alpha
        (fun k => P.analysis (h k) (alpha k)) : N) := by
  classical
  calc
    B h = ∑ gamma : J, ∑ alpha : Fin n → I,
      Q.projector gamma
        (B (fun k => P.projector (alpha k) (h k))) :=
      reconstruction_from_resolutions P.projector Q.projector
        P.complete Q.complete B h
    _ = ∑ gamma : J, ∑ alpha : Fin n → I,
      (packetJet P Q B gamma alpha
        (fun k => P.analysis (h k) (alpha k)) : N) := by
      simp only [packetJet_apply_coe, P.analysis_apply]

/-- On projected ambient vectors, the range jet and the ambient extension
    agree literally. This guards against accidentally dropping cross slots. -/
theorem packetJet_eq_ambientJet_on_analysis
    (P : System R M I) (Q : System R N J)
    (B : MultilinearMap R (fun (_ : Fin n) => M) N)
    (gamma : J) (alpha : Fin n → I) (h : Fin n → M) :
    (packetJet P Q B gamma alpha
      (fun k => P.analysis (h k) (alpha k)) : N) =
      ambientJet P Q B gamma alpha h := by
  simp only [packetJet_apply_coe, P.analysis_apply, ambientJet_apply]

end Komorebi.PaperIII.PacketCoordinates
