/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIII.ReversibleConnections

/-!
# Gauge covariance of finite holonomy blocks

The reversible-connection module proves exact finite block reconstruction,
detection, and packet-supported witnesses.  This extension proves that a
gauge commuting with the packet projectors conjugates every block separately,
so the zero/nonzero pattern is preserved packet by packet.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.Transport.ReversibleConnection

universe u v w

variable {R : Type u} {X : Type v} {F : X → Type w}
variable [CommRing R] [∀ a, AddCommGroup (F a)] [∀ a, Module R (F a)]

/-- The additive triangle obstruction transforms by conjugation at its base. -/
theorem gauge_triangleObstruction
    (C : ReversibleConnection R X F) (G : Gauge (R := R) (F := F))
    (a b c : X) :
    (C.gauge G).triangleObstruction a b c =
      (G a).toLinearMap.comp
        ((C.triangleObstruction a b c).comp (G a).symm.toLinearMap) := by
  unfold triangleObstruction
  rw [C.gauge_triangleHolonomy]
  ext value
  simp only [LinearMap.sub_apply, LinearMap.id_apply, LinearMap.comp_apply,
    LinearEquiv.coe_toLinearMap, LinearEquiv.trans_apply, map_sub,
    LinearEquiv.apply_symm_apply]

end Komorebi.PaperIII.Transport.ReversibleConnection

namespace Komorebi.PaperIII.HolonomyBlocks

universe u v w

variable {R : Type u} {M : Type v} {I : Type w}
variable [CommRing R] [AddCommGroup M] [Module R M]

namespace PacketResolution

variable [Fintype I]
variable (P : PacketResolution R M I)

/-- Conjugation of an endomorphism by a linear equivalence. -/
def gaugeConjugate (gauge : M ≃ₗ[R] M) (map : M →ₗ[R] M) : M →ₗ[R] M :=
  gauge.toLinearMap.comp (map.comp gauge.symm.toLinearMap)

/-- A gauge is packet preserving when it commutes with every packet projector. -/
def PacketPreserving (gauge : M ≃ₗ[R] M) : Prop :=
  ∀ packet, gauge.toLinearMap.comp (P.projector packet) =
    (P.projector packet).comp gauge.toLinearMap

/-- The inverse of a packet-preserving gauge also commutes with every projector. -/
theorem symm_commutes_of_packetPreserving
    (gauge : M ≃ₗ[R] M) (hpreserves : P.PacketPreserving gauge) (packet : I) :
    gauge.symm.toLinearMap.comp (P.projector packet) =
      (P.projector packet).comp gauge.symm.toLinearMap := by
  ext value
  apply gauge.injective
  have hpoint := LinearMap.congr_fun (hpreserves packet) (gauge.symm value)
  simpa using hpoint.symm

/-- Packet-preserving conjugation acts on each input-output block separately. -/
theorem block_gauge_of_commutes
    (gauge : M ≃ₗ[R] M) (map : M →ₗ[R] M)
    (hpreserves : P.PacketPreserving gauge) (target source : I) :
    P.block (gaugeConjugate gauge map) target source =
      gaugeConjugate gauge (P.block map target source) := by
  ext value
  simp only [block, gaugeConjugate, LinearMap.comp_apply,
    LinearEquiv.coe_toLinearMap]
  have htarget (y : M) :
      P.projector target (gauge y) = gauge (P.projector target y) :=
    (LinearMap.congr_fun (hpreserves target) y).symm
  have hsource :
      gauge.symm (P.projector source value) =
        P.projector source (gauge.symm value) :=
    LinearMap.congr_fun
      (P.symm_commutes_of_packetPreserving gauge hpreserves source) value
  calc
    P.projector target
        (gauge (map (gauge.symm (P.projector source value)))) =
        gauge
          (P.projector target
            (map (gauge.symm (P.projector source value)))) :=
      htarget _
    _ = gauge
          (P.projector target
            (map (P.projector source (gauge.symm value)))) := by
      rw [hsource]

/-- Conjugation by a linear equivalence preserves whether a map is zero. -/
theorem gaugeConjugate_eq_zero_iff
    (gauge : M ≃ₗ[R] M) (map : M →ₗ[R] M) :
    gaugeConjugate gauge map = 0 ↔ map = 0 := by
  constructor
  · intro hzero
    ext value
    apply gauge.injective
    simpa [gaugeConjugate] using LinearMap.congr_fun hzero (gauge value)
  · rintro rfl
    simp [gaugeConjugate]

/-- Packet-preserving conjugation preserves the zero/nonzero status of each block. -/
theorem block_gauge_eq_zero_iff
    (gauge : M ≃ₗ[R] M) (map : M →ₗ[R] M)
    (hpreserves : P.PacketPreserving gauge) (target source : I) :
    P.block (gaugeConjugate gauge map) target source = 0 ↔
      P.block map target source = 0 := by
  rw [P.block_gauge_of_commutes gauge map hpreserves]
  exact gaugeConjugate_eq_zero_iff gauge _

end PacketResolution

universe x y

variable {Chart : Type x} {Fibre : Chart → Type y}
variable [∀ chart, AddCommGroup (Fibre chart)]
variable [∀ chart, Module R (Fibre chart)]

/--
For a packet-preserving gauge, each holonomy-obstruction block is conjugated
by the gauge at the base chart.
-/
theorem obstructionBlock_gauge_of_commutes
    (C : Transport.ReversibleConnection R Chart Fibre)
    (G : Transport.ReversibleConnection.Gauge (R := R) (F := Fibre))
    (a b c : Chart) {Packet : Type w} [Fintype Packet]
    (P : PacketResolution R (Fibre a) Packet)
    (hpreserves : P.PacketPreserving (G a)) (target source : Packet) :
    P.block ((C.gauge G).triangleObstruction a b c) target source =
      PacketResolution.gaugeConjugate (G a)
        (P.block (C.triangleObstruction a b c) target source) := by
  rw [C.gauge_triangleObstruction]
  exact P.block_gauge_of_commutes (G a)
    (C.triangleObstruction a b c) hpreserves target source

/-- Packet-preserving gauges preserve each obstruction block's zero status. -/
theorem obstructionBlock_gauge_eq_zero_iff
    (C : Transport.ReversibleConnection R Chart Fibre)
    (G : Transport.ReversibleConnection.Gauge (R := R) (F := Fibre))
    (a b c : Chart) {Packet : Type w} [Fintype Packet]
    (P : PacketResolution R (Fibre a) Packet)
    (hpreserves : P.PacketPreserving (G a)) (target source : Packet) :
    P.block ((C.gauge G).triangleObstruction a b c) target source = 0 ↔
      P.block (C.triangleObstruction a b c) target source = 0 := by
  rw [obstructionBlock_gauge_of_commutes C G a b c P hpreserves]
  exact PacketResolution.gaugeConjugate_eq_zero_iff (G a) _

end Komorebi.PaperIII.HolonomyBlocks
