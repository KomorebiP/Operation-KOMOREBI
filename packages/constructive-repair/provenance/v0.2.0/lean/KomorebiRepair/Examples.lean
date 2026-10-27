import KomorebiRepair.Search
import KomorebiRepair.Minimal
import KomorebiRepair.Conservation
import KomorebiRepair.Transport
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith

/-! # Concrete witnesses and counterexamples from the exact audit -/
namespace KomorebiRepair.Examples

abbrev Q3 := Fin 3 → ℚ

def rationalD : ℚ →ₗ[ℚ] Q3 where
  toFun x := ![x, 0, 0]
  map_add' x y := by ext i; fin_cases i <;> simp
  map_smul' c x := by ext i; fin_cases i <;> simp

def rationalR : Q3 := ![0, 1, 0]
def rationalE0 : Q3 := ![0, 1, 1]
def rationalE1 : Q3 := ![0, 0, 1]

theorem first_menu_entry_insufficient :
    ¬ ∃ u a : ℚ, rationalD u + a • rationalE0 = -rationalR := by
  rintro ⟨u, a, h⟩
  have h1 := congrFun h 1
  have h2 := congrFun h 2
  norm_num [rationalD, rationalE0, rationalR] at h1
  have h2' : a = 0 := by simpa [rationalD, rationalE0, rationalR, Matrix.cons_val] using h2
  linarith

theorem second_menu_entry_insufficient :
    ¬ ∃ u a : ℚ, rationalD u + a • rationalE1 = -rationalR := by
  rintro ⟨u, a, h⟩
  have h1 := congrFun h 1
  norm_num [rationalD, rationalE1, rationalR] at h1

theorem two_menu_entries_repair :
    rationalD 0 + (-1 : ℚ) • rationalE0 + (1 : ℚ) • rationalE1 = -rationalR := by
  ext i
  fin_cases i <;> norm_num [rationalD, rationalE0, rationalE1, rationalR]

theorem one_free_direction_repairs :
    rationalD 0 + (-1 : ℚ) • rationalR = -rationalR := by
  simp

def fineD : ℚ →ₗ[ℚ] (ℚ × ℚ) := (LinearMap.id : ℚ →ₗ[ℚ] ℚ).prod 0

theorem coarse_information_loss :
    ¬ Correctable fineD (0, 1) ∧
    Correctable (LinearMap.id : ℚ →ₗ[ℚ] ℚ) ((LinearMap.fst ℚ ℚ ℚ) (0, 1)) := by
  constructor
  · rintro ⟨u, h⟩
    have hh := congrArg Prod.snd h
    norm_num [fineD] at hh
  · exact ⟨0, by simp⟩

theorem collapsing_transport_not_faithful :
    ¬ FaithfulOn
      (obstructionTransport fineD (LinearMap.id : ℚ →ₗ[ℚ] ℚ)
        LinearMap.id (LinearMap.fst ℚ ℚ ℚ) (by ext; simp [fineD]))
      (obstructionSpan fineD (fun _ : Unit => (0, 1))) := by
  intro hf
  exact coarse_information_loss.1
    ((transport_faithfulness_on_obstruction_span fineD LinearMap.id LinearMap.id
      (LinearMap.fst ℚ ℚ ℚ) (by ext; simp [fineD])
      (fun _ : Unit => (0, 1)) hf ()).mp coarse_information_loss.2)

abbrev F2 := ZMod 2
abbrev F23 := Fin 3 → F2

def finiteD : F2 →ₗ[F2] F23 where
  toFun x := ![x, 0, 0]
  map_add' x y := by ext i; fin_cases i <;> simp
  map_smul' c x := by ext i; fin_cases i <;> simp

def finiteR (_ : Unit) : F23 := ![0, 1, 0]
def finiteE (j : Fin 2) : F23 := if j = 0 then ![0, 1, 1] else ![0, 0, 1]

theorem executable_menu_returns_both :
    bestRepairMenu finiteD finiteE finiteR (fun _ => true) Finset.card =
      some {0, 1} := by
  unfold bestRepairMenu allMenus
  rw [Fin.sort_univ]
  decide +kernel

theorem executable_restricted_menu_rejects :
    bestRepairMenu finiteD finiteE finiteR (fun S => decide (S.card ≤ 1)) Finset.card =
      none := by
  unfold bestRepairMenu allMenus
  rw [Fin.sort_univ]
  decide +kernel

/-- This conclusion comes from the generic certified algorithm theorem. -/
theorem executable_menu_is_globally_optimal :
    FamilyRepairable finiteD (menuMap finiteE {0, 1}) finiteR ∧
    ∀ T : Finset (Fin 2), FamilyRepairable finiteD (menuMap finiteE T) finiteR → 2 ≤ T.card := by
  obtain ⟨_, hr, hmin⟩ := menu_optimality_certificate finiteD finiteE finiteR
    (fun _ => true) Finset.card {0, 1} executable_menu_returns_both
  refine ⟨hr, ?_⟩
  intro T hT
  simpa using hmin T rfl hT

#eval bestRepairMenu finiteD finiteE finiteR (fun _ => true) Finset.card
#eval bestRepairMenu finiteD finiteE finiteR (fun S => decide (S.card ≤ 1)) Finset.card

end KomorebiRepair.Examples
