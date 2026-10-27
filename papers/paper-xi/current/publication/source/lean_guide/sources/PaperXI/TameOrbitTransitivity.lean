import PaperXI.OrbitSpan
import PaperXI.GeneratedIrreducibility

/-! The orbit-transitivity part of Theorem 3.2 for an actual irreducible group
representation with explicitly generating tame inertia and Frobenius. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameOrbitTransitivity
open scoped BigOperators
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.FrobeniusOrbit
open PaperXI.OrbitSpan PaperXI.GeneratedIrreducibility
variable {G V : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable {M : ℕ} [NeZero M]

abbrev tameRestriction (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) : Action (K := ℂ) (V := V) (M := M) := π.comp ι

def generators (ι : Multiplicative (ZMod M) →* G) (φ : G) : Set G :=
  Set.range ι ∪ {φ, φ⁻¹}

omit [NeZero M] in
/-- The geometric group relation implies the checked operator relation. -/
theorem geometric_relation (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M))) :
    (actionEquiv π φ).symm.conj (operator (tameRestriction π ι) 1) =
      operator (tameRestriction π ι) (q : ZMod M) := by
  apply LinearMap.ext
  intro v
  change π φ⁻¹ (π (ι (Multiplicative.ofAdd (1 : ZMod M))) (π φ v)) =
    π (ι (Multiplicative.ofAdd (q : ZMod M))) v
  calc
    _ = π (φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ) v := by
      simp [map_mul, Module.End.mul_apply]
    _ = _ := by rw [hrel]

theorem generators_preserve_orbitSpan (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M))) (j : ZMod M) :
    ∀ g ∈ generators ι φ, ∀ v ∈ orbitSpan (tameRestriction π ι) q j,
      π g v ∈ orbitSpan (tameRestriction π ι) q j := by
  intro g hg v hv
  rcases hg with ⟨a, rfl⟩ | hg
  · exact inertia_stable (tameRestriction π ι) q j a.toAdd hv
  · rcases hg with hg | hg
    · have heq : g = φ := hg
      subst g
      exact forward_stable (tameRestriction π ι) (actionEquiv π φ) q
        (geometric_relation π ι φ q hrel) j hv
    · have heq : g = φ⁻¹ := hg
      subst g
      exact backward_stable (tameRestriction π ι) (actionEquiv π φ) q
        (geometric_relation π ι φ q hrel) j hv

/-- A packet orbit spans a genuine subrepresentation of the whole group. -/
def orbitSubrepresentation (π : Representation ℂ G V)
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M))) (j : ZMod M) : Subrepresentation π where
  toSubmodule := orbitSpan (tameRestriction π ι) q j
  apply_mem_toSubmodule g _ hv :=
    stable_of_generators π (generators ι φ) hgen _
      (generators_preserve_orbitSpan π ι φ q hrel j) g hv

theorem orbitSpan_eq_top (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥) :
    orbitSpan (tameRestriction π ι) q j = ⊤ := by
  exact (eq_bot_or_top π (generators ι φ) hgen _
    (generators_preserve_orbitSpan π ι φ q hrel j)).resolve_left
      (span_ne_bot (tameRestriction π ι) q hj)

/-- Any two nonzero tame character packets lie in one Frobenius orbit. -/
theorem nonzero_packets_one_orbit (π : Representation ℂ G V)
    [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) (φ : G) (q : (ZMod M)ˣ)
    (hgen : Submonoid.closure (generators ι φ) = ⊤)
    (hrel : φ⁻¹ * ι (Multiplicative.ofAdd (1 : ZMod M)) * φ =
      ι (Multiplicative.ofAdd (q : ZMod M)))
    {j k : ZMod M} (hj : packet (tameRestriction π ι) j ≠ ⊥)
    (hk : packet (tameRestriction π ι) k ≠ ⊥) :
    ∃ n : ℤ, ((q ^ n : (ZMod M)ˣ) : ZMod M) * j = k :=
  related_of_span_top (tameRestriction π ι) q (orbitSpan_eq_top π ι φ q hgen hrel hj) hk

/-- Completeness ensures that the support of an irreducible representation is nonempty. -/
theorem exists_nonzero_packet (π : Representation ℂ G V) [Representation.IsIrreducible π]
    (ι : Multiplicative (ZMod M) →* G) :
    ∃ j : ZMod M, packet (tameRestriction π ι) j ≠ ⊥ := by
  have : Nontrivial V := nontrivial_space π
  obtain ⟨v, hv⟩ := exists_ne (0 : V)
  by_contra hn
  push Not at hn
  have hp (j : ZMod M) : projector (tameRestriction π ι) j v = 0 := by
    have h := PaperXI.FourierPackets.projector_mem_packet (tameRestriction π ι)
      ZMod.stdAddChar j v
    change projector (tameRestriction π ι) j v ∈ packet (tameRestriction π ι) j at h
    simpa [hn j] using h
  have hsum := PaperXI.FourierPackets.vector_reconstruction (tameRestriction π ι)
    ZMod.stdAddChar (ZMod.isPrimitive_stdAddChar M) (NeZero.ne (M : ℂ)) v
  change (∑ j : ZMod M, projector (tameRestriction π ι) j v) = v at hsum
  have hz : v = 0 := by simpa only [hp, Finset.sum_const_zero] using hsum.symm
  exact hv hz

end PaperXI.TameOrbitTransitivity
