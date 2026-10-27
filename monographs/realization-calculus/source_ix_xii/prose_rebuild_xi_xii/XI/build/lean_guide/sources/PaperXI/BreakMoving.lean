import PaperXI.MovingPhase
import PaperXI.OrthogonalPhase

/-! Actual finite-family moving spaces. The maps below use the image of the
actual difference, not an independently supplied vector space of the same size. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.BreakMoving
open FixedMoving
open scoped BigOperators Classical

variable {K ι : Type*} [Field K] {V : ι → Type*}
variable [∀ i, AddCommGroup (V i)] [∀ i, Module K (V i)]

/-- The moving image of the componentwise action is the product of the actual
component moving images. Its inverse assembles witnesses for each difference. -/
def productEquiv (g : ∀ i, V i ≃ₗ[K] V i) :
    moving (LinearEquiv.piCongrRight g) ≃ₗ[K] (∀ i, moving (g i)) where
  toFun x i := ⟨x.val i, by
    obtain ⟨y, hy⟩ := x.property
    exact ⟨y i, congrFun hy i⟩⟩
  invFun x := ⟨fun i => (x i).val, by
    choose y hy using fun i => (mem_moving (g i) (x i)).mp (x i).property
    exact ⟨y, funext hy⟩⟩
  left_inv x := by apply Subtype.ext; rfl
  right_inv x := by funext i; apply Subtype.ext; rfl
  map_add' x y := by funext i; apply Subtype.ext; rfl
  map_smul' c x := by funext i; apply Subtype.ext; rfl

@[simp] theorem productEquiv_coe (g : ∀ i, V i ≃ₗ[K] V i)
    (x : moving (LinearEquiv.piCongrRight g)) (i : ι) :
    (productEquiv g x i : V i) = x.val i := rfl

@[simp] theorem productEquiv_symm_coe (g : ∀ i, V i ≃ₗ[K] V i)
    (x : ∀ i, moving (g i)) (i : ι) :
    ((productEquiv g).symm x).val i = (x i : V i) := rfl

/-- This comparison intertwines the actual restricted moving actions. -/
theorem productEquiv_intertwines (g : ∀ i, V i ≃ₗ[K] V i)
    (x : moving (LinearEquiv.piCongrRight g)) :
    productEquiv g (movingAction (LinearEquiv.piCongrRight g) x) =
      LinearEquiv.piCongrRight (fun i => movingAction (g i)) (productEquiv g x) := by
  funext i
  apply Subtype.ext
  rfl

variable {X : Type*} [AddCommGroup X] [Module K X]

/-- An actual ambient decomposition gives the moving decomposition by
restriction followed by the proved product-image comparison. -/
def equiv (G : X ≃ₗ[K] X) (g : ∀ i, V i ≃ₗ[K] V i)
    (e : X ≃ₗ[K] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x)) :
    moving G ≃ₗ[K] (∀ i, moving (g i)) :=
  (movingEquiv G (LinearEquiv.piCongrRight g) e he).trans (productEquiv g)

@[simp] theorem equiv_coe (G : X ≃ₗ[K] X) (g : ∀ i, V i ≃ₗ[K] V i)
    (e : X ≃ₗ[K] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (x : moving G) (i : ι) : (equiv G g e he x i : V i) = e x i := rfl

theorem equiv_intertwines (G : X ≃ₗ[K] X) (g : ∀ i, V i ≃ₗ[K] V i)
    (e : X ≃ₗ[K] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x)) (x : moving G) :
    equiv G g e he (movingAction G x) =
      LinearEquiv.piCongrRight (fun i => movingAction (g i)) (equiv G g e he x) := by
  funext i
  apply Subtype.ext
  exact congrFun (he x) i

/-- Orthogonal form preservation restricts to the actual moving images. -/
theorem equiv_preserves [Fintype ι]
    (G : X ≃ₗ[K] X) (g : ∀ i, V i ≃ₗ[K] V i)
    (e : X ≃ₗ[K] (∀ i, V i))
    (he : ∀ x, e (G x) = LinearEquiv.piCongrRight g (e x))
    (b : LinearMap.BilinForm K X) (bs : ∀ i, LinearMap.BilinForm K (V i))
    (hb : ∀ x y, b x y = ∑ i, bs i (e x i) (e y i)) (x y : moving G) :
    movingForm G b x y =
      ∑ i, movingForm (g i) (bs i) (equiv G g e he x i) (equiv G g e he y i) :=
  hb x y

section PrimeField
variable {p : ℕ} [Fact p.Prime]
variable {Y : Type*} [AddCommGroup Y] [Module (ZMod p) Y]
variable [FiniteDimensional (ZMod p) Y]

/-- In finite dimension, the source's exact fixed-point-free moving condition
already implies the fixed/moving complement. No order assumption is added. -/
theorem isCompl_of_moving_fixedPointFree (G : Y ≃ₗ[ZMod p] Y)
    (hf : OddPhase.FixedPointFree (movingAction G)) : IsCompl (fixed G) (moving G) := by
  constructor
  · apply disjoint_iff.mpr
    apply bot_unique
    intro x hx
    change x = 0
    have hx' : movingAction G ⟨x, hx.2⟩ = ⟨x, hx.2⟩ := by
      apply Subtype.ext
      exact (mem_fixed G x).mp hx.1
    exact congrArg Subtype.val (hf ⟨x, hx.2⟩ hx')
  · apply Submodule.codisjoint_iff_exists_add_eq.mpr
    intro x
    let dx : moving G := ⟨G x - x, ⟨x, rfl⟩⟩
    obtain ⟨y, hy⟩ := ((OddPhase.fixedPointFree_iff_bijective (movingAction G)).mp hf).2 dx
    have hy' : G (y : Y) - (y : Y) = G x - x := congrArg Subtype.val hy
    refine ⟨x - (y : Y), (y : Y), ?_, y.property, sub_add_cancel x (y : Y)⟩
    rw [mem_fixed, map_sub]
    exact sub_eq_sub_iff_sub_eq_sub.mp hy'.symm

theorem movingForm_nondegenerate (G : Y ≃ₗ[ZMod p] Y)
    (hf : OddPhase.FixedPointFree (movingAction G))
    (b : LinearMap.BilinForm (ZMod p) Y) (ha : b.IsAlt) (hn : b.Nondegenerate)
    (hb : ∀ x y, b (G x) (G y) = b x y) : (movingForm G b).Nondegenerate :=
  movingForm_nondegenerate_of_isCompl G b ha hn hb (isCompl_of_moving_fixedPointFree G hf)

end PrimeField
end PaperXI.BreakMoving
