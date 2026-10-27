import PaperX.MonodromyKernels
import Mathlib.RepresentationTheory.Invariants

/-! Group actions with monodromy, an explicit norm character, and actual
inertia-fixed kernels. Arithmetic identification of G and H is separate. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilData
variable {K G : Type*} [Field K] [Group G]
variable (ν : G →* Kˣ)

structure Datum (V : Type*) [AddCommGroup V] [Module K V] where
  r : Representation K G V
  N : Module.End K V
  nilpotent : IsNilpotent N
  relation : ∀ g x, r g (N x) = (ν g : K) • N (r g x)

variable {ν} {V : Type*} [AddCommGroup V] [Module K V]

def actionEquiv (ρ : Representation K G V) (g : G) : V ≃ₗ[K] V where
  toFun := ρ g
  invFun := ρ g⁻¹
  left_inv x := by simp [← Module.End.mul_apply, ← map_mul]
  right_inv x := by simp [← Module.End.mul_apply, ← map_mul]
  map_add' := (ρ g).map_add
  map_smul' := (ρ g).map_smul

def toMonodromy (D : Datum ν V) (g : G) : PaperX.MonodromyData.Datum (ν g) V where
  F := actionEquiv D.r g
  N := D.N
  nilpotent := D.nilpotent
  relation := D.relation g

def inertiaFixed (H : Subgroup G) (ρ : Representation K G V) : Submodule K V :=
  Representation.invariants (ρ.comp H.subtype)

def fixedKernel (D : Datum ν V) (H : Subgroup G) : Submodule K V :=
  LinearMap.ker D.N ⊓ inertiaFixed H D.r

@[simp] theorem mem_fixedKernel (D : Datum ν V) (H : Subgroup G) (x : V) :
    x ∈ fixedKernel D H ↔ D.N x = 0 ∧ ∀ h : H, D.r h x = x := Iff.rfl

theorem inertia_N_commutes (D : Datum ν V) (H : Subgroup G)
    (hν : ∀ h : H, ν h = 1) (h : H) (x : V) : D.r h (D.N x) = D.N (D.r h x) := by
  simpa [hν h] using D.relation h x

theorem kernel_stable (D : Datum ν V) (g : G) {x : V} (hx : D.N x = 0) :
    D.N (D.r g x) = 0 := by
  have h := D.relation g x
  rw [hx, map_zero] at h
  exact (smul_eq_zero.mp h.symm).resolve_left (Units.ne_zero (ν g))

theorem inertia_stable (ρ : Representation K G V) (H : Subgroup G) [H.Normal]
    (g : G) {x : V} (hx : x ∈ inertiaFixed H ρ) : ρ g x ∈ inertiaFixed H ρ := by
  intro h
  have hh : g⁻¹ * (h : G) * g ∈ H := by
    simpa using (inferInstance : H.Normal).conj_mem (h : G) h.property g⁻¹
  have he := hx (⟨g⁻¹ * (h : G) * g, hh⟩ : H)
  calc
    ρ h (ρ g x) = ρ g (ρ (g⁻¹ * (h : G) * g) x) := by
      simp [← Module.End.mul_apply, ← map_mul, mul_assoc]
    _ = ρ g x := congrArg (ρ g) he

theorem fixedKernel_stable (D : Datum ν V) (H : Subgroup G) [H.Normal]
    (g : G) {x : V} (hx : x ∈ fixedKernel D H) : D.r g x ∈ fixedKernel D H :=
  ⟨kernel_stable D g hx.1, inertia_stable D.r H g hx.2⟩

/-- The restriction is an actual representation on the independently defined subspace. -/
def fixedRep (D : Datum ν V) (H : Subgroup G) [H.Normal] :
    Representation K G (fixedKernel D H) where
  toFun g :=
    { toFun := fun x => ⟨D.r g x.val, fixedKernel_stable D H g x.property⟩
      map_add' := by intros; apply Subtype.ext; simp
      map_smul' := by intros; apply Subtype.ext; simp }
  map_one' := by ext x; simp
  map_mul' g h := by ext x; simp

@[simp] theorem fixedRep_val (D : Datum ν V) (H : Subgroup G) [H.Normal]
    (g : G) (x : fixedKernel D H) : (fixedRep D H g x).val = D.r g x.val := rfl

def fixedF (D : Datum ν V) (H : Subgroup G) [H.Normal] (φ : G) :
    fixedKernel D H ≃ₗ[K] fixedKernel D H := actionEquiv (fixedRep D H) φ

def localCharpoly [FiniteDimensional K V] (D : Datum ν V) (H : Subgroup G)
    [H.Normal] (φ : G) : Polynomial K := (fixedRep D H φ).charpoly

/-- Changing a Frobenius lift by an inertia element leaves its restricted action equal. -/
theorem lift_independent (D : Datum ν V) (H : Subgroup G) [H.Normal]
    (φ : G) (h : H) : fixedRep D H (φ * h) = fixedRep D H φ := by
  ext x
  change D.r (φ * h) x.val = D.r φ x.val
  rw [map_mul, Module.End.mul_apply]
  exact congrArg (D.r φ) (x.property.2 h)

theorem localCharpoly_lift_independent [FiniteDimensional K V]
    (D : Datum ν V) (H : Subgroup G) [H.Normal] (φ : G) (h : H) :
    localCharpoly D H (φ * h) = localCharpoly D H φ := by
  unfold localCharpoly
  rw [lift_independent]

/-- Trivial inertia recovers the earlier monodromy kernel exactly. -/
theorem fixedKernel_eq_kernel (D : Datum ν V) (H : Subgroup G)
    (hr : ∀ h : H, D.r h = 1) : fixedKernel D H = LinearMap.ker D.N := by
  ext x
  simp [mem_fixedKernel, hr]

end PaperX.WeilData
