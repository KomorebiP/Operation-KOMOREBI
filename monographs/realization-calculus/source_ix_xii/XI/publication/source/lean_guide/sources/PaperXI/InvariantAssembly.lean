import PaperXI.GroupFixed
import Mathlib.LinearAlgebra.Dimension.Constructions

/-! Actual invariant spaces under a supplied equivariant finite decomposition. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.InvariantAssembly
open scoped BigOperators Classical
variable {K G U : Type*} [Field K] [Group G] [AddCommGroup U] [Module K U]
variable {ι : Type*} {V : ι → Type*} [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]

/-- Restrict an equivariant decomposition to the canonical invariant spaces. -/
def invariantsEquiv (π : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (π g x) i = τ i g (e x i)) :
    π.invariants ≃ₗ[K] (∀ i, (τ i).invariants) where
  toFun x i := ⟨e x i, fun g => by rw [← he, x.property g]⟩
  invFun x := ⟨e.symm (fun i => x i), by
    intro g
    apply e.injective
    ext i
    rw [he, e.apply_symm_apply]
    exact (x i).property g⟩
  left_inv x := by apply Subtype.ext; exact e.symm_apply_apply x
  right_inv x := by ext i; exact congrFun (e.apply_symm_apply (fun i => x i)) i
  map_add' x y := by ext i; simp
  map_smul' c x := by ext i; simp

theorem invariantsEquiv_apply (π : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (π g x) i = τ i g (e x i))
    (x : π.invariants) (i : ι) : (invariantsEquiv π τ e he x i : V i) = e x i := rfl

theorem finrank_invariants [Fintype ι] [∀ i, FiniteDimensional K (V i)]
    (π : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (π g x) i = τ i g (e x i)) :
    Module.finrank K π.invariants = ∑ i, Module.finrank K (τ i).invariants := by
  rw [(invariantsEquiv π τ e he).finrank_eq, Module.finrank_pi_fintype]

/-- A literal count, after independently computing each actual packet fixed space. -/
theorem count_invariants [Fintype ι] [∀ i, FiniteDimensional K (V i)]
    (π : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (π g x) i = τ i g (e x i))
    (P : ι → Prop) [DecidablePred P] (hP : ∀ i, Module.finrank K (τ i).invariants = if P i then 1 else 0) :
    Module.finrank K π.invariants = (Finset.univ.filter P).card := by
  rw [finrank_invariants π τ e he]
  simp_rw [hP]
  simp

end PaperXI.InvariantAssembly
