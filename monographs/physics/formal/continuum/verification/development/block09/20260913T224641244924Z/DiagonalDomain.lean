module

public import KomorebiPhysics.CountableContinuity

/-!
A genuine Hilbert-space realization: arbitrary real diagonal multiplication
on its maximal weighted-l2 domain. Domain invariance, density, symmetry,
self-adjointness and graph-compatible coordinate resolution are proved.
The model is spectral; no differential-operator identification is assumed.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DiagonalDomain
open Filter
open scoped BigOperators Topology lp

variable {I : Type*} [DecidableEq I]
variable (eig : I → ℝ)

/-- Maximal multiplication domain, not just finitely supported vectors. -/
def domain : Submodule ℂ (ℓ²(I, ℂ)) where
  carrier := {x | Memℓp (fun i => (eig i : ℂ) * x i) 2}
  zero_mem' := by simpa using (zero_mem_ℓp' (E := fun _ : I => ℂ) (p := 2))
  add_mem' hx hy := by
    simpa only [lp.coeFn_add, Pi.add_apply, mul_add] using hx.add hy
  smul_mem' c x hx := by
    simpa only [lp.coeFn_smul, Pi.smul_apply, smul_eq_mul, mul_left_comm]
      using hx.const_smul c

/-- A partial linear operator with a genuinely weighted domain. -/
def operator : ℓ²(I, ℂ) →ₗ.[ℂ] ℓ²(I, ℂ) where
  domain := domain eig
  toFun := {
    toFun := fun x => ⟨fun i => (eig i : ℂ) * (x : ℓ²(I, ℂ)) i, x.property⟩
    map_add' := fun x y => lp.ext (funext fun i => mul_add (eig i : ℂ) _ _)
    map_smul' := fun c x => lp.ext (funext fun i => mul_left_comm (eig i : ℂ) c _) }

theorem operator_apply (x : (operator eig).domain) (i : I) :
    operator eig x i = (eig i : ℂ) * (x : ℓ²(I, ℂ)) i := rfl

/-- Multiplication of an actual coordinate singleton. -/
theorem weighted_single (i : I) (c : ℂ) :
    (fun j => (eig j : ℂ) * lp.single 2 i c j) =
      (fun j => (lp.single 2 i ((eig i : ℂ) * c) : ℓ²(I, ℂ)) j) := by
  funext j
  by_cases h : j = i
  · subst j; simp
  · simp [lp.single_apply_ne, h]

theorem single_mem (i : I) (c : ℂ) : lp.single 2 i c ∈ domain eig := by
  change Memℓp (fun j => (eig j : ℂ) * lp.single 2 i c j) 2
  rw [weighted_single]
  exact (lp.single 2 i ((eig i : ℂ) * c)).memℓp

def single (i : I) (c : ℂ) : (operator eig).domain :=
  ⟨lp.single 2 i c, single_mem eig i c⟩

theorem single_coe (i : I) (c : ℂ) :
    (single eig i c : ℓ²(I, ℂ)) = lp.single 2 i c := rfl

theorem operator_single (i : I) (c : ℂ) :
    operator eig (single eig i c) = lp.single 2 i ((eig i : ℂ) * c) :=
  lp.ext (weighted_single eig i c)

/-- Actual bounded coordinate projections on the infinite Hilbert sum. -/
def coordinate (i : I) : ℓ²(I, ℂ) →L[ℂ] ℓ²(I, ℂ) :=
  (lp.singleContinuousLinearMap ℂ (fun _ : I => ℂ) 2 i).comp
    (lp.evalCLM ℂ (fun _ : I => ℂ) 2 i)

theorem coordinate_apply (i : I) (x : ℓ²(I, ℂ)) :
    coordinate i x = lp.single 2 i (x i) := rfl

def coordinateAtlas : StrongAtlas (ℓ²(I, ℂ)) I where
  proj := coordinate
  idempotent i x := by simp [coordinate_apply]
  orthogonal i j hij x := by simp [coordinate_apply, hij]
  selfAdjoint i x y := by
    simp only [coordinate_apply, lp.inner_single_left, lp.inner_single_right]
  strong x := lp.hasSum_single (by norm_num) x

/-- The diagonal domain is explicitly preserved by every coordinate projector. -/
def atlas : DomainAtlas (operator eig) I where
  atlas := coordinateAtlas
  preserves i x := single_mem eig i ((x : ℓ²(I, ℂ)) i)

theorem action_project (i : I) (x : (operator eig).domain) :
    operator eig ((atlas eig).project i x) = coordinate i (operator eig x) := by
  exact lp.ext (weighted_single eig i ((x : ℓ²(I, ℂ)) i))

/-- Full graph compatibility for every vector in the maximal weighted domain,
not merely eventual exactness on finite-support states. -/
theorem graph_compatible : (atlas eig).GraphCompatible := by
  apply (atlas eig).graph_iff_action.mpr
  intro x
  have h := coordinateAtlas.strong (operator eig x)
  simpa only [action_project] using h

theorem symmetric : GraphDomain.IsSymmetric (operator eig) := by
  intro x y
  rw [lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro i
  simp only [operator_apply, RCLike.inner_apply, map_mul, Complex.conj_ofReal]
  ring

/-- Coordinate approximations prove density of the full weighted domain. -/
theorem dense_domain : Dense ((operator eig).domain : Set (ℓ²(I, ℂ))) := by
  intro x
  apply mem_closure_of_tendsto (coordinateAtlas.partial_tendsto x)
  apply Filter.Eventually.of_forall
  intro s
  exact (domain eig).sum_mem (fun i _ => single_mem eig i (x i))

/-- Adjoint coordinates are determined by testing actual domain singletons. -/
theorem adjoint_apply_coordinate (y : (operator eig).adjoint.domain) (i : I) :
    (operator eig).adjoint y i = (eig i : ℂ) * (y : ℓ²(I, ℂ)) i := by
  have h := (LinearPMap.adjoint_isFormalAdjoint (dense_domain eig)).symm (single eig i 1) y
  rw [operator_single, single_coe, lp.inner_single_left, lp.inner_single_left] at h
  simpa only [mul_one, RCLike.inner_apply, map_one, mul_one, Complex.conj_ofReal,
    mul_comm] using h.symm

/-- The adjoint has no vectors outside the declared maximal weighted domain. -/
theorem adjoint_domain_le : (operator eig).adjoint.domain ≤ (operator eig).domain := by
  intro y hy
  have h := ((operator eig).adjoint ⟨y, hy⟩).memℓp
  simpa only [adjoint_apply_coordinate] using h

/-- Actual equality to the unbounded adjoint, stronger than formal symmetry. -/
theorem selfAdjoint : IsSelfAdjoint (operator eig) := by
  rw [LinearPMap.isSelfAdjoint_def]
  apply le_antisymm
  · refine ⟨adjoint_domain_le eig, ?_⟩
    intro x y hxy
    apply lp.ext
    funext i
    rw [adjoint_apply_coordinate, operator_apply, hxy]
  · exact LinearPMap.IsFormalAdjoint.le_adjoint (dense_domain eig) (symmetric eig)

theorem closed : (operator eig).IsClosed := (selfAdjoint eig).isClosed

end DiagonalDomain
end KomorebiPhysics
