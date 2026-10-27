import PaperX.WeilSpecialChain
import PaperX.WeilSmooth
import PaperX.WeilMorphisms
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.NormNum

/-! An infinite finite-by-cyclic group with two actual inertia actions.
The same F and the same nonzero N can have different local Euler denominators.
No identification with an arithmetic local field's Weil group is asserted. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.WeilExamples
open Polynomial PaperX.WeilData PaperX.WeilEuler PaperX.WeilSpecialChain
open PaperX.WeilCopies PaperX.CarrierSummands

abbrev C2 := Multiplicative (ZMod 2)
abbrev G := C2 × Multiplicative ℤ

def inertia : Subgroup G := (MonoidHom.snd C2 (Multiplicative ℤ)).ker
instance inertiaNormal : inertia.Normal := inferInstanceAs (MonoidHom.ker _).Normal

instance inertiaFinite : Finite inertia := Finite.of_injective (fun h : inertia => h.val.1) (by
  intro h k he
  apply Subtype.ext
  apply Prod.ext he
  exact h.property.trans k.property.symm)

instance groupTopology : TopologicalSpace G := ⊥
instance groupDiscrete : DiscreteTopology G := ⟨rfl⟩

def powerChar (b : ℚˣ) : Multiplicative ℤ →* ℚˣ where
  toFun z := b ^ z.toAdd
  map_one' := by simp
  map_mul' x y := by
    change b ^ (x.toAdd + y.toAdd) = _
    rw [zpow_add]

def signChar : C2 →* ℚˣ where
  toFun g := if g.toAdd = 0 then 1 else -1
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

def ν : G →* ℚˣ :=
  (powerChar (Units.mk0 (1/3) (by norm_num))).comp (MonoidHom.snd _ _)

def α : G →* ℚˣ :=
  (powerChar (Units.mk0 2 (by norm_num))).comp (MonoidHom.snd _ _)

def β : G →* ℚˣ := (signChar.comp (MonoidHom.fst _ _)) * α

def φ : G := (1, Multiplicative.ofAdd 1)
def τ : inertia := ⟨(Multiplicative.ofAdd 1, 1), rfl⟩

theorem norm_inertia (h : inertia) : ν h = 1 := by
  have hh : h.val.2 = 1 := h.property
  simp [ν, hh]

theorem unramified_inertia (h : inertia) : α h = 1 := by
  have hh : h.val.2 = 1 := h.property
  simp [α, hh]

theorem ramified_inertia : β τ ≠ 1 := by
  change (if (1 : ZMod 2) = 0 then (1 : ℚˣ) else -1) * _ ≠ 1
  rw [unramified_inertia]
  norm_num

theorem character_at_frobenius : α φ = Units.mk0 2 (by norm_num) ∧ β φ = α φ := by
  constructor <;> simp [α, β, φ, signChar, powerChar]

def unramified : Datum ν (Fin 3 → ℚ) := chainDatum ν α 3
def ramified : Datum ν (Fin 3 → ℚ) := chainDatum ν β 3

def unramifiedInertial : PaperX.WeilSmooth.InertialDatum (ν := ν) inertia (Fin 3 → ℚ) where
  toDatum := unramified
  inertia_finite := Set.finite_range _
  inertia_open := isOpen_discrete _

def ramifiedInertial : PaperX.WeilSmooth.InertialDatum (ν := ν) inertia (Fin 3 → ℚ) where
  toDatum := ramified
  inertia_finite := Set.finite_range _
  inertia_open := isOpen_discrete _

theorem same_F_and_N : unramified.r φ = ramified.r φ ∧ unramified.N = ramified.N := by
  constructor
  · change (PaperX.SpecialMonodromy.diagonalF (ν φ) (α φ) 3).toLinearMap =
      (PaperX.SpecialMonodromy.diagonalF (ν φ) (β φ) 3).toLinearMap
    rw [character_at_frobenius.2]
  · rfl

theorem nonzero_monodromy : unramified.N ^ 2 ≠ 0 ∧ unramified.N ^ 3 = 0 :=
  ⟨PaperX.SpecialMonodromy.shift_previous_power_nonzero 3 (by decide),
    PaperX.SpecialMonodromy.shift_nilpotent 3⟩

theorem local_dimensions : Module.finrank ℚ (fixedKernel unramified inertia) = 1 ∧
    Module.finrank ℚ (fixedKernel ramified inertia) = 0 := by
  constructor
  · exact unramified_dimension ν α 3 (by decide) inertia norm_inertia unramified_inertia
  · exact ramified_dimension ν β 3 inertia norm_inertia ⟨τ, ramified_inertia⟩

theorem local_polynomials : localCharpoly unramified inertia φ = X - C 2 ∧
    localCharpoly ramified inertia φ = 1 := by
  constructor
  · rw [unramified, unramified_charpoly ν α 3 (by decide) inertia norm_inertia
      unramified_inertia φ, character_at_frobenius.1]
    rfl
  · exact ramified_charpoly ν β 3 inertia norm_inertia ⟨τ, ramified_inertia⟩ φ

theorem euler_polynomials : eulerPolynomial unramified inertia φ = 1 - C 2 * X ∧
    eulerPolynomial ramified inertia φ = 1 := by
  constructor
  · rw [unramified, unramified_euler ν α 3 (by decide) inertia norm_inertia
      unramified_inertia φ, character_at_frobenius.1]
    rfl
  · exact ramified_euler ν β 3 inertia norm_inertia ⟨τ, ramified_inertia⟩ φ

theorem same_F_N_different_euler : unramified.r φ = ramified.r φ ∧
    unramified.N = ramified.N ∧
    eulerPolynomial unramified inertia φ ≠ eulerPolynomial ramified inertia φ := by
  refine ⟨same_F_and_N.1, same_F_and_N.2, ?_⟩
  rw [euler_polynomials.1, euler_polynomials.2]
  intro he
  have hc := congrArg (fun p : Polynomial ℚ => p.coeff 1) he
  norm_num at hc

def family (i : Fin 2) : Datum ν (Fin 3 → ℚ) := if i = 0 then unramified else ramified
def multiplicities (i : Fin 2) : ℕ := if i = 0 then 2 else 1

theorem mixed_dimension :
    Module.finrank ℚ (fixedKernel (copiesDatum family multiplicities) inertia) = 2 := by
  rw [fixed_dimension_sum, Fin.sum_univ_two]
  change 2 * Module.finrank ℚ (fixedKernel unramified inertia) +
    1 * Module.finrank ℚ (fixedKernel ramified inertia) = 2
  rw [local_dimensions.1, local_dimensions.2]

theorem mixed_euler : eulerPolynomial (copiesDatum family multiplicities) inertia φ =
    (1 - C 2 * X)^2 := by
  rw [euler_product]
  simp [Fin.prod_univ_two, family, multiplicities, euler_polynomials.1, euler_polynomials.2]


theorem geometric_norm : (ν φ : ℚ) = 1/3 := by simp [ν, φ, powerChar]

/-- Equal Euler factors do not recover chain length or the monodromy operator. -/
theorem same_euler_different_monodromy :
    eulerPolynomial (chainDatum ν α 1) inertia φ = eulerPolynomial unramified inertia φ ∧
    (chainDatum ν α 1).N = 0 ∧ unramified.N ^ 2 ≠ 0 := by
  refine ⟨?_, ?_, nonzero_monodromy.1⟩
  · rw [unramified, unramified_euler ν α 1 (by decide) inertia norm_inertia
      unramified_inertia φ, unramified_euler ν α 3 (by decide) inertia norm_inertia
      unramified_inertia φ]
  · exact PaperX.SpecialMonodromy.shift_nilpotent 1

end PaperX.WeilExamples
