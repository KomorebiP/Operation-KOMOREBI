import PaperXI.PacketBasis
import PaperXI.InertiaFixed
import PaperXI.InertiaQuotient
import Mathlib.Data.Rat.Cast.Order

/-! The nontrivial tame conductor calculation, with its finite-quotient
attachment explicit. These definitions encode finite ramification sums. They
do not construct local fields, Weil groups or ramification filtrations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameConductor
open scoped BigOperators Classical
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusPeriod
open PaperXI.GeneratedIrreducibility PaperXI.TameOrbitTransitivity
variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable [FiniteDimensional ℂ V]
variable {M : ℕ} [NeZero M]

omit [FiniteDimensional ℂ V] [NeZero M] in
/-- The trivial inertia label has exact period one. -/
theorem zero_label_period (q : (ZMod M)ˣ) : period q 0 = 1 :=
  Nat.dvd_one.mp ((stabilizing_power_iff q 0 1).mp (by simp))

/-- Nonzero inertia invariants would force the whole irreducible space to
have dimension one. No invariant-space or orbit-basis conclusion is assumed. -/
theorem inertia_invariants_eq_bot
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (hdim : 1 < Module.finrank ℂ V) : (Representation.invariants (π.comp ι)) = ⊥ := by
  by_contra h
  have hj : packet (tameRestriction π ι) 0 ≠ ⊥ := by
    simpa only [PaperXI.InertiaFixed.invariants_eq_packet_zero] using h
  have hn := PaperXI.PacketBasis.finrank_eq_period π ι φ q hgen hrel hj
  rw [zero_label_period] at hn
  omega

theorem inertia_finrank_zero
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (hdim : 1 < Module.finrank ℂ V) : Module.finrank ℂ (Representation.invariants (π.comp ι)) = 0 := by
  rw [inertia_invariants_eq_bot π ι φ q hgen hrel hdim]
  simp

/-- Codimension of the genuine J-fixed subspace. -/
def fixedCodimension (π : Representation ℂ G V) (J : Subgroup G) : ℕ :=
  Module.finrank ℂ V - Module.finrank ℂ (Representation.invariants (π.comp J.subtype))

/-- A finite positive-depth ramification sum; the filtration and conventional
weights must be supplied and identified by the local-field attachment. -/
def finiteSwan (π : Representation ℂ G V) (S : Finset ℕ)
    (J : ℕ → Subgroup G) (w : ℕ → ℚ) : ℚ :=
  ∑ r ∈ S, w r * (fixedCodimension π (J r) : ℚ)

omit [NeZero M] [FiniteDimensional ℂ V] in
theorem invariants_eq_top_of_trivial_on (π : Representation ℂ G V) (J : Subgroup G)
    (hJ : ∀ g ∈ J, ∀ v, π g v = v) : (Representation.invariants (π.comp J.subtype)) = ⊤ := by
  apply top_unique
  intro v _ g
  exact hJ g g.property v

omit [NeZero M] [FiniteDimensional ℂ V] in
theorem fixedCodimension_zero_of_trivial_on (π : Representation ℂ G V) (J : Subgroup G)
    (hJ : ∀ g ∈ J, ∀ v, π g v = v) : fixedCodimension π J = 0 := by
  unfold fixedCodimension
  rw [invariants_eq_top_of_trivial_on π J hJ]
  simp

omit [NeZero M] [FiniteDimensional ℂ V] in
/-- Wild triviality is an action hypothesis, not an assumed Swan value. -/
theorem finiteSwan_zero (π : Representation ℂ G V) (P : Subgroup G)
    (hP : ∀ g ∈ P, ∀ v, π g v = v)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (hJP : ∀ r ∈ S, J r ≤ P) : finiteSwan π S J w = 0 := by
  unfold finiteSwan
  apply Finset.sum_eq_zero
  intro r hr
  rw [fixedCodimension_zero_of_trivial_on π (J r)
    (fun g hg v => hP g (hJP r hr hg) v)]
  simp

/-- Finite Artin expression with the actual inertia fixed-space term. -/
def finiteArtin (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ) : ℚ :=
  (Module.finrank ℂ V : ℚ) - (Module.finrank ℂ (Representation.invariants (π.comp ι)) : ℚ) +
    finiteSwan π S J w

/-- Source-facing conductor endpoint in the declared finite-inertia model. -/
theorem conductor_of_nontrivial_tame_atom
    (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    (hdim : 1 < Module.finrank ℂ V)
    (P : Subgroup G) (hP : ∀ g ∈ P, ∀ v, π g v = v)
    (S : Finset ℕ) (J : ℕ → Subgroup G) (w : ℕ → ℚ)
    (hJP : ∀ r ∈ S, J r ≤ P) :
    finiteSwan π S J w = 0 ∧
    Module.finrank ℂ (Representation.invariants (π.comp ι)) = 0 ∧
    finiteArtin π ι S J w = (Module.finrank ℂ V : ℚ) := by
  have hs := finiteSwan_zero π P hP S J w hJP
  have hi := inertia_finrank_zero π ι φ q hgen hrel hdim
  refine ⟨hs, hi, ?_⟩
  simp [finiteArtin, hs, hi]

end PaperXI.TameConductor
