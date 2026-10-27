import PaperXI.InvariantPolynomial
import PaperXI.PacketCycle

/-! Both local-polynomial branches for a cyclic interaction packet. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InteractionPolynomial
open Polynomial
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.InertiaFixed
open PaperXI.InvariantPolynomial
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

theorem character_trivial_iff (j : ZMod M) :
    (∀ a : ZMod M, ZMod.stdAddChar (j * a) = (1 : ℂ)) ↔ j = 0 := by
  constructor
  · intro h
    apply ZMod.injective_stdAddChar
    simpa using h 1
  · rintro rfl
    simp

/-- Proposition 5.4: the determinant is on actual inertia invariants. -/
theorem local_polynomial [FiniteDimensional ℂ V]
    (ρ : Action (K := ℂ) (V := V) (M := M)) (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ V) (j : ZMod M) {v : V}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (F ^ n) v = c • v) :
    localPolynomial ρ F q h = if j = 0 then 1 - C c * X ^ n else 1 := by
  classical
  have hinv := invariants_of_cycle_basis ρ F q h b j hv hb
  by_cases hj : j = 0
  · rw [ite_eq_left hj] at hinv ⊢
    rw [localPolynomial_of_top ρ F q h hinv, operatorPolynomial]
    have hlin (i : Fin n) : b i = (F.toLinearMap ^ (i : ℕ)) v := by
      rw [PaperXI.PacketCycle.linear_power]
      exact hb i
    have hcl : (F.toLinearMap ^ n) v = c • v := by
      simpa only [PaperXI.PacketCycle.linear_power] using hclose
    rw [PaperXI.CyclicPolynomial.charpoly_of_orbit_basis F.toLinearMap hn b v hlin c hcl,
      PaperXI.CyclicPolynomial.reverse_cycle_polynomial]
  · rw [ite_eq_right hj] at hinv ⊢
    exact localPolynomial_of_bot ρ F q h hinv

/-- The same formula using the literal trivial-character condition. -/
theorem local_polynomial_character_form [FiniteDimensional ℂ V]
    (ρ : Action (K := ℂ) (V := V) (M := M)) (F : V ≃ₗ[ℂ] V) (q : (ZMod M)ˣ)
    (h : F.symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ V) (j : ZMod M) {v : V}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (F ^ n) v = c • v) :
    localPolynomial ρ F q h =
      if (∀ a : ZMod M, ZMod.stdAddChar (j * a) = (1 : ℂ))
      then 1 - C c * X ^ n else 1 := by
  simpa only [character_trivial_iff] using local_polynomial ρ F q h hn b j hv hb c hclose

variable {G : Type*} [Group G]

/-- Applied to an actual group action with the geometric inertia relation.
No irreducibility or group-generation hypothesis is required. -/
theorem group_local_polynomial [FiniteDimensional ℂ V]
    (π : Representation ℂ G V) (ι : Multiplicative (ZMod M) →* G)
    (φ : G) (q : (ZMod M)ˣ)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ V) (j : ZMod M) {v : V}
    (hv : v ∈ packet (PaperXI.TameOrbitTransitivity.tameRestriction π ι) j)
    (hb : ∀ i : Fin n, b i = (PaperXI.GeneratedIrreducibility.actionEquiv π φ ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (PaperXI.GeneratedIrreducibility.actionEquiv π φ ^ n) v = c • v) :
    localPolynomial (PaperXI.TameOrbitTransitivity.tameRestriction π ι)
      (PaperXI.GeneratedIrreducibility.actionEquiv π φ) q
      (PaperXI.TameOrbitTransitivity.geometric_relation π ι φ q hrel) =
        if j = 0 then 1 - C c * X ^ n else 1 :=
  local_polynomial _ _ _ _ hn b j hv hb c hclose

end PaperXI.InteractionPolynomial
