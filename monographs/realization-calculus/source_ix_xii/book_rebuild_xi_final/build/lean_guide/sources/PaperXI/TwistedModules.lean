import PaperXI.TwistedMatrix
import PaperXI.SimpleModuleClassification

/-! The simple-module conclusions of Paper XI, Proposition 8.3, for the actual
constructed twisted algebra. Existence, uniqueness, finite dimensionality,
and the square-root dimension are proved under the source hypotheses. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedModules
open CocycleCommutator

variable {A : Type*} [CommGroup A] [Fintype A]
variable (c : Cocycle A ℂˣ) (hc : Normalized c) (hnd : radical c = ⊥)
include hc hnd

set_option backward.isDefEq.respectTransparency false in
/-- A genuine simple module exists: it can be taken to be a left ideal. -/
theorem exists_simple_ideal :
    let B : Type _ := TwistedAlgebra.Algebra c hc
    letI : Ring B := inferInstance
    ∃ I : Ideal B, IsSimpleModule B I := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  exact SimpleModuleClassification.exists_simple_ideal (TwistedAlgebra.Algebra c hc)

/-- Any two actual simple twisted-algebra modules are isomorphic as modules. -/
theorem equivalent (M N : Type*) [AddCommGroup M] [AddCommGroup N]
    [Module (TwistedAlgebra.Algebra c hc) M] [Module (TwistedAlgebra.Algebra c hc) N]
    [IsSimpleModule (TwistedAlgebra.Algebra c hc) M]
    [IsSimpleModule (TwistedAlgebra.Algebra c hc) N] :
    Nonempty (M ≃ₗ[TwistedAlgebra.Algebra c hc] N) := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  exact SimpleModuleClassification.equivalent (TwistedAlgebra.Algebra c hc) M N

variable (M : Type*) [AddCommGroup M] [Module ℂ M]
variable [Module (TwistedAlgebra.Algebra c hc) M]
variable [IsScalarTower ℂ (TwistedAlgebra.Algebra c hc) M]
variable [IsSimpleModule (TwistedAlgebra.Algebra c hc) M]

/-- Finite dimensionality is derived for every simple module, not supplied. -/
theorem finiteDimensional : FiniteDimensional ℂ M := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  exact SimpleModuleClassification.finiteDimensional (TwistedAlgebra.Algebra c hc) M

/-- The square of the simple-module dimension equals the index-group order. -/
theorem finrank_sq : Module.finrank ℂ M ^ 2 = Fintype.card A := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  exact (SimpleModuleClassification.finrank_sq (TwistedAlgebra.Algebra c hc) M).trans
    (TwistedAlgebra.finrank_eq_card c hc)

/-- Every irreducible twisted-algebra module has the dimension claimed in 8.3. -/
theorem finrank_sqrt : Module.finrank ℂ M = Nat.sqrt (Fintype.card A) := by
  rw [← finrank_sq c hc hnd M, Nat.sqrt_eq']

end PaperXI.TwistedModules
