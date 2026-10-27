import PaperXI.CycleFixed
import PaperXI.InertiaQuotient

/-! Fixedness under an actual group, including supplied inertia quotient data. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GroupFixed
open scoped BigOperators Classical
open PaperXI.CycleFixed PaperXI.GeneratedIrreducibility
variable {K V G I : Type*} [Field K] [AddCommGroup V] [Module K V] [Group G] [Group I]

theorem fixed_of_generators (π : Representation K G V) (S : Set G)
    (hgen : Submonoid.closure S = ⊤) (x : V) (hx : ∀ g ∈ S, π g x = x) :
    x ∈ π.invariants := by
  intro g
  have hg : g ∈ Submonoid.closure S := by rw [hgen]; trivial
  induction hg using Submonoid.closure_induction with
  | mem g hg => exact hx g hg
  | one => simp
  | mul a b _ _ ha hb => simp [map_mul, Module.End.mul_apply, ha, hb]

theorem invariants_eq_common (π : Representation K G V) (ι : I →* G) (φ : G)
    (hgen : Submonoid.closure (Set.range ι ∪ {φ, φ⁻¹}) = ⊤) :
    π.invariants = (Representation.invariants (π.comp ι)) ⊓ fixedSpace (π φ) := by
  ext x
  constructor
  · intro hx
    exact ⟨fun a => hx (ι a), (mem_fixedSpace _ _).mpr (hx φ)⟩
  · rintro ⟨hI, hF⟩
    have hF' := (mem_fixedSpace _ _).mp hF
    apply fixed_of_generators π _ hgen x
    intro g hg
    rcases hg with ⟨a, rfl⟩ | hg
    · exact hI a
    · rcases hg with hg | hg
      · have he : g = φ := hg
        simpa [he] using hF'
      · have he : g = φ⁻¹ := hg
        subst g
        have h := congrArg (π φ⁻¹) hF'
        simpa using h.symm

variable {U : Type*} [AddCommGroup U] [Module ℂ U]
open PaperXI.CyclicAction PaperXI.PacketTransport

theorem orbit_basis_steps (F : U ≃ₗ[ℂ] U) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) ℂ U) (v : U)
    (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) (c : ℂ)
    (hclose : (F ^ n) v = c • v) :
    (∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩) ∧
    F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩ := by
  constructor
  · intro i hi
    rw [hb, hb, pow_succ']
    rfl
  · rw [hb, hb]
    have hn' : n = (n - 1) + 1 := by omega
    have h := hclose
    conv_lhs at h => rw [hn', pow_succ']
    simpa using h

/-- The count for one packet uses the actual full-group invariant space. -/
theorem packet_finrank {M : ℕ} [NeZero M]
    (π : Representation ℂ G U) (ι : I →* G) (φ : G)
    (hgen : Submonoid.closure (Set.range ι ∪ {φ, φ⁻¹}) = ⊤)
    (ρ : Action (K := ℂ) (V := U) (M := M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
    (hfactor : π.comp ι = ρ.comp s) (q : (ZMod M)ˣ)
    (hrel : (actionEquiv π φ).symm.conj (operator ρ 1) = operator ρ (q : ZMod M))
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) ℂ U) (j : ZMod M) {v : U}
    (hv : v ∈ packet ρ j) (hb : ∀ i : Fin n, b i = (actionEquiv π φ ^ (i : ℕ)) v)
    (c : ℂ) (hclose : (actionEquiv π φ ^ n) v = c • v) :
    Module.finrank ℂ π.invariants = if j = 0 ∧ c = 1 then 1 else 0 := by
  have hI : Representation.invariants (π.comp ι) = if j = 0 then ⊤ else ⊥ := by
    rw [hfactor, PaperXI.InertiaQuotient.invariants_comp_of_surjective ρ s hs]
    exact PaperXI.InertiaFixed.invariants_of_cycle_basis ρ (actionEquiv π φ) q hrel b j hv hb
  have hsteps := orbit_basis_steps (actionEquiv π φ) hn b v hb c hclose
  rw [invariants_eq_common π ι φ hgen, hI]
  by_cases hj : j = 0
  · rw [ite_eq_left hj, top_inf_eq]
    simpa only [hj, true_and] using fixedSpace_finrank (π φ) hn b hsteps.1 c hsteps.2
  · rw [ite_eq_right hj, bot_inf_eq]
    simp [hj]

end PaperXI.GroupFixed
