import PaperXI.InvariantAssembly

/-! Proposition 5.6 for an actual representation with supplied refined packets. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TensorFixed
open scoped Classical
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.GeneratedIrreducibility
variable {G I U : Type*} [Group G] [Group I] [AddCommGroup U] [Module ℂ U]
variable {A : Type*} [Fintype A] {V : A → Type*}
variable [∀ a, AddCommGroup (V a)] [∀ a, Module ℂ (V a)] [∀ a, FiniteDimensional ℂ (V a)]
variable {M : ℕ} [NeZero M]

/-- The right side counts packet indices, not polynomial root multiplicities. -/
theorem count_trivial_packets
    (π : Representation ℂ G U) (τ : ∀ a, Representation ℂ G (V a))
    (e : U ≃ₗ[ℂ] (∀ a, V a)) (he : ∀ g x a, e (π g x) a = τ a g (e x a))
    (ι : I →* G) (φ : G) (hgen : Submonoid.closure (Set.range ι ∪ {φ, φ⁻¹}) = ⊤)
    (ρ : ∀ a, Action (K := ℂ) (V := V a) (M := M))
    (s : I →* Multiplicative (ZMod M)) (hs : Function.Surjective s)
    (hfactor : ∀ a, (τ a).comp ι = (ρ a).comp s) (q : (ZMod M)ˣ)
    (hrel : ∀ a, (actionEquiv (τ a) φ).symm.conj (operator (ρ a) 1) =
      operator (ρ a) (q : ZMod M))
    (n : A → ℕ) (hn : ∀ a, 0 < n a) (b : ∀ a, Module.Basis (Fin (n a)) ℂ (V a))
    (j : A → ZMod M) (v : ∀ a, V a) (hv : ∀ a, v a ∈ packet (ρ a) (j a))
    (hb : ∀ a (i : Fin (n a)), b a i = (actionEquiv (τ a) φ ^ (i : ℕ)) (v a))
    (c : A → ℂ) (hclose : ∀ a, (actionEquiv (τ a) φ ^ n a) (v a) = c a • v a) :
    Module.finrank ℂ π.invariants = (Finset.univ.filter (fun a => j a = 0 ∧ c a = 1)).card := by
  have hP (a : A) : Module.finrank ℂ (τ a).invariants = if j a = 0 ∧ c a = 1 then 1 else 0 :=
    PaperXI.GroupFixed.packet_finrank (τ a) ι φ hgen (ρ a) s hs (hfactor a) q
      (hrel a) (hn a) (b a) (j a) (hv a) (hb a) (c a) (hclose a)
  simpa using PaperXI.InvariantAssembly.count_invariants π τ e he (fun a => j a = 0 ∧ c a = 1) hP

end PaperXI.TensorFixed
