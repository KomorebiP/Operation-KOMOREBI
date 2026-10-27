import PaperX.MonodromyReconstruction
import PaperX.WeilEuler

/-! Local fixed kernels and Euler polynomials are preserved by twisting supplied data. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionLocal
open PaperX.WeilData PaperX.MonodromyReconstruction PaperX.WeilEuler
variable {K G V : Type*} [Field K] [CharZero K] [Group G]
variable {ν : G →* Kˣ} [AddCommGroup V] [Module K V]

def localEquiv (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G) :
    fixedKernel (twist D t) H ≃ₗ[K] fixedKernel D H where
  toFun x := ⟨x.val, by rw [← twist_fixedKernel D t H]; exact x.property⟩
  invFun x := ⟨x.val, by rw [twist_fixedKernel D t H]; exact x.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem local_equivariant (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G)
    [H.Normal] (g : G) (x : fixedKernel (twist D t) H) :
    localEquiv D t H (fixedRep (twist D t) H g x) =
      fixedRep D H g (localEquiv D t H x) := by
  apply Subtype.ext
  exact reconstruct_on_kernel D t g x.property.1

theorem local_conjugate (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G)
    [H.Normal] (g : G) :
    (localEquiv D t H).conj (fixedRep (twist D t) H g) = fixedRep D H g := by
  ext x
  exact reconstruct_on_kernel D t g x.property.1

variable [FiniteDimensional K V]

theorem twist_localCharpoly (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G)
    [H.Normal] (φ : G) : localCharpoly (twist D t) H φ = localCharpoly D H φ := by
  unfold localCharpoly
  rw [← LinearEquiv.charpoly_conj (localEquiv D t H), local_conjugate]

theorem twist_euler (D : Datum ν V) (t : TwistedCocycle ν) (H : Subgroup G)
    [H.Normal] (φ : G) : eulerPolynomial (twist D t) H φ = eulerPolynomial D H φ := by
  unfold eulerPolynomial
  rw [twist_localCharpoly]

end PaperX.ReconstructionLocal
