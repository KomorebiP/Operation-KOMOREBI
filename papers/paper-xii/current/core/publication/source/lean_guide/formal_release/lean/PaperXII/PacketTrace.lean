import Mathlib.LinearAlgebra.Trace
import Mathlib.LinearAlgebra.Dimension.LinearMap

set_option autoImplicit false

/-! Paper XII, Corollary 8.4. The projector is the actual action of a supplied
idempotent of the Hecke algebra, and the packet is its actual image submodule.
This block does not construct the canonical Artin idempotents (Fact 8.1), nor
prove the localization/direct-sum comparisons in Theorem 8.2. Its conclusions
apply to every supplied idempotent, in particular to those canonical inputs.
No semisimplicity or faithful action is assumed. -/
namespace PaperXII.PacketTrace

variable {E T V : Type*} [Field E] [CommRing T] [Algebra E T]
    [AddCommGroup V] [Module E V] [Module T V] [IsScalarTower E T V]

/-- The actual E-linear action of the Hecke element. -/
def projector (e : T) : V →ₗ[E] V := Algebra.lsmul E E V e

/-- The packet eV, as a submodule of the original representation space. -/
def packet (e : T) : Submodule E V := LinearMap.range (projector (V := V) e)

theorem projector_apply (e : T) (v : V) : projector (E := E) e v = e • v := rfl

theorem projector_idempotent {e : T} (he : IsIdempotentElem e) :
    IsIdempotentElem (projector (E := E) (V := V) e) := by
  change projector e * projector e = projector e
  ext v
  change e • (e • v) = e • v
  rw [← mul_smul, he]

theorem mem_packet_iff (e : T) (v : V) :
    v ∈ packet (E := E) e ↔ ∃ w : V, e • w = v := Iff.rfl

/-- An element lies in eV exactly when e fixes it. -/
theorem mem_packet_iff_fixed {e : T} (he : IsIdempotentElem e) (v : V) :
    v ∈ packet (E := E) e ↔ e • v = v := by
  rw [mem_packet_iff]
  constructor
  · rintro ⟨w, rfl⟩
    rw [← mul_smul, he]
  · intro hv
    exact ⟨v, hv⟩

variable [FiniteDimensional E V]

/-- Operator rank is the natural image dimension, with its cardinal cast. -/
theorem rank_eq_dimension (e : T) :
    LinearMap.rank (projector (E := E) (V := V) e) =
      (Module.finrank E (packet (E := E) (V := V) e) : Cardinal) := by
  exact (Module.finrank_eq_rank (R := E) (M := packet (E := E) (V := V) e)).symm

/-- The trace formula includes the necessary cast from natural dimension to E.
The equality itself holds in every characteristic. -/
theorem trace_eq_cast_finrank {e : T} (he : IsIdempotentElem e) :
    LinearMap.trace E V (projector e) =
      (Module.finrank E (packet (E := E) (V := V) e) : E) := by
  exact ((LinearMap.isProj_range_iff_isIdempotentElem _).mpr
    (projector_idempotent (E := E) (V := V) he)).trace

/-- Occupancy means a nonzero image, and rank positivity is a statement in N. -/
theorem occupied_iff_positive_rank (e : T) :
    packet (E := E) (V := V) e ≠ ⊥ ↔
      0 < Module.finrank E (packet (E := E) (V := V) e) := by
  rw [Module.finrank_pos_iff, Submodule.nontrivial_iff_ne_bot]

/-- Characteristic zero is needed only for nonzero scalar trace detection. -/
theorem occupied_iff_trace_ne_zero [CharZero E] {e : T} (he : IsIdempotentElem e) :
    packet (E := E) (V := V) e ≠ ⊥ ↔
      LinearMap.trace E V (projector e) ≠ 0 := by
  rw [trace_eq_cast_finrank he, Nat.cast_ne_zero, occupied_iff_positive_rank,
    Nat.pos_iff_ne_zero]

end PaperXII.PacketTrace
