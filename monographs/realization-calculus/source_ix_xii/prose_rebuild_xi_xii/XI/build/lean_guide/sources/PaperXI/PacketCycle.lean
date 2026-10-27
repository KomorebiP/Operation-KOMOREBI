import PaperXI.CycleCoordinates
import PaperXI.PacketBasis

/-! Cycle invariants of the actual irreducible tame algebraic group action. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketCycle
open Polynomial
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {V : Type*} [AddCommGroup V] [Module ℂ V]

theorem linear_power (F : V ≃ₗ[ℂ] V) (n : ℕ) (v : V) :
    (F.toLinearMap ^ n) v = (F ^ n) v := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [pow_succ', pow_succ']
    change F ((F.toLinearMap ^ n) v) = F ((F ^ n) v)
    rw [ih]

variable {G : Type*} [Group G] {M : ℕ} [NeZero M]
variable (π : Representation ℂ G V) [Representation.IsIrreducible π]
variable (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
variable (hgen : Submonoid.closure (generators ι φ) = ⊤)
variable (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
  ι (Multiplicative.ofAdd (q : ZMod M)))

include hgen hrel

/-- The characteristic polynomial of the actual Frobenius action. -/
theorem charpoly [FiniteDimensional ℂ V] (j : ZMod M) {v : V}
    (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    (actionEquiv π φ).toLinearMap.charpoly = X ^ period q j - C c := by
  let b := PaperXI.PacketBasis.orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose
  apply PaperXI.CyclicPolynomial.charpoly_of_orbit_basis _ (period_pos q j) b v
  · intro a
    rw [linear_power]
    exact PaperXI.PacketBasis.orbitBasis_apply π ι φ q hgen hrel j hv hv0 hc hclose a
  · simpa only [linear_power] using hclose

theorem det [FiniteDimensional ℂ V] (j : ZMod M) {v : V}
    (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    (actionEquiv π φ).toLinearMap.det = (-1) ^ (period q j - 1) * c := by
  let b := PaperXI.PacketBasis.orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose
  apply PaperXI.CyclicPolynomial.det_of_orbit_basis _ (period_pos q j) b v
  · intro a
    rw [linear_power]
    exact PaperXI.PacketBasis.orbitBasis_apply π ι φ q hgen hrel j hv hv0 hc hclose a
  · simpa only [linear_power] using hclose

theorem ambient_polynomial [FiniteDimensional ℂ V] (j : ZMod M) {v : V}
    (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    (LinearMap.toMatrix
      (PaperXI.PacketBasis.orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose)
      (PaperXI.PacketBasis.orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose)
      (actionEquiv π φ).toLinearMap).charpolyRev = 1 - C c * X ^ period q j := by
  rw [← Matrix.reverse_charpoly, LinearMap.charpoly_toMatrix,
    charpoly π ι φ q hgen hrel j hv hv0 hc hclose,
    PaperXI.CyclicPolynomial.reverse_cycle_polynomial]

/-- Every nonzero packet supplies a nonzero closing scalar with these invariants. -/
theorem exists_cycle_invariants [FiniteDimensional ℂ V] {j : ZMod M}
    (hj : packet (tameRestriction π ι) j ≠ ⊥) :
    ∃ c : ℂ, c ≠ 0 ∧
      (actionEquiv π φ).toLinearMap.charpoly = X ^ period q j - C c ∧
      (actionEquiv π φ).toLinearMap.det = (-1) ^ (period q j - 1) * c := by
  obtain ⟨c, v, hc, hv, hv0, hclose⟩ := PaperXI.PacketReturn.exists_closing_eigenvector
    (tameRestriction π ι) (actionEquiv π φ) q (geometric_relation π ι φ q hrel) hj
  exact ⟨c, hc, charpoly π ι φ q hgen hrel j hv hv0 hc hclose,
    det π ι φ q hgen hrel j hv hv0 hc hclose⟩

end PaperXI.PacketCycle
