module
public import KomorebiPhysics.LadderDomains
public import KomorebiPhysics.ResidueProjectors

/-! Unbounded ladder routing with an actual domain-valued input packet.
Residue subtraction is in ZMod, so the wraparound and vacuum are distinct. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace LadderRouting
open BoundedSpectral LadderDomains ResidueProjectors
open scoped lp BigOperators
variable (M : ℕ) [NeZero M]

theorem packet_mem (r : ZMod M) (x : domain) : projector M r x ∈ domain :=
  projector_mem_domain M (fun n : ℕ => Real.sqrt n) r x

/-- The input projection is packaged only after domain preservation is proved. -/
def packet (r : ZMod M) : domain →ₗ[ℂ] domain where
  toFun x := ⟨projector M r x, packet_mem M r x⟩
  map_add' x y := Subtype.ext ((projector M r).map_add (x : Space) (y : Space))
  map_smul' c x := Subtype.ext ((projector M r).map_smul c (x : Space))

theorem packet_coe (r : ZMod M) (x : domain) :
    (packet M r x : Space) = projector M r x := rfl

theorem lower_packet (s : ZMod M) (x : domain) :
    lower (packet M s x) = projector M (s-1) (lower x) := by
  apply lp.ext
  funext n
  simp only [lower_apply, packet_coe, projector_apply, Nat.cast_add, Nat.cast_one]
  have h : (n : ZMod M) + 1 = s ↔ (n : ZMod M) = s-1 := by
    exact eq_sub_iff_add_eq.symm
  simp only [h, mul_ite, mul_zero]

theorem raise_packet (s : ZMod M) (x : domain) :
    raise (packet M s x) = projector M (s+1) (raise x) := by
  apply lp.ext
  funext n
  cases n with
  | zero => simp [raise_zero, projector_apply]
  | succ n =>
    simp only [raise_succ, packet_coe, projector_apply, Nat.cast_add, Nat.cast_one]
    have h : (n : ZMod M) + 1 = s+1 ↔ (n : ZMod M) = s := add_left_inj 1
    simp only [h, mul_ite, mul_zero]

/-- Source (6.51), as an equality of actual Hilbert vectors on the domain. -/
theorem lower_routing (r s : ZMod M) (h : r ≠ s-1) (x : domain) :
    projector M r (lower (packet M s x)) = 0 := by
  rw [lower_packet]
  exact projector_orthogonal M r (s-1) h (lower x)

/-- Source (6.52), with raising orientation and domain input preserved. -/
theorem raise_routing (r s : ZMod M) (h : r ≠ s+1) (x : domain) :
    projector M r (raise (packet M s x)) = 0 := by
  rw [raise_packet]
  exact projector_orthogonal M r (s+1) h (raise x)

theorem lower_allowed_corner (s : ZMod M) (x : domain) :
    projector M (s-1) (lower (packet M s x)) = lower (packet M s x) := by
  rw [lower_packet]
  exact projector_idempotent M (s-1) (lower x)

theorem raise_allowed_corner (s : ZMod M) (x : domain) :
    projector M (s+1) (raise (packet M s x)) = raise (packet M s x) := by
  rw [raise_packet]
  exact projector_idempotent M (s+1) (raise x)

/-- Ladder outputs belong to l2, but are not assumed to return to this domain. -/
theorem lower_full_resolution (x : domain) :
    ∑ r : ZMod M, projector M r (lower x) = lower x := projector_complete M _

theorem raise_full_resolution (x : domain) :
    ∑ r : ZMod M, projector M r (raise x) = raise x := projector_complete M _

end LadderRouting
end KomorebiPhysics
