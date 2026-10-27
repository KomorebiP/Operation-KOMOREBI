import PaperXI.SchurHom
import PaperXI.TensorFixed

/-! Corollary 5.7: the actual tensor fixed space is the actual Hom space.
The refined packet data are precisely the inherited Proposition 5.6 contract.
The 0/1 bound is derived from irreducibility, not supplied with the packets. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameHomCriterion
open scoped BigOperators Classical TensorProduct
open PaperXI.CyclicAction PaperXI.PacketTransport PaperXI.GeneratedIrreducibility
variable {G I X Y : Type*} [Group G] [Group I]
variable [AddCommGroup X] [Module ℂ X] [FiniteDimensional ℂ X]
variable [AddCommGroup Y] [Module ℂ Y] [FiniteDimensional ℂ Y]
variable {A : Type*} [Fintype A] {V : A → Type*}
variable [∀ a, AddCommGroup (V a)] [∀ a, Module ℂ (V a)] [∀ a, FiniteDimensional ℂ (V a)]
variable {M : ℕ} [NeZero M]

/-- Actual Hom dimension, computed by the refined tensor packet test. -/
theorem hom_finrank_eq_trivial_count
    (ξ : Representation ℂ G X) (η : Representation ℂ G Y) (τ : ∀ a, Representation ℂ G (V a))
    (e : (X ⊗[ℂ] Y) ≃ₗ[ℂ] (∀ a, V a)) (he : ∀ g x a, e ((ξ.tprod η) g x) a = τ a g (e x a))
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
    Module.finrank ℂ (Representation.IntertwiningMap ξ.dual η) =
      (Finset.univ.filter (fun a => j a = 0 ∧ c a = 1)).card := by
  rw [PaperXI.DualityLinear.hom_finrank_eq_tensor_invariants ξ η]
  exact PaperXI.TensorFixed.count_trivial_packets (ξ.tprod η) τ e he ι φ hgen ρ s hs
    hfactor q hrel n hn b j v hv hb c hclose

/-- Source-facing zero-or-one criterion for irreducible tame atoms. -/
theorem tame_hom_test
    (ξ : Representation ℂ G X) (η : Representation ℂ G Y)
    [Representation.IsIrreducible ξ] [Representation.IsIrreducible η] (τ : ∀ a, Representation ℂ G (V a))
    (e : (X ⊗[ℂ] Y) ≃ₗ[ℂ] (∀ a, V a)) (he : ∀ g x a, e ((ξ.tprod η) g x) a = τ a g (e x a))
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
    let N := (Finset.univ.filter (fun a => j a = 0 ∧ c a = 1)).card
    Module.finrank ℂ (Representation.IntertwiningMap ξ.dual η) = N ∧
      (N = 0 ∨ N = 1) ∧
      (Module.finrank ℂ (Representation.IntertwiningMap ξ.dual η) = 1 ↔ N = 1) := by
  dsimp only
  have hcount := hom_finrank_eq_trivial_count ξ η τ e he ι φ hgen ρ s hs hfactor q hrel
    n hn b j v hv hb c hclose
  let : Representation.IsIrreducible ξ.dual := PaperXI.DualityLinear.dual_irreducible ξ
  have hdim := PaperXI.SchurHom.finrank_zero_or_one ξ.dual η
  rw [hcount] at hdim
  exact ⟨hcount, hdim, by rw [hcount]⟩

end PaperXI.TameHomCriterion
