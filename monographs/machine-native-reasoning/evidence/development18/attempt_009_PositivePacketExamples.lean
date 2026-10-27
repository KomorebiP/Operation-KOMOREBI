import MachineTheory.CoordinatePackets
import MachineTheory.PacketTransport
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-!
# Exact packet examples and hypothesis boundaries

The examples are actual linear maps over the reals. They distinguish a signed
Haar detail from a valid state in a transported cone, strict from non-strict mass,
complete positive maps from idempotent ones, and empty coordinate edge cases.
-/
namespace Komorebi.MachineTheory.PositivePackets.Examples

noncomputable section

open scoped BigOperators

abbrev V2 := ℝ × ℝ

def first : V2 →ₗ[ℝ] ℝ := LinearMap.fst ℝ ℝ ℝ
def second : V2 →ₗ[ℝ] ℝ := LinearMap.snd ℝ ℝ ℝ
def mass2 : V2 →ₗ[ℝ] ℝ := first + second

def quadrant : ConvexCone ℝ V2 where
  carrier := {v | 0 ≤ v.1 ∧ 0 ≤ v.2}
  smul_mem' := by
    intro c hc v hv
    exact ⟨mul_nonneg (le_of_lt hc) hv.1, mul_nonneg (le_of_lt hc) hv.2⟩
  add_mem' := by
    intro v hv w hw
    exact ⟨add_nonneg hv.1 hw.1, add_nonneg hv.2 hw.2⟩

def leftPacket : V2 →ₗ[ℝ] V2 := first.prod 0
def rightPacket : V2 →ₗ[ℝ] V2 := (0 : V2 →ₗ[ℝ] ℝ).prod second

def coordinateFamily (b : Bool) : V2 →ₗ[ℝ] V2 := if b then rightPacket else leftPacket

theorem strict_mass2 : StrictMass quadrant mass2 := by
  intro v hv hn
  change 0 < v.1 + v.2
  have h0 : v.1 ≠ 0 ∨ v.2 ≠ 0 := by
    by_contra h
    push_neg at h
    apply hn
    exact Prod.ext h.1 h.2
  change 0 ≤ v.1 ∧ 0 ≤ v.2 at hv
  rcases h0 with h | h
  · have hp : 0 < v.1 := lt_of_le_of_ne hv.1 (Ne.symm h)
    linarith
  · have hp : 0 < v.2 := lt_of_le_of_ne hv.2 (Ne.symm h)
    linarith

theorem coordinate_family_preserves (b : Bool) : Preserves quadrant (coordinateFamily b) := by
  intro v hv
  cases b <;> simpa [coordinateFamily, leftPacket, rightPacket, first, second, quadrant] using hv

theorem coordinate_family_complete : Complete coordinateFamily := by
  apply LinearMap.ext
  intro v
  ext <;> simp [Complete, LinearMap.sum_apply, coordinateFamily, leftPacket, rightPacket, first, second]

theorem coordinate_family_idempotent (b : Bool) :
    (coordinateFamily b).comp (coordinateFamily b) = coordinateFamily b := by
  apply LinearMap.ext
  intro v
  cases b <;> ext <;> simp [coordinateFamily, leftPacket, rightPacket, first, second]

theorem zero_weight_is_present :
    IsState quadrant mass2 (1, 0) ∧ weight mass2 coordinateFamily (1, 0) true = 0 ∧
    coordinateFamily true (1, 0) = 0 := by
  norm_num [IsState, quadrant, weight, mass2, coordinateFamily, leftPacket, rightPacket, first, second]

/-- The actual nonzero-index construction applies to a zero-weight boundary input. -/
theorem boundary_mixture :
    (∑ i : PositiveIndex mass2 coordinateFamily (1, 0),
      weight mass2 coordinateFamily (1, 0) i.val • normalized mass2 coordinateFamily (1, 0) i) =
      ((1, 0) : V2) :=
  mixture_reconstruction quadrant mass2 strict_mass2 coordinateFamily coordinate_family_preserves
    coordinate_family_complete (by norm_num [quadrant])

def average : V2 →ₗ[ℝ] V2 := ((1 / 2 : ℝ) • mass2).prod ((1 / 2 : ℝ) • mass2)
def detail : V2 →ₗ[ℝ] V2 := LinearMap.id - average
def haarFamily (b : Bool) : V2 →ₗ[ℝ] V2 := if b then detail else average

theorem haar_complete : Complete haarFamily := by
  apply LinearMap.ext
  intro v
  ext <;> simp [LinearMap.sum_apply, haarFamily, detail]

theorem haar_idempotent (b : Bool) : (haarFamily b).comp (haarFamily b) = haarFamily b := by
  apply LinearMap.ext
  intro v
  cases b <;> ext <;>
    simp [haarFamily, detail, average, mass2, first, second] <;> ring

/-- The two ranges are orthogonal for the ordinary real coordinate inner product. -/
theorem haar_orthogonal (v w : V2) :
    (average v).1 * (detail w).1 + (average v).2 * (detail w).2 = 0 := by
  simp [average, detail, mass2, first, second]
  ring

theorem haar_detail_packet : detail (3 / 4, 1 / 4) = ((1 / 4, -(1 / 4)) : V2) := by
  ext <;> norm_num [detail, average, mass2, first, second]

theorem haar_detail_zero_mass_nonzero :
    mass2 (detail (3 / 4, 1 / 4)) = 0 ∧ detail (3 / 4, 1 / 4) ≠ 0 := by
  rw [haar_detail_packet]
  norm_num [mass2, first, second]

theorem haar_detail_not_preserving : ¬ Preserves quadrant detail := by
  intro h
  have hv := h (1, 0) (by norm_num [quadrant])
  norm_num [quadrant, detail, average, mass2, first, second] at hv

/-- A nonnegative but non-strict functional misses a nonzero cone member. -/
theorem nonstrict_mass_counterexample :
    (∀ v ∈ quadrant, 0 ≤ first v) ∧ ((0, 1) : V2) ∈ quadrant ∧
    first (0, 1) = 0 ∧ ((0, 1) : V2) ≠ 0 ∧ ¬ StrictMass quadrant first := by
  refine ⟨fun _ hv => hv.1, by norm_num [quadrant], rfl, by norm_num, ?_⟩
  intro h
  have hp := h (0, 1) (by norm_num [quadrant]) (by norm_num)
  norm_num [first] at hp

def halfIdentity : V2 →ₗ[ℝ] V2 := (1 / 2 : ℝ) • LinearMap.id

theorem half_identity_preserves : Preserves quadrant halfIdentity := by
  intro v hv
  change 0 ≤ (1 / 2 : ℝ) * v.1 ∧ 0 ≤ (1 / 2 : ℝ) * v.2
  exact ⟨mul_nonneg (by norm_num) hv.1, mul_nonneg (by norm_num) hv.2⟩

theorem two_halves_complete : Complete (fun _ : Bool => halfIdentity) := by
  apply LinearMap.ext
  intro v
  ext <;> simp [LinearMap.sum_apply, halfIdentity] <;> ring

theorem half_identity_not_idempotent : halfIdentity.comp halfIdentity ≠ halfIdentity := by
  intro h
  have hh := congrArg Prod.fst (LinearMap.congr_fun h (1, 0))
  norm_num [halfIdentity] at hh

theorem incomplete_weight_counterexample :
    weight mass2 (fun _ : Unit => halfIdentity) (1, 0) () = (1 / 2 : ℝ) := by
  norm_num [weight, mass2, halfIdentity, first, second]

def signedFamily (b : Bool) : V2 →ₗ[ℝ] V2 :=
  if b then (2 : ℝ) • LinearMap.id else -(LinearMap.id : V2 →ₗ[ℝ] V2)

theorem signed_family_complete : Complete signedFamily := by
  apply LinearMap.ext
  intro v
  ext <;> simp [LinearMap.sum_apply, signedFamily] <;> ring

theorem signed_weight_negative : weight mass2 signedFamily (1, 0) false = -1 := by
  norm_num [weight, signedFamily, mass2, first, second]

/-- A genuinely invertible coordinate map that creates signed coordinates. -/
def shear : V2 ≃ₗ[ℝ] V2 where
  toFun v := (v.1 - v.2, v.2)
  invFun w := (w.1 + w.2, w.2)
  left_inv := by intro v; ext <;> simp
  right_inv := by intro v; ext <;> simp
  map_add' := by intro v w; ext <;> simp <;> ring
  map_smul' := by intro c v; ext <;> simp <;> ring

theorem transported_signed_state :
    IsState (Transport.cone shear quadrant) (Transport.mass shear mass2) (-1, 1) := by
  have h := (Transport.state_iff shear quadrant mass2 (0, 1)).mpr
    (by norm_num [IsState, quadrant, mass2, first, second])
  exact h

theorem transported_mass_strict :
    StrictMass (Transport.cone shear quadrant) (Transport.mass shear mass2) :=
  Transport.strictMass shear quadrant mass2 strict_mass2

theorem signed_state_not_in_original_cone : ((-1, 1) : V2) ∉ quadrant := by
  norm_num [quadrant]

theorem transported_family_preserves (b : Bool) :
    Preserves (Transport.cone shear quadrant) (Transport.operator shear (coordinateFamily b)) :=
  Transport.preserves shear quadrant (coordinateFamily b) (coordinate_family_preserves b)

/-- The transported second projector has a negative coordinate, with positive valid mass. -/
theorem transported_packet_explicit :
    Transport.operator shear rightPacket (0, 1 / 2) = ((-(1 / 2), 1 / 2) : V2) ∧
    Transport.mass shear mass2 (-(1 / 2), 1 / 2) = (1 / 2 : ℝ) := by
  norm_num [Transport.operator, Transport.mass, shear, rightPacket, second, mass2, first]

/-- Empty coordinate and index sets are allowed by the selector construction. -/
theorem empty_coordinate_family :
    Complete (Coordinate.selector (fun x : Fin 0 => x)) := Coordinate.selector_complete _

/-- Completeness on an empty index family cannot support a unit-mass input. -/
theorem no_state_for_empty_family {V : Type*} [AddCommGroup V] [Module ℝ V]
    (C : ConvexCone ℝ V) (m : V →ₗ[ℝ] ℝ) (P : Fin 0 → V →ₗ[ℝ] V)
    (hc : Complete P) (v : V) : ¬ IsState C m v := by
  intro hv
  have h := sum_weights_one C m P hc hv
  simp at h

end
end Komorebi.MachineTheory.PositivePackets.Examples
