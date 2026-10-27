module
public import KomorebiInformation.Foundations
public import Mathlib.LinearAlgebra.Basis.VectorSpace
public import Mathlib.LinearAlgebra.Quotient.Basic
public import Mathlib.LinearAlgebra.Isomorphisms
public import Mathlib.LinearAlgebra.Dimension.Finrank
@[expose] public section

namespace KomorebiInformation
namespace Linear
variable {K V O Y E C : Type*}
variable [DivisionRing K]
variable [AddCommGroup V] [Module K V]
variable [AddCommGroup O] [Module K O]
variable [AddCommGroup Y] [Module K Y]
variable [AddCommGroup E] [Module K E]
variable [AddCommGroup C] [Module K C]

/-- Equality on observation fibers is exactly the linear kernel criterion. -/
theorem sufficient_iff_kernel (R : V →ₗ[K] O) (F : V →ₗ[K] Y) :
    Sufficient R F ↔ R.ker ≤ F.ker := by
  constructor
  · intro h x hx
    change F x = 0
    have heq : R x = R 0 := by simpa using hx
    simpa using h x 0 heq
  · intro h x y hxy
    have hk : x-y ∈ R.ker := by
      change R (x-y) = 0
      rw [map_sub, hxy, sub_self]
    have hf : F (x-y) = 0 := h hk
    exact sub_eq_zero.mp (by simpa only [map_sub] using hf)

/-- Algebraic factorization is proved by quotienting the kernel and extending
from the image. No finite-dimensional assumption is required for existence. -/
theorem exists_linear_decoder_iff_kernel (R : V →ₗ[K] O) (F : V →ₗ[K] Y) :
    (∃ G : O →ₗ[K] Y, G.comp R = F) ↔ R.ker ≤ F.ker := by
  constructor
  · rintro ⟨G, hG⟩ x hx
    change F x = 0
    rw [← hG]
    change G (R x) = 0
    rw [show R x = 0 from hx, map_zero]
  · intro h
    let q := R.quotKerEquivRange
    let L := (R.ker.liftQ F h).comp q.symm.toLinearMap
    obtain ⟨G, hG⟩ := L.exists_extend
    refine ⟨G, ?_⟩
    ext x
    have hg := LinearMap.congr_fun hG (R.rangeRestrict x)
    change G (R x) = L (R.rangeRestrict x) at hg
    change G (R x) = F x
    rw [hg]
    have hx : R.rangeRestrict x = q (Submodule.Quotient.mk x) := by
      apply Subtype.ext
      simp [q]
    simp [L, hx]

/-- Feasibility criterion for a helper with explicitly restricted access. -/
theorem access_feasibility (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E) :
    (∃ G : O × E →ₗ[K] Y, G.comp (R.prod U) = F) ↔
      R.ker ⊓ U.ker ≤ F.ker := by
  rw [exists_linear_decoder_iff_kernel, LinearMap.ker_prod]

/-- Any nonlinear code is subject to the same feasibility condition. -/
theorem arbitrary_repair_implies_kernel
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    {Message : Type*} {h : E → Message} {g : O × Message → Y}
    (hr : Repair R F U h g) : R.ker ⊓ U.ker ≤ F.ker := by
  have hs : Sufficient (R.prod U) F := repair_implies_joint_sufficient hr
  simpa only [LinearMap.ker_prod] using (sufficient_iff_kernel (R.prod U) F).mp hs

/-- Linear decoder feasibility is equivalent to arbitrary exact decoding of
all accessible information, not just sufficient for it. -/
theorem access_sufficient_iff_kernel
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E) :
    Sufficient (fun x => (R x, U x)) F ↔ R.ker ⊓ U.ker ≤ F.ker := by
  simpa only [Sufficient, LinearMap.prod_apply, Function.prod_apply, LinearMap.ker_prod] using sufficient_iff_kernel (R.prod U) F

/-- A nonzero task value on the joint kernel refutes every permitted code. -/
theorem kernel_witness_rejects_repair
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    (v : V) (hr : R v = 0) (hu : U v = 0) (hf : F v ≠ 0)
    {Message : Type*} (h : E → Message) (g : O × Message → Y) :
    ¬ Repair R F U h g := by
  intro hrep
  exact hf (arbitrary_repair_implies_kernel R F U hrep ⟨hr, hu⟩)

/-- The failed kernel inclusion has a concrete vector witness. -/
theorem not_feasible_iff_witness
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E) :
    ¬ (R.ker ⊓ U.ker ≤ F.ker) ↔ ∃ v, R v = 0 ∧ U v = 0 ∧ F v ≠ 0 := by
  change (¬ ∀ v, (R v = 0 ∧ U v = 0) → F v = 0) ↔ _
  simp only [not_forall, exists_prop, and_assoc]

/-- Soundness of the exact H,G certificate from the Python interface. -/
theorem repair_certificate_sound
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (U : V →ₗ[K] E)
    (H : E →ₗ[K] C) (G : O × C →ₗ[K] Y)
    (hcert : G.comp (R.prod (H.comp U)) = F) : Repair R F U H G := by
  intro x
  exact LinearMap.congr_fun hcert x

/-- The missing answer directions, represented as a genuine subspace. -/
def ObstructionSpace (R : V →ₗ[K] O) (F : V →ₗ[K] Y) : Submodule K Y :=
  (F.domRestrict R.ker).range

/-- On a fiber x0 + ker R, task differences are exactly the obstruction space. -/
theorem fiber_task_difference_iff
    (R : V →ₗ[K] O) (F : V →ₗ[K] Y) (x0 : V) (y : Y) :
    (∃ x, R x = R x0 ∧ F x = y) ↔ y-F x0 ∈ ObstructionSpace R F := by
  constructor
  · rintro ⟨x, hr, hf⟩
    refine ⟨⟨x-x0, ?_⟩, ?_⟩
    · change R (x-x0) = 0
      rw [map_sub, hr, sub_self]
    · change F (x-x0) = y-F x0
      rw [map_sub, hf]
  · rintro ⟨v, hv⟩
    refine ⟨x0+v, ?_, ?_⟩
    · rw [map_add, show R v = 0 from v.property, add_zero]
    · change F v = y-F x0 at hv
      rw [map_add, hv, add_sub_cancel]
end Linear
end KomorebiInformation
