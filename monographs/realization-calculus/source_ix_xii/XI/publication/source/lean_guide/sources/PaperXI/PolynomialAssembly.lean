import PaperXI.InvariantAssembly
import PaperXI.PiPolynomial
import Mathlib.FieldTheory.RatFunc.Basic

/-! Restricted Frobenius and determinant products under equivariant decompositions. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.PolynomialAssembly
open scoped BigOperators Classical
open Polynomial PaperXI.InvariantPolynomial PaperXI.InvariantAssembly
variable {K G U : Type*} [Field K] [Group G] [AddCommGroup U] [Module K U]
variable {ι : Type*} {V : ι → Type*} [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]

def restricted (ρ : Representation K G U) (F : Module.End K U)
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants) : Module.End K ρ.invariants where
  toFun x := ⟨F x, hF x x.property⟩
  map_add' x y := by ext; simp
  map_smul' c x := by ext; simp

theorem restricted_apply (ρ : Representation K G U) (F : Module.End K U)
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants) (x : ρ.invariants) :
    (restricted ρ F hF x : U) = F x := rfl

theorem stable_of_decomposition
    (ρ : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (ρ g x) i = τ i g (e x i))
    (F : Module.End K U) (A : ∀ i, Module.End K (V i))
    (hA : ∀ i x, x ∈ (τ i).invariants → A i x ∈ (τ i).invariants)
    (hmap : ∀ x i, e (F x) i = A i (e x i)) :
    ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants := by
  intro x hx g
  apply e.injective
  funext i
  rw [he, hmap]
  exact hA i (e x i) (fun g => by rw [← he, hx g]) g

theorem restricted_conj
    (ρ : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (ρ g x) i = τ i g (e x i))
    (F : Module.End K U) (A : ∀ i, Module.End K (V i))
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants)
    (hA : ∀ i x, x ∈ (τ i).invariants → A i x ∈ (τ i).invariants)
    (hmap : ∀ x i, e (F x) i = A i (e x i)) :
    (invariantsEquiv ρ τ e he).conj (restricted ρ F hF) =
      LinearMap.piMap (fun i => restricted (τ i) (A i) (hA i)) := by
  apply LinearMap.ext
  intro x
  funext i
  apply Subtype.ext
  change e (F (e.symm (fun i => (x i : V i)))) i = A i (x i : V i)
  rw [hmap, e.apply_symm_apply]

theorem polynomial_product [Fintype ι] [FiniteDimensional K U]
    [∀ i, FiniteDimensional K (V i)]
    (ρ : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (ρ g x) i = τ i g (e x i))
    (F : Module.End K U) (A : ∀ i, Module.End K (V i))
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants)
    (hA : ∀ i x, x ∈ (τ i).invariants → A i x ∈ (τ i).invariants)
    (hmap : ∀ x i, e (F x) i = A i (e x i)) :
    operatorPolynomial (restricted ρ F hF) =
      ∏ i, operatorPolynomial (restricted (τ i) (A i) (hA i)) := by
  rw [← operatorPolynomial_conj (invariantsEquiv ρ τ e he),
    restricted_conj ρ τ e he F A hF hA hmap, PaperXI.PiPolynomial.operatorPolynomial_pi]

/-- Rational local factors are reciprocals of actual restricted determinants. -/
def localFactor [FiniteDimensional K U] (ρ : Representation K G U) (F : Module.End K U)
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants) : RatFunc K :=
  (algebraMap K[X] (RatFunc K) (operatorPolynomial (restricted ρ F hF)))⁻¹

theorem localFactor_product [Fintype ι] [FiniteDimensional K U]
    [∀ i, FiniteDimensional K (V i)]
    (ρ : Representation K G U) (τ : ∀ i, Representation K G (V i))
    (e : U ≃ₗ[K] (∀ i, V i)) (he : ∀ g x i, e (ρ g x) i = τ i g (e x i))
    (F : Module.End K U) (A : ∀ i, Module.End K (V i))
    (hF : ∀ x ∈ ρ.invariants, F x ∈ ρ.invariants)
    (hA : ∀ i x, x ∈ (τ i).invariants → A i x ∈ (τ i).invariants)
    (hmap : ∀ x i, e (F x) i = A i (e x i)) :
    localFactor ρ F hF = ∏ i, localFactor (τ i) (A i) (hA i) := by
  simp only [localFactor, polynomial_product ρ τ e he F A hF hA hmap, map_prod,
    Finset.prod_inv_distrib]

end PaperXI.PolynomialAssembly
