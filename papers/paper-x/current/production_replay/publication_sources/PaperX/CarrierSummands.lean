import Mathlib.RepresentationTheory.Basic
import Mathlib.LinearAlgebra.Pi

/-! Explicit summands of a supplied constituent-copy carrier. No arithmetic
compatibility or decomposition of an unknown carrier is assumed implicitly. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CarrierSummands

variable {R G I : Type*} [CommRing R] [Monoid G]
variable {V : I → Type*} [∀ i, AddCommGroup (V i)] [∀ i, Module R (V i)]

abbrev Copies (V : I → Type*) (m : I → ℕ) := (i : I) → Fin (m i) → V i

/-- The actual componentwise representation on the selected copies. -/
def copiesRep (ρ : ∀ i, Representation R G (V i)) (m : I → ℕ) :
    Representation R G (Copies V m) where
  toFun g :=
    { toFun := fun x i k => ρ i g (x i k)
      map_add' := by intros; ext i k; simp
      map_smul' := by intros; ext i k; simp }
  map_one' := by ext x i k; simp
  map_mul' g h := by ext x i k; simp

@[simp] theorem copiesRep_apply (ρ : ∀ i, Representation R G (V i))
    (m : I → ℕ) (g : G) (x : Copies V m) (i : I) (k : Fin (m i)) :
    copiesRep ρ m g x i k = ρ i g (x i k) := rfl

/-- Extend by zero in the remaining copies. -/
def inclusion {m c : I → ℕ} (_h : ∀ i, m i ≤ c i) :
    Copies V m →ₗ[R] Copies V c where
  toFun x i k := if hk : k.val < m i then x i ⟨k.val, hk⟩ else 0
  map_add' := by intros; ext i k; dsimp; split <;> simp
  map_smul' := by intros; ext i k; dsimp; split <;> simp

/-- Restrict to the first selected copies. -/
def retraction {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Copies V c →ₗ[R] Copies V m where
  toFun x i k := x i ⟨k.val, lt_of_lt_of_le k.isLt (h i)⟩
  map_add' := by intros; rfl
  map_smul' := by intros; rfl

@[simp] theorem retraction_inclusion {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (x : Copies V m) : retraction (R := R) h (inclusion (R := R) h x) = x := by
  ext i k
  simp [retraction, inclusion, k.isLt]

theorem split_law {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    (retraction (R := R) h (V := V)).comp (inclusion (R := R) h) = LinearMap.id := by
  ext x : 1
  exact retraction_inclusion (R := R) h x

theorem inclusion_injective {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Function.Injective (inclusion (R := R) h (V := V)) := by
  exact Function.LeftInverse.injective (retraction_inclusion (R := R) h)

theorem retraction_surjective {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Function.Surjective (retraction (R := R) h (V := V)) := by
  intro x
  exact ⟨inclusion (R := R) h x, retraction_inclusion (R := R) h x⟩

theorem inclusion_equivariant (ρ : ∀ i, Representation R G (V i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) (x : Copies V m) :
    inclusion (R := R) h (copiesRep ρ m g x) = copiesRep ρ c g (inclusion (R := R) h x) := by
  ext i k
  dsimp [inclusion]
  split <;> simp

theorem retraction_equivariant (ρ : ∀ i, Representation R G (V i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) (x : Copies V c) :
    retraction (R := R) h (copiesRep ρ c g x) = copiesRep ρ m g (retraction (R := R) h x) := rfl

/-- The image is characterized by its unused coordinates, independently of maps. -/
def Supported (m c : I → ℕ) (x : Copies V c) : Prop :=
  ∀ i (k : Fin (c i)), m i ≤ k.val → x i k = 0

theorem range_inclusion_iff {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (x : Copies V c) :
    x ∈ LinearMap.range (inclusion (R := R) h) ↔ Supported m c x := by
  constructor
  · rintro ⟨y, rfl⟩ i k hk
    simp [inclusion, not_lt.mpr hk]
  · intro hx
    refine ⟨retraction (R := R) h x, ?_⟩
    ext i k
    dsimp [inclusion, retraction]
    split
    · rfl
    · rename_i hk
      exact (hx i k (le_of_not_gt hk)).symm

def projector {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    Module.End R (Copies V c) := (inclusion (R := R) h).comp (retraction (R := R) h)

theorem projector_idempotent {m c : I → ℕ} (h : ∀ i, m i ≤ c i) :
    (projector (R := R) h (V := V)).comp (projector (R := R) h) = projector (R := R) h := by
  ext x : 1
  exact congrArg (inclusion (R := R) h) (retraction_inclusion (R := R) h (retraction (R := R) h x))

theorem projector_equivariant (ρ : ∀ i, Representation R G (V i))
    {m c : I → ℕ} (h : ∀ i, m i ≤ c i) (g : G) :
    (projector (R := R) h).comp (copiesRep ρ c g) = (copiesRep ρ c g).comp (projector (R := R) h) := by
  ext x : 1
  exact inclusion_equivariant ρ h g (retraction (R := R) h x)

theorem projector_fixed_iff {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (x : Copies V c) : projector (R := R) h x = x ↔ Supported m c x := by
  rw [← range_inclusion_iff (R := R) h x]
  constructor
  · intro hx; exact ⟨retraction (R := R) h x, hx⟩
  · rintro ⟨y, rfl⟩
    exact congrArg (inclusion (R := R) h) (retraction_inclusion (R := R) h y)

variable {W : Type*} [AddCommGroup W] [Module R W]

/-- Transport into an original carrier using a supplied decomposition. -/
def transportedInclusion {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (D : W ≃ₗ[R] Copies V c) : Copies V m →ₗ[R] W :=
  D.symm.toLinearMap.comp (inclusion (R := R) h)

def transportedRetraction {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (D : W ≃ₗ[R] Copies V c) : W →ₗ[R] Copies V m :=
  (retraction (R := R) h).comp D.toLinearMap

theorem transported_split {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (D : W ≃ₗ[R] Copies V c) (x : Copies V m) :
    transportedRetraction h D (transportedInclusion h D x) = x := by
  simp [transportedRetraction, transportedInclusion]

theorem transported_inclusion_equivariant (ρ : ∀ i, Representation R G (V i))
    (σ : Representation R G W) {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (D : W ≃ₗ[R] Copies V c)
    (hD : ∀ g x, D (σ g x) = copiesRep ρ c g (D x)) (g : G) (x : Copies V m) :
    transportedInclusion h D (copiesRep ρ m g x) = σ g (transportedInclusion h D x) := by
  apply D.injective
  simp only [transportedInclusion, LinearMap.comp_apply, LinearEquiv.coe_coe,
    LinearEquiv.apply_symm_apply, hD]
  exact inclusion_equivariant ρ h g x

theorem transported_retraction_equivariant (ρ : ∀ i, Representation R G (V i))
    (σ : Representation R G W) {m c : I → ℕ} (h : ∀ i, m i ≤ c i)
    (D : W ≃ₗ[R] Copies V c)
    (hD : ∀ g x, D (σ g x) = copiesRep ρ c g (D x)) (g : G) (x : W) :
    transportedRetraction h D (σ g x) = copiesRep ρ m g (transportedRetraction h D x) := by
  change retraction (R := R) h (D (σ g x)) = _
  rw [hD]
  exact retraction_equivariant ρ h g (D x)

end PaperX.CarrierSummands
