import PaperXI.FiniteProductDeterminant
import PaperXI.OddPhaseTransport
import PaperXI.OddSymplectic

/-! Finite-product laws for the actual determinant phases. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddPhaseSum
open scoped BigOperators Classical

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] {V : ι → Type*}
variable [∀ i, AddCommGroup (V i)] [∀ i, Module (ZMod p) (V i)]
variable [∀ i, FiniteDimensional (ZMod p) (V i)]

def action (g : ∀ i, V i ≃ₗ[ZMod p] V i) :
    (∀ i, V i) ≃ₗ[ZMod p] (∀ i, V i) := LinearEquiv.piCongrRight g

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
@[simp] theorem action_apply (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (x : ∀ i, V i) (i : ι) : action g x i = g i (x i) := rfl

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
theorem difference (g : ∀ i, V i ≃ₗ[ZMod p] V i) :
    OddPhase.difference (action g) =
      FiniteProductDeterminant.map (fun i => OddPhase.difference (g i)) := by
  apply LinearMap.ext
  intro x
  rfl

theorem determinant (g : ∀ i, V i ≃ₗ[ZMod p] V i) :
    (OddPhase.difference (action g)).det = ∏ i, (OddPhase.difference (g i)).det := by
  rw [difference, FiniteProductDeterminant.determinant]

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
theorem fixedPointFree (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (hg : ∀ i, OddPhase.FixedPointFree (g i)) : OddPhase.FixedPointFree (action g) := by
  intro x hx
  funext i
  exact hg i (x i) (congrFun hx i)

theorem half_dimension (h : ∀ i, Even (Module.finrank (ZMod p) (V i))) :
    Module.finrank (ZMod p) (∀ i, V i) / 2 =
      ∑ i, Module.finrank (ZMod p) (V i) / 2 := by
  rw [Module.finrank_pi_fintype]
  have he (i : ι) : Module.finrank (ZMod p) (V i) =
      2 * (Module.finrank (ZMod p) (V i) / 2) := by
    obtain ⟨n, hn⟩ := h i
    omega
  have hs : (∑ i, Module.finrank (ZMod p) (V i)) =
      2 * ∑ i, Module.finrank (ZMod p) (V i) / 2 := by
    calc
      _ = ∑ i, 2 * (Module.finrank (ZMod p) (V i) / 2) :=
        Finset.sum_congr rfl (fun i _ => he i)
      _ = _ := (Finset.mul_sum _ _ _).symm
  omega

theorem phase_product (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (h : ∀ i, Even (Module.finrank (ZMod p) (V i))) :
    OddPhase.phase (action g) = ∏ i, OddPhase.phase (g i) := by
  simp only [OddPhase.phase, determinant, half_dimension h, map_prod,
    Finset.prod_mul_distrib]
  rw [Finset.prod_pow_eq_pow_sum]

theorem phase_product_symplectic (hp : p ≠ 2)
    (b : ∀ i, LinearMap.BilinForm (ZMod p) (V i))
    (ha : ∀ i, (b i).IsAlt) (hn : ∀ i, (b i).Nondegenerate)
    (g : ∀ i, V i ≃ₗ[ZMod p] V i) :
    OddPhase.phase (action g) = ∏ i, OddPhase.phase (g i) :=
  phase_product g (fun i => OddSymplectic.even_finrank_zmod hp (b i) (ha i) (hn i))

variable {X : Type*} [AddCommGroup X] [Module (ZMod p) X]

/-- An actual decomposition equivalence intertwining the actions transports the product law. -/
theorem of_decomposition (hp : p ≠ 2)
    (b : ∀ i, LinearMap.BilinForm (ZMod p) (V i))
    (ha : ∀ i, (b i).IsAlt) (hn : ∀ i, (b i).Nondegenerate)
    (g : ∀ i, V i ≃ₗ[ZMod p] V i) (G : X ≃ₗ[ZMod p] X)
    (e : (∀ i, V i) ≃ₗ[ZMod p] X)
    (he : ∀ x, e (action g x) = G (e x)) :
    OddPhase.phase G = ∏ i, OddPhase.phase (g i) := by
  rw [← OddPhase.conjugacy (action g) G e he]
  exact phase_product_symplectic hp b ha hn g

omit [Fintype ι] [∀ i, FiniteDimensional (ZMod p) (V i)] in
theorem fixedPointFree_of_decomposition (g : ∀ i, V i ≃ₗ[ZMod p] V i)
    (hg : ∀ i, OddPhase.FixedPointFree (g i)) (G : X ≃ₗ[ZMod p] X)
    (e : (∀ i, V i) ≃ₗ[ZMod p] X)
    (he : ∀ x, e (action g x) = G (e x)) : OddPhase.FixedPointFree G := by
  exact (OddPhase.fixedPointFree_conjugacy (action g) G e he).mp (fixedPointFree g hg)

end PaperXI.OddPhaseSum
