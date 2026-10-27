import Mathlib.Algebra.Algebra.Hom
import Mathlib.Algebra.Algebra.Tower
import Mathlib.Algebra.Module.RingHom
import Mathlib.LinearAlgebra.BilinearMap
import Mathlib.RingTheory.SimpleModule.Basic
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic

/-! An algebra action gives an actual module on a separate copy of its vector space.
Submodules and intertwiners are identified with the corresponding complex-linear data. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AlgebraActionModule

variable {B W : Type*} [Ring B] [Algebra ℂ B] [AddCommGroup W] [Module ℂ W]

/-- A copy of the original space carrying the module structure specified by the action. -/
@[nolint unusedArguments]
def Space (_ : B →ₐ[ℂ] Module.End ℂ W) := W
  deriving AddCommGroup, Module ℂ

variable (φ : B →ₐ[ℂ] Module.End ℂ W)

/-- The canonical complex linear identification with the original vector space. -/
def equiv : Space φ ≃ₗ[ℂ] W := LinearEquiv.refl ℂ W

instance instModule : Module B (Space φ) := Module.compHom W φ.toRingHom

@[simp] theorem equiv_smul (b : B) (w : Space φ) :
    equiv φ (b • w) = φ b (equiv φ w) := rfl

@[simp] theorem equiv_symm_apply (w : W) : equiv φ ((equiv φ).symm w) = w := rfl

instance instScalarTower : IsScalarTower ℂ B (Space φ) where
  smul_assoc c b w := by
    change φ (c • b) w = c • φ b w
    rw [map_smul]
    rfl

/-- Stability under every actual algebra operator. -/
def Stable (S : Submodule ℂ W) : Prop :=
  ∀ (b : B) (w : W), w ∈ S → φ b w ∈ S

/-- Restrict an actual module subspace to the compatible complex scalar action. -/
def toSubspace (S : Submodule B (Space φ)) : Submodule ℂ W := S.restrictScalars ℂ

@[simp] theorem mem_toSubspace (S : Submodule B (Space φ)) (w : W) :
    w ∈ toSubspace φ S ↔ (equiv φ).symm w ∈ S := Iff.rfl

theorem stable_toSubspace (S : Submodule B (Space φ)) : Stable φ (toSubspace φ S) := by
  intro b w hw
  exact S.smul_mem b hw

/-- Every stable complex subspace is an actual algebra submodule. -/
def ofSubspace (S : Submodule ℂ W) (hS : Stable φ S) : Submodule B (Space φ) where
  carrier := (S : Set W)
  zero_mem' := S.zero_mem
  add_mem' := S.add_mem
  smul_mem' := hS

@[simp] theorem mem_ofSubspace (S : Submodule ℂ W) (hS : Stable φ S) (w : Space φ) :
    w ∈ ofSubspace φ S hS ↔ equiv φ w ∈ S := Iff.rfl

@[simp] theorem toSubspace_ofSubspace (S : Submodule ℂ W) (hS : Stable φ S) :
    toSubspace φ (ofSubspace φ S hS) = S := by ext w; rfl

@[simp] theorem ofSubspace_toSubspace (S : Submodule B (Space φ)) :
    ofSubspace φ (toSubspace φ S) (stable_toSubspace φ S) = S := by ext w; rfl

/-- The complete ordered collection of module subspaces is exactly the stable complex subspaces. -/
def submoduleOrderIso : Submodule B (Space φ) ≃o {S : Submodule ℂ W // Stable φ S} where
  toFun S := ⟨toSubspace φ S, stable_toSubspace φ S⟩
  invFun S := ofSubspace φ S.1 S.2
  left_inv := ofSubspace_toSubspace φ
  right_inv S := by apply Subtype.ext; exact toSubspace_ofSubspace φ S.1 S.2
  map_rel_iff' := Iff.rfl

@[simp] theorem toSubspace_bot : toSubspace φ ⊥ = ⊥ := by ext w; rfl
@[simp] theorem toSubspace_top : toSubspace φ ⊤ = ⊤ := by ext w; rfl

/-- Simplicity is exactly nontriviality and absence of proper stable complex subspaces. -/
theorem simple_iff : IsSimpleModule B (Space φ) ↔
    Nontrivial W ∧ ∀ S : Submodule ℂ W, Stable φ S → S = ⊥ ∨ S = ⊤ := by
  constructor
  · intro h
    let : IsSimpleModule B (Space φ) := h
    refine ⟨IsSimpleModule.nontrivial B (Space φ), ?_⟩
    intro S hS
    have hh := eq_bot_or_eq_top (ofSubspace φ S hS)
    rcases hh with hh | hh
    · left
      have := congrArg (toSubspace φ) hh
      simpa using this
    · right
      have := congrArg (toSubspace φ) hh
      simpa using this
  · rintro ⟨hn, hs⟩
    let : Nontrivial W := hn
    let : Nontrivial (Space φ) := hn
    refine { eq_bot_or_eq_top := ?_ }
    intro S
    rcases hs (toSubspace φ S) (stable_toSubspace φ S) with h | h
    · left
      ext w
      have hh := congrArg (fun P : Submodule ℂ W => equiv φ w ∈ P) h
      simpa using hh
    · right
      ext w
      have hh := congrArg (fun P : Submodule ℂ W => equiv φ w ∈ P) h
      simpa using hh

section Intertwiners

variable {V U : Type*} [AddCommGroup V] [Module ℂ V]
variable [AddCommGroup U] [Module ℂ U]
variable (χ : B →ₐ[ℂ] Module.End ℂ V)

/-- The original complex-linear map commutes with the two actual algebra actions. -/
def Intertwines (f : W →ₗ[ℂ] V) : Prop :=
  ∀ (b : B) (w : W), f (φ b w) = χ b (f w)

/-- An action-preserving complex-linear map is an actual module-linear map. -/
def toModuleMap (f : W →ₗ[ℂ] V) (hf : Intertwines φ χ f) :
    Space φ →ₗ[B] Space χ where
  toFun := f
  map_add' := f.map_add
  map_smul' := hf

/-- Restriction of an actual module map to the original complex vector spaces. -/
def toComplexMap (f : Space φ →ₗ[B] Space χ) : W →ₗ[ℂ] V :=
  f.restrictScalars ℂ

@[simp] theorem toModuleMap_apply (f : W →ₗ[ℂ] V) (hf : Intertwines φ χ f)
    (w : Space φ) : equiv χ (toModuleMap φ χ f hf w) = f (equiv φ w) := rfl

@[simp] theorem toComplexMap_apply (f : Space φ →ₗ[B] Space χ) (w : W) :
    toComplexMap φ χ f w = equiv χ (f ((equiv φ).symm w)) := rfl

theorem intertwines_toComplexMap (f : Space φ →ₗ[B] Space χ) :
    Intertwines φ χ (toComplexMap φ χ f) := f.map_smul

/-- All complex action intertwiners correspond bijectively to actual module maps. -/
def intertwinerEquiv : {f : W →ₗ[ℂ] V // Intertwines φ χ f} ≃
    (Space φ →ₗ[B] Space χ) where
  toFun f := toModuleMap φ χ f.1 f.2
  invFun f := ⟨toComplexMap φ χ f, intertwines_toComplexMap φ χ f⟩
  left_inv f := by apply Subtype.ext; ext w; rfl
  right_inv f := by ext w; rfl

@[simp] theorem toComplexMap_toModuleMap (f : W →ₗ[ℂ] V) (hf : Intertwines φ χ f) :
    toComplexMap φ χ (toModuleMap φ χ f hf) = f := by ext w; rfl

@[simp] theorem toModuleMap_toComplexMap (f : Space φ →ₗ[B] Space χ) :
    toModuleMap φ χ (toComplexMap φ χ f) (intertwines_toComplexMap φ χ f) = f := by
  ext w
  rfl

/-- The correspondence preserves identity maps. -/
@[simp] theorem toComplexMap_id :
    toComplexMap φ φ (LinearMap.id : Space φ →ₗ[B] Space φ) = LinearMap.id := by
  ext w
  rfl

/-- The correspondence preserves composition. -/
@[simp] theorem toComplexMap_comp (θ : B →ₐ[ℂ] Module.End ℂ U)
    (g : Space χ →ₗ[B] Space θ) (f : Space φ →ₗ[B] Space χ) :
    toComplexMap φ θ (g.comp f) =
      (toComplexMap χ θ g).comp (toComplexMap φ χ f) := by
  ext w
  rfl

/-- An invertible complex intertwiner gives an actual module equivalence. -/
def toModuleEquiv (e : W ≃ₗ[ℂ] V) (he : Intertwines φ χ e.toLinearMap) :
    Space φ ≃ₗ[B] Space χ where
  toFun := e
  invFun := e.symm
  left_inv := e.left_inv
  right_inv := e.right_inv
  map_add' := e.map_add
  map_smul' := he

/-- A module equivalence gives an invertible intertwiner on the original spaces. -/
def toComplexEquiv (e : Space φ ≃ₗ[B] Space χ) : W ≃ₗ[ℂ] V :=
  e.restrictScalars ℂ

@[simp] theorem toModuleEquiv_apply (e : W ≃ₗ[ℂ] V)
    (he : Intertwines φ χ e.toLinearMap) (w : Space φ) :
    equiv χ (toModuleEquiv φ χ e he w) = e (equiv φ w) := rfl

@[simp] theorem toComplexEquiv_apply (e : Space φ ≃ₗ[B] Space χ) (w : W) :
    toComplexEquiv φ χ e w = equiv χ (e ((equiv φ).symm w)) := rfl

theorem intertwines_toComplexEquiv (e : Space φ ≃ₗ[B] Space χ) :
    Intertwines φ χ (toComplexEquiv φ χ e).toLinearMap := e.map_smul

/-- Invertible intertwiners correspond bijectively to actual module equivalences. -/
def equivalenceEquiv : {e : W ≃ₗ[ℂ] V // Intertwines φ χ e.toLinearMap} ≃
    (Space φ ≃ₗ[B] Space χ) where
  toFun e := toModuleEquiv φ χ e.1 e.2
  invFun e := ⟨toComplexEquiv φ χ e, intertwines_toComplexEquiv φ χ e⟩
  left_inv e := by apply Subtype.ext; ext w; rfl
  right_inv e := by ext w; rfl

@[simp] theorem toComplexEquiv_toModuleEquiv (e : W ≃ₗ[ℂ] V)
    (he : Intertwines φ χ e.toLinearMap) :
    toComplexEquiv φ χ (toModuleEquiv φ χ e he) = e := by ext w; rfl

@[simp] theorem toModuleEquiv_toComplexEquiv (e : Space φ ≃ₗ[B] Space χ) :
    toModuleEquiv φ χ (toComplexEquiv φ χ e) (intertwines_toComplexEquiv φ χ e) = e := by
  ext w
  rfl

@[simp] theorem toComplexEquiv_refl :
    toComplexEquiv φ φ (LinearEquiv.refl B (Space φ)) = LinearEquiv.refl ℂ W := by
  ext w
  rfl

@[simp] theorem toComplexEquiv_trans (θ : B →ₐ[ℂ] Module.End ℂ U)
    (e : Space φ ≃ₗ[B] Space χ) (f : Space χ ≃ₗ[B] Space θ) :
    toComplexEquiv φ θ (e.trans f) =
      (toComplexEquiv φ χ e).trans (toComplexEquiv χ θ f) := by
  ext w
  rfl

end Intertwiners

section ExistingModule

variable [Module B W] [IsScalarTower ℂ B W]

/-- Starting with an actual compatible module and forming its action recovers that module. -/
def ofModuleEquiv : Space (Algebra.lsmul ℂ ℂ W (A := B)) ≃ₗ[B] W where
  toFun := equiv (Algebra.lsmul ℂ ℂ W (A := B))
  invFun := (equiv (Algebra.lsmul ℂ ℂ W (A := B))).symm
  left_inv := (equiv (Algebra.lsmul ℂ ℂ W (A := B))).left_inv
  right_inv := (equiv (Algebra.lsmul ℂ ℂ W (A := B))).right_inv
  map_add' := (equiv (Algebra.lsmul ℂ ℂ W (A := B))).map_add
  map_smul' := fun _ _ => rfl

@[simp] theorem ofModuleEquiv_apply (w : Space (Algebra.lsmul ℂ ℂ W (A := B))) :
    ofModuleEquiv (B := B) (W := W) w = equiv (Algebra.lsmul ℂ ℂ W (A := B)) w := rfl

/-- The canonical module round trip preserves simplicity. -/
theorem ofModule_simple_iff :
    IsSimpleModule B (Space (Algebra.lsmul ℂ ℂ W (A := B))) ↔ IsSimpleModule B W :=
  (ofModuleEquiv (B := B) (W := W)).isSimpleModule_iff

end ExistingModule

end PaperXI.AlgebraActionModule
