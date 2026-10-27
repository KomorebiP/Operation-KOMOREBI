import PaperXI.TwistedRegular
import Mathlib.LinearAlgebra.Dimension.StrongRankCondition
import Mathlib.LinearAlgebra.FiniteDimensional.Defs

/-! A concrete realization of the complex twisted group algebra, including its
actual basis, multiplication, units, and dimension. The ambient endomorphism
algebra supplies the ring laws; all closure and basis assertions are proved. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedAlgebra

open CocycleCommutator TwistedRegular Module
variable {A : Type*} [CommGroup A]

/-- Linear span of all twisted left regular operators. -/
def operatorSpan (c : Cocycle A ℂˣ) : Submodule ℂ (Module.End ℂ (A → ℂ)) :=
  Submodule.span ℂ (Set.range (regular c))

theorem regular_mem (c : Cocycle A ℂˣ) (a : A) : regular c a ∈ operatorSpan c :=
  Submodule.subset_span (Set.mem_range_self a)

theorem one_mem (c : Cocycle A ℂˣ) (hc : Normalized c) :
    (1 : Module.End ℂ (A → ℂ)) ∈ operatorSpan c := by
  rw [← regular_one c hc]
  exact regular_mem c 1

theorem mul_mem (c : Cocycle A ℂˣ) {x y : Module.End ℂ (A → ℂ)}
    (hx : x ∈ operatorSpan c) (hy : y ∈ operatorSpan c) : x * y ∈ operatorSpan c := by
  induction hx using Submodule.span_induction with
  | mem x hx =>
      obtain ⟨a, rfl⟩ := hx
      induction hy using Submodule.span_induction with
      | mem y hy =>
          obtain ⟨b, rfl⟩ := hy
          rw [regular_mul]
          exact (operatorSpan c).smul_mem _ (regular_mem c (a * b))
      | zero => simp
      | add x y _ _ hx hy => simpa [mul_add] using (operatorSpan c).add_mem hx hy
      | smul z y _ hy => simpa [mul_smul_comm] using (operatorSpan c).smul_mem z hy
  | zero => simp
  | add x y _ _ hx hy => simpa [add_mul] using (operatorSpan c).add_mem hx hy
  | smul z x _ hx => simpa [smul_mul_assoc] using (operatorSpan c).smul_mem z hx

/-- The normalized twisted algebra as a concrete complex subalgebra. -/
def subalgebra (c : Cocycle A ℂˣ) (hc : Normalized c) :
    Subalgebra ℂ (Module.End ℂ (A → ℂ)) where
  carrier := operatorSpan c
  zero_mem' := (operatorSpan c).zero_mem
  add_mem' := (operatorSpan c).add_mem
  one_mem' := one_mem c hc
  mul_mem' := mul_mem c
  algebraMap_mem' z := by
    rw [Algebra.algebraMap_eq_smul_one]
    exact (operatorSpan c).smul_mem z (one_mem c hc)

/-- The actual complex twisted group algebra ℂᶜ[A]. -/
abbrev Algebra (c : Cocycle A ℂˣ) (hc : Normalized c) := subalgebra c hc

variable [Fintype A]

/-- Its canonical basis is proved independent by acting on the identity point mass. -/
def basis (c : Cocycle A ℂˣ) (hc : Normalized c) : Basis A ℂ (Algebra c hc) :=
  (Basis.span (regular_linearIndependent c hc)).map (subalgebra c hc).toSubmoduleEquiv

@[simp] theorem coe_basis (c : Cocycle A ℂˣ) (hc : Normalized c) (a : A) :
    (basis c hc a : Module.End ℂ (A → ℂ)) = regular c a := by
  unfold basis
  erw [Basis.map_apply]
  exact Basis.coe_span_apply (regular_linearIndependent c hc) a

theorem basis_mul (c : Cocycle A ℂˣ) (hc : Normalized c) (a b : A) :
    basis c hc a * basis c hc b = (c.coeff a b : ℂ) • basis c hc (a * b) := by
  apply Subtype.ext
  change (basis c hc a : Module.End ℂ (A → ℂ)) * basis c hc b =
    (c.coeff a b : ℂ) • (basis c hc (a * b) : Module.End ℂ (A → ℂ))
  simp only [coe_basis, regular_mul]

@[simp] theorem basis_one (c : Cocycle A ℂˣ) (hc : Normalized c) :
    basis c hc 1 = 1 := by
  apply Subtype.ext
  simpa using regular_one c hc

/-- Every canonical basis vector has an explicit two-sided inverse. -/
def basisUnit (c : Cocycle A ℂˣ) (hc : Normalized c) (a : A) : (Algebra c hc)ˣ where
  val := basis c hc a
  inv := ((c.coeff a a⁻¹)⁻¹ : ℂˣ) • basis c hc a⁻¹
  val_inv := by
    rw [Units.smul_def, mul_smul_comm, basis_mul, mul_inv_cancel, basis_one, smul_smul]
    simp
  inv_val := by
    have h : c.coeff a a⁻¹ = c.coeff a⁻¹ a := by
      simpa [hc.1, hc.2] using c.assoc a a⁻¹ a
    rw [Units.smul_def, smul_mul_assoc, basis_mul, inv_mul_cancel, basis_one, smul_smul, h]
    simp

@[simp] theorem coe_basisUnit (c : Cocycle A ℂˣ) (hc : Normalized c) (a : A) :
    (basisUnit c hc a : Algebra c hc) = basis c hc a := rfl

theorem basis_isUnit (c : Cocycle A ℂˣ) (hc : Normalized c) (a : A) :
    IsUnit (basis c hc a) := (basisUnit c hc a).isUnit

instance finiteDimensional (c : Cocycle A ℂˣ) (hc : Normalized c) :
    FiniteDimensional ℂ (Algebra c hc) := Module.Finite.of_basis (basis c hc)

theorem finrank_eq_card (c : Cocycle A ℂˣ) (hc : Normalized c) :
    Module.finrank ℂ (Algebra c hc) = Fintype.card A :=
  Module.finrank_eq_card_basis (basis c hc)

end PaperXI.TwistedAlgebra
