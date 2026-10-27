module
public import Mathlib.LinearAlgebra.StdBasis
public import Mathlib.Data.ZMod.Basic
public import Mathlib.Data.Fintype.Pi
public import Mathlib.Data.List.OfFn
public import Mathlib.Algebra.BigOperators.Fin
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic.FinCases
/-! Author: Komorebi P. Paper VII second block, Theorem 2.4.
A composition of addressed local X gates generates the full computational basis. -/
public section
set_option autoImplicit false
namespace KomorebiPaperVII.ComputationalSeed
open scoped BigOperators
abbrev Address (n : ℕ) := Fin n → ZMod 2
abbrev State (n : ℕ) := Address n → ℂ
def ket {n : ℕ} (a : Address n) : State n := Pi.single a 1
def seed (n : ℕ) : State n := ket 0
def translation {n : ℕ} (a : Address n) : Module.End ℂ (State n) where
  toFun := fun v x => v (x - a)
  map_add' := by intros; rfl
  map_smul' := by intros; rfl

theorem translation_zero (n : ℕ) : translation (0 : Address n) = 1 := by
  ext v x
  simp [translation]
theorem translation_add {n : ℕ} (a b : Address n) :
    translation a * translation b = translation (a + b) := by
  ext v x
  simp [translation, sub_sub]
theorem translation_ket {n : ℕ} (a b : Address n) :
    translation a (ket b) = ket (a + b) := by
  ext x
  simp [translation, ket, Pi.single_apply, sub_eq_iff_eq_add, add_comm]
theorem translation_involution {n : ℕ} (a : Address n) :
    translation a * translation a = 1 := by
  rw [translation_add, ZModModule.add_self, translation_zero]
def bit {n : ℕ} (j : Fin n) : Address n := Pi.single j 1
def localX {n : ℕ} (j : Fin n) : Module.End ℂ (State n) := translation (bit j)
theorem localX_on_ket {n : ℕ} (j : Fin n) (a : Address n) :
    localX j (ket a) = ket (Function.update a j (a j + 1)) := by
  rw [localX, translation_ket]
  congr 1
  ext k
  by_cases hk : k = j
  · subst k
    simp [bit, add_comm]
  · simp [bit, hk]
def controlledX {n : ℕ} (a : Address n) (j : Fin n) : Module.End ℂ (State n) :=
  if a j = 0 then 1 else localX j
theorem controlledX_eq_translation {n : ℕ} (a : Address n) (j : Fin n) :
    controlledX a j = translation (Pi.single j (a j)) := by
  have h : a j = 0 ∨ a j = 1 := by
    generalize a j = b
    fin_cases b
    · exact Or.inl rfl
    · exact Or.inr rfl
  rcases h with h | h
  · simp [controlledX, h, translation_zero]
  · simp [controlledX, h, localX, bit]
def addressCircuit {n : ℕ} (a : Address n) : Module.End ℂ (State n) :=
  (List.ofFn (fun j : Fin n => controlledX a j)).prod
theorem translation_list_product {n : ℕ} (L : List (Address n)) :
    (L.map translation).prod = translation L.sum := by
  induction L with
  | nil => simp [translation_zero]
  | cons a L ih => simp only [List.map_cons, List.prod_cons, List.sum_cons, ih, translation_add]
theorem sum_local_addresses {n : ℕ} (a : Address n) :
    (∑ j, Pi.single j (a j)) = a := by
  ext k
  simp [Finset.sum_apply, Pi.single_apply]
theorem circuit_eq_translation {n : ℕ} (a : Address n) :
    addressCircuit a = translation a := by
  unfold addressCircuit
  simp_rw [controlledX_eq_translation]
  simpa only [List.map_ofFn, Function.comp_def, List.sum_ofFn, sum_local_addresses] using
    translation_list_product (List.ofFn (fun j : Fin n => Pi.single j (a j)))
theorem circuit_seed {n : ℕ} (a : Address n) : addressCircuit a (seed n) = ket a := by
  rw [circuit_eq_translation, seed, translation_ket, add_zero]
theorem circuit_seed_basis {n : ℕ} (a : Address n) :
    addressCircuit a (seed n) = Pi.basisFun ℂ (Address n) a := by
  rw [circuit_seed, Pi.basisFun_apply, ket]
theorem addressed_seed_linearIndependent (n : ℕ) :
    LinearIndependent ℂ (fun a : Address n => addressCircuit a (seed n)) := by
  simp_rw [circuit_seed_basis]
  exact (Pi.basisFun ℂ (Address n)).linearIndependent
theorem addressed_seed_spans (n : ℕ) :
    Submodule.span ℂ (Set.range (fun a : Address n => addressCircuit a (seed n))) = ⊤ := by
  simp_rw [circuit_seed_basis]
  exact (Pi.basisFun ℂ (Address n)).span_eq
theorem number_of_addresses (n : ℕ) : Fintype.card (Address n) = 2 ^ n := by
  simp [Address]
end KomorebiPaperVII.ComputationalSeed

#print axioms KomorebiPaperVII.ComputationalSeed.translation_zero
#print axioms KomorebiPaperVII.ComputationalSeed.translation_add
#print axioms KomorebiPaperVII.ComputationalSeed.translation_ket
#print axioms KomorebiPaperVII.ComputationalSeed.translation_involution
#print axioms KomorebiPaperVII.ComputationalSeed.localX_on_ket
#print axioms KomorebiPaperVII.ComputationalSeed.controlledX_eq_translation
#print axioms KomorebiPaperVII.ComputationalSeed.translation_list_product
#print axioms KomorebiPaperVII.ComputationalSeed.sum_local_addresses
#print axioms KomorebiPaperVII.ComputationalSeed.circuit_eq_translation
#print axioms KomorebiPaperVII.ComputationalSeed.circuit_seed
#print axioms KomorebiPaperVII.ComputationalSeed.circuit_seed_basis
#print axioms KomorebiPaperVII.ComputationalSeed.addressed_seed_linearIndependent
#print axioms KomorebiPaperVII.ComputationalSeed.addressed_seed_spans
#print axioms KomorebiPaperVII.ComputationalSeed.number_of_addresses
