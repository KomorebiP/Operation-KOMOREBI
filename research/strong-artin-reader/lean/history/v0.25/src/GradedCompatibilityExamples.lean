import PolynomialMovingSyzygyHensel
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.NormNum

/-! A nontrivial redundant quadratic system instantiates the full lifting
theorem. Exact small-ring controls distinguish graded compatibility from the
false fixed-target shortcut. -/
namespace Komorebi.StrongArtin.GradedCompatibilityExamples
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PolynomialResidueModel
open Komorebi.StrongArtin.PolynomialMovingSyzygyHensel
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PowerDivisibility

variable {R k : Type*} [CommRing R] [Field k]

/-- One equation and its genuinely variable-dependent redundant companion. -/
def quadraticSystem (c : R) : System Unit Bool R :=
  let f := Expr.add (Expr.add (.mul (.var ()) (.var ())) (.var ())) (.const c)
  fun b => if b then .mul (.var ()) f else f

/-- The exact row relation is `(-x, 1)`, not the frozen row `(0, 1)`. -/
def quadraticRelations : Unit → Bool → Expr Unit R :=
  fun _ b => if b then .const 1 else .neg (.var ())

theorem quadratic_exact_moving_identity (c : R) (x : Unit → R) :
    relationMap quadraticRelations x (evalSystem (quadraticSystem c) x) = 0 := by
  funext l
  simp [relationMap, quadraticRelations, quadraticSystem, evalSystem,
    Expr.eval]

theorem quadratic_residual_exactness (q : R →+* k) (c : R) (hc : q c = 0) :
    LinearMap.range (systemDerivative (reduceSystem q (quadraticSystem c)) (0 : Unit → k)) =
      LinearMap.ker (relationMap (reduceRelations q quadraticRelations) (0 : Unit → k)) := by
  have hJ : ∀ u : Unit → k,
      systemDerivative (reduceSystem q (quadraticSystem c)) 0 u =
        (fun b : Bool => if b then 0 else u ()) := by
    intro u
    funext b
    cases b <;> simp [systemDerivative, reduceSystem, quadraticSystem, reduceExpr,
      Expr.deriv, Expr.eval, hc]
  have hB : ∀ w : Bool → k,
      relationMap (reduceRelations q quadraticRelations) (0 : Unit → k) w =
        (fun _ : Unit => w true) := by
    intro w
    funext l
    simp [relationMap, reduceRelations, quadraticRelations, reduceExpr,
      Expr.eval]
  ext w
  constructor
  · rintro ⟨u, rfl⟩
    change relationMap (reduceRelations q quadraticRelations) (0 : Unit → k)
      (systemDerivative (reduceSystem q (quadraticSystem c)) 0 u) = 0
    rw [hB, hJ]
    rfl
  · intro hw
    have hwzero : w true = 0 := by
      change relationMap (reduceRelations q quadraticRelations) (0 : Unit → k) w = 0 at hw
      rw [hB] at hw
      exact congrFun hw ()
    refine ⟨fun _ : Unit => w false, ?_⟩
    rw [hJ]
    funext b
    cases b
    · rfl
    · exact hwzero.symm

/-- The new theorem is instantiated: the full redundant nonlinear system has
a solution, not only a separately written linearized surrogate. -/
theorem exists_redundant_quadratic_root
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (hnil : IsNilpotent pi)
    (c : R) (hc : q c = 0) :
    ∃ z : R, q z = 0 ∧ z * z + z + c = 0 ∧ z * (z * z + z + c) = 0 := by
  obtain ⟨x, hx, hFx⟩ := exists_exact_root_over_principal_nilpotent_residue
    pi q hq hker hnil (quadraticSystem c) quadraticRelations (0 : Unit → R)
    (by intro j; cases j <;> simp [evalSystem, quadraticSystem, Expr.eval, hc])
    (by intro x _; exact quadratic_exact_moving_identity c x)
    (by
      have hz : (fun i : Unit => q ((0 : Unit → R) i)) = (0 : Unit → k) := by
        funext i; exact q.map_zero
      rw [hz]
      exact quadratic_residual_exactness q c hc)
  have hqx : q (x ()) = 0 := by
    have hr := (ResidualLayer.coordinateReduction (ι := Unit) pi q hq hker).zero_iff
    have hz := (hr (x - 0)).mpr hx
    simpa using congrFun hz ()
  refine ⟨x (), hqx, ?_, ?_⟩
  · simpa [evalSystem, quadraticSystem, Expr.eval] using congrFun hFx false
  · simpa [evalSystem, quadraticSystem, Expr.eval] using congrFun hFx true

/-- Mandatory v0.24 negative control: the ambient error is not in the fixed
horizontal target, but its normalized residue is compatible. -/
theorem normalized_error_repairs_fixed_target_failure :
    (2 : ZMod 8) * 1 = 2 ∧ (2 : ZMod 8) * 2 = 4 ∧
    (4 : ZMod 8) ≠ 0 ∧ (2 : ZMod 2) = 0 := by
  decide

/-- A residual root alone does not imply lifting; here the genuine next-order
obstruction is nonzero. -/
theorem square_plus_one_has_no_root_mod_four :
    ∀ x : ZMod 4, x * x + 1 ≠ 0 := by decide

/-- A residual relation coefficient equal to one cannot be lifted to an exact
annihilating relation for the nonzero constant error 2. -/
theorem residual_identity_relation_does_not_lift :
    ∀ a : ZMod 4, a.val % 2 = 1 → a * 2 ≠ 0 := by decide

end Komorebi.StrongArtin.GradedCompatibilityExamples
