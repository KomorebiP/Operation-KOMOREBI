import PaperXI.PacketLines
import Mathlib.LinearAlgebra.Basis.Basic

/-! The finite Frobenius orbit is a proved basis, giving the exact ambient
dimension and the action of inertia and Frobenius on the basis vectors. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PacketBasis
open scoped BigOperators
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
open PaperXI.CycleSpan PaperXI.PacketLines
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

theorem cycleVector_ne_zero (F : V ≃ₗ[ℂ] V) {v : V} (hv : v ≠ 0)
    {f : ℕ} (a : Fin f) : cycleVector F v a ≠ 0 := by
  intro h
  exact hv ((F ^ (a : ℕ)).injective (h.trans (map_zero _).symm))

/-- Distinct packet projectors extract coefficients from any linear relation. -/
theorem cycle_linearIndependent (ρ : Action (K := ℂ) (V := V) (M := M))
    (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    (j : ZMod M) {v : V} (hv : v ∈ packet ρ j) (hv0 : v ≠ 0) :
    LinearIndependent ℂ (cycleVector (f := period q j) F v) := by
  classical
  apply Fintype.linearIndependent_iff.mpr
  intro c hc a
  have hp := congrArg (projector ρ (orbitLabel q j a)) hc
  simp only [map_sum, map_smul, map_zero] at hp
  simp_rw [projector_cycle ρ F q h j hv] at hp
  have hs : c a • cycleVector F v a = 0 := by simpa using hp
  exact (smul_eq_zero.mp hs).resolve_right (cycleVector_ne_zero F hv0 a)

variable {G : Type*} [Group G]

/-- An explicit basis whose a-th vector is F^a v. -/
def orbitBasis (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    Module.Basis (Fin (period q j)) ℂ V :=
  Module.Basis.mk
    (cycle_linearIndependent (tameRestriction π ι) (actionEquiv π φ) q
      (geometric_relation π ι φ q hrel) j hv hv0)
    (cycleSpan_eq_top π ι φ q hgen hrel j hv hv0 hc hclose).ge

theorem orbitBasis_apply (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v)
    (a : Fin (period q j)) :
    orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose a = (actionEquiv π φ ^ (a : ℕ)) v :=
  Module.Basis.mk_apply _ _ a

theorem finrank_eq_period_of_return (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (j : ZMod M) {v : V} (hv : v ∈ packet (tameRestriction π ι) j) (hv0 : v ≠ 0)
    {c : ℂ} (hc : c ≠ 0) (hclose : (actionEquiv π φ ^ period q j) v = c • v) :
    Module.finrank ℂ V = period q j := by
  simpa using Module.finrank_eq_card_basis (orbitBasis π ι φ q hgen hrel j hv hv0 hc hclose)

/-- The algebraic dimension formula in Corollary 3.3. -/
theorem finrank_eq_period [FiniteDimensional ℂ V]
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥) :
    Module.finrank ℂ V = period q j := by
  obtain ⟨c, v, hc, hv, hv0, hclose⟩ := PaperXI.PacketReturn.exists_closing_eigenvector
    (tameRestriction π ι) (actionEquiv π φ) q (geometric_relation π ι φ q hrel) hj
  exact finrank_eq_period_of_return π ι φ q hgen hrel j hv hv0 hc hclose

theorem finrank_eq_orbit_card [FiniteDimensional ℂ V]
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥) :
    Module.finrank ℂ V = Nat.card {k : ZMod M // PaperXI.FrobeniusOrbit.Related q j k} := by
  rw [orbit_card]
  exact finrank_eq_period π ι φ q hgen hrel hj

end PaperXI.PacketBasis
