import KomorebiSpace.TowerCorrection
import Mathlib.Analysis.Normed.Lp.lpSpace
import Mathlib.Analysis.Normed.Operator.NormedSpace
import Mathlib.Algebra.Category.ModuleCat.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

set_option autoImplicit false

/-!
# Bounded Banach tower transports

The candidate space is the dependent l-infinity product of continuous linear
operator spaces. Bonding maps have a supplied uniform bound. The actual
naturality differential is constructed as a continuous linear map with a
proved operator bound, rather than supplied as an unrelated analytic map.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace

structure BanachTower (𝕜 : Type u) [NontriviallyNormedField 𝕜] where
  Obj : ℕ → Type v
  [normed : ∀ n, NormedAddCommGroup (Obj n)]
  [space : ∀ n, NormedSpace 𝕜 (Obj n)]
  [complete : ∀ n, CompleteSpace (Obj n)]
  down : ∀ n, Obj (n + 1) →L[𝕜] Obj n
  bound : ℝ≥0
  down_bound : ∀ n, ‖down n‖ ≤ (bound : ℝ)

attribute [instance] BanachTower.normed BanachTower.space BanachTower.complete

namespace BanachTower
open CategoryTheory
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

abbrev Candidates := lp (fun n => X.Obj n →L[𝕜] Y.Obj n) (∞ : ℝ≥0∞)
abbrev Residuals := lp (fun n => X.Obj (n+1) →L[𝕜] Y.Obj n) (∞ : ℝ≥0∞)

/-- Explicit check that no candidate-space completeness is being postulated. -/
theorem candidates_complete : CompleteSpace (Candidates X Y) := inferInstance

def rawDefect (f : Candidates X Y) (n : ℕ) : X.Obj (n+1) →L[𝕜] Y.Obj n :=
  (Y.down n).comp (f (n+1)) - (f n).comp (X.down n)

theorem rawDefect_bound (f : Candidates X Y) (n : ℕ) :
    ‖rawDefect X Y f n‖ ≤ ((X.bound : ℝ) + Y.bound) * ‖f‖ := by
  have hfn := lp.norm_apply_le_norm ENNReal.top_ne_zero f n
  have hfs := lp.norm_apply_le_norm ENNReal.top_ne_zero f (n+1)
  calc
    ‖rawDefect X Y f n‖ ≤ ‖(Y.down n).comp (f (n+1))‖ +
        ‖(f n).comp (X.down n)‖ := norm_sub_le _ _
    _ ≤ ‖Y.down n‖ * ‖f (n+1)‖ + ‖f n‖ * ‖X.down n‖ :=
      add_le_add ((Y.down n).opNorm_comp_le _) ((f n).opNorm_comp_le _)
    _ ≤ (Y.bound : ℝ) * ‖f‖ + ‖f‖ * (X.bound : ℝ) :=
      add_le_add
        (mul_le_mul (Y.down_bound n) hfs (norm_nonneg _) (NNReal.coe_nonneg _))
        (mul_le_mul hfn (X.down_bound n) (norm_nonneg _) (norm_nonneg _))
    _ = ((X.bound : ℝ) + Y.bound) * ‖f‖ := by ring

/-- Boundedness of the actual defect family. -/
theorem rawDefect_mem (f : Candidates X Y) :
    Memℓp (rawDefect X Y f) (∞ : ℝ≥0∞) := by
  apply memℓp_infty
  refine ⟨((X.bound : ℝ) + Y.bound) * ‖f‖, ?_⟩
  rintro _ ⟨n, rfl⟩
  exact rawDefect_bound X Y f n

def differentialLinear : Candidates X Y →ₗ[𝕜] Residuals X Y where
  toFun f := ⟨rawDefect X Y f, rawDefect_mem X Y f⟩
  map_add' f g := by
    apply lp.ext
    funext n
    change rawDefect X Y (f + g) n = rawDefect X Y f n + rawDefect X Y g n
    ext x
    simp only [rawDefect, lp.coeFn_add, Pi.add_apply, ContinuousLinearMap.comp_apply,
      sub_apply, add_apply, map_add]
    abel
  map_smul' c f := by
    apply lp.ext
    funext n
    ext x
    simp [rawDefect, smul_sub]

theorem differentialLinear_bound (f : Candidates X Y) :
    ‖differentialLinear X Y f‖ ≤ ((X.bound : ℝ) + Y.bound) * ‖f‖ := by
  apply lp.norm_le_of_forall_le (by positivity)
  exact rawDefect_bound X Y f

/-- The residual operator used by analytic exactification is now constructed. -/
def differential : Candidates X Y →L[𝕜] Residuals X Y :=
  (differentialLinear X Y).mkContinuous ((X.bound : ℝ) + Y.bound)
    (differentialLinear_bound X Y)

@[simp] theorem differential_apply (f : Candidates X Y) (n : ℕ) :
    differential X Y f n =
      (Y.down n).comp (f (n+1)) - (f n).comp (X.down n) := rfl

theorem differential_bound (f : Candidates X Y) :
    ‖differential X Y f‖ ≤ ((X.bound : ℝ) + Y.bound) * ‖f‖ :=
  differentialLinear_bound X Y f

theorem differential_opNorm :
    ‖differential X Y‖ ≤ (X.bound : ℝ) + Y.bound :=
  ContinuousLinearMap.opNorm_le_bound _ (by positivity) (differential_bound X Y)

/-- A genuinely continuous semantic observable: protect the entire level-n operator. -/
def evaluation (n : ℕ) : Candidates X Y →L[𝕜] (X.Obj n →L[𝕜] Y.Obj n) :=
  lp.evalCLM 𝕜 (fun n => X.Obj n →L[𝕜] Y.Obj n) ∞ n

@[simp] theorem evaluation_apply (f : Candidates X Y) (n : ℕ) :
    evaluation X Y n f = f n := rfl

theorem evaluation_bound (f : Candidates X Y) (n : ℕ) :
    ‖evaluation X Y n f‖ ≤ ‖f‖ :=
  lp.norm_apply_le_norm ENNReal.top_ne_zero f n

def Exact (f : Candidates X Y) : Prop :=
  ∀ n, (Y.down n).comp (f (n+1)) = (f n).comp (X.down n)

theorem exact_iff_differential_zero (f : Candidates X Y) :
    Exact X Y f ↔ differential X Y f = 0 := by
  constructor
  · intro h
    apply lp.ext
    funext n
    exact sub_eq_zero.mpr (h n)
  · intro h n
    have he := congrArg (fun g : Residuals X Y => g n) h
    exact sub_eq_zero.mp he

/-- Forget norms and continuity, preserving the actual bonding maps. -/
def algebraic : Tower (ModuleCat.{v} 𝕜) where
  obj n := ModuleCat.of 𝕜 (X.Obj n)
  down n := ModuleCat.ofHom (X.down n).toLinearMap

def algebraicPreHom (f : Candidates X Y) : Tower.PreHom X.algebraic Y.algebraic where
  app n := ModuleCat.ofHom (f n).toLinearMap

theorem exact_iff_algebraic (f : Candidates X Y) :
    Exact X Y f ↔ (algebraicPreHom X Y f).Exact := by
  constructor
  · intro h n
    ext x
    exact congrArg (fun T : X.Obj (n+1) →L[𝕜] Y.Obj n => T x) (h n)
  · intro h n
    ext x
    exact congrArg (fun T : ModuleCat.of 𝕜 (X.Obj (n+1)) ⟶
      ModuleCat.of 𝕜 (Y.Obj n) => T x) (h n)

def exactHom (f : Candidates X Y) (hf : Exact X Y f) :
    Tower.ExactHom X.algebraic Y.algebraic :=
  ⟨algebraicPreHom X Y f, (exact_iff_algebraic X Y f).mp hf⟩

/-- Actual inverse-limit points, with adjacent compatibility. -/
def Point := {x : ∀ n, X.Obj n // ∀ n, X.down n (x (n+1)) = x n}

/-- Exact bounded tower maps act on the entire inverse-limit point type. -/
def onLimit (f : Candidates X Y) (hf : Exact X Y f) (x : X.Point) : Y.Point :=
  ⟨fun n => f n (x.val n), by
    intro n
    have h := congrArg (fun T : X.Obj (n+1) →L[𝕜] Y.Obj n => T (x.val (n+1))) (hf n)
    change Y.down n (f (n+1) (x.val (n+1))) = f n (x.val n)
    exact h.trans (congrArg (f n) (x.property n))⟩

@[simp] theorem onLimit_coordinate (f : Candidates X Y) (hf : Exact X Y f)
    (x : X.Point) (n : ℕ) : (onLimit X Y f hf x).val n = f n (x.val n) := rfl

theorem onLimit_unique (f : Candidates X Y) (hf : Exact X Y f)
    (g : X.Point → Y.Point) (hg : ∀ x n, (g x).val n = f n (x.val n)) :
    g = onLimit X Y f hf := by
  funext x
  apply Subtype.ext
  funext n
  exact hg x n

end BanachTower
end KomorebiSpace
end
