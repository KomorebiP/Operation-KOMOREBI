module
public import FiniteDefinability
public import SemanticBoundaries

@[expose] public section
namespace Komorebi.LogicalResolution.Small
open Komorebi.Representation
set_option maxRecDepth 10000

def residue (n : Nat) (hn : 0<n) (a : Nat) : Fin n := ⟨a%n,Nat.mod_lt _ hn⟩

def source : System (Fin 8) (Fin 1) (Fin 1) (Fin 2) where
  step := fun _ s => residue 8 (by decide)
    ((s.val%2+s.val/2%2)%2 + 2*(s.val/2%2)+4*(s.val/4))
  observe := fun _ s => residue 2 (by decide) s.val

def target : System (Fin 4) (Fin 1) (Fin 1) (Fin 2) where
  step := fun _ s => residue 4 (by decide) ((s.val%2+s.val/2)%2+2*(s.val/2))
  observe := fun _ s => residue 2 (by decide) s.val

def encode : Fin 8 → Fin 4 := fun s => residue 4 (by decide) s.val

theorem local_check : checkLocal source target encode = true := by decide

def transport : Transport source target := checkedTransport source target encode local_check

def representative (s : Fin 4) : Fin 8 := ⟨s.val,Nat.lt_trans s.isLt (by decide)⟩

theorem representative_correct (s : Fin 4) : encode (representative s) = s := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt s.isLt

theorem encode_surjective : ∀ y, ∃ x, transport.encode x = y := by
  intro y; exact ⟨representative y,representative_correct y⟩

/-- Eight states compress to four with preservation of all formulas in our fragment. -/
theorem all_observational_formulas {n : Nat} (f : Formula (Fin 1) (Fin 1) (Fin 2) n)
    (ρ : Fin n → Fin 8) :
    f.Holds source ρ ↔ f.Holds target (fun i => encode (ρ i)) :=
  formula_transport transport encode_surjective f ρ

def tests : List (List (Fin 1) × Fin 1) := [([],0),([0],0)]

theorem finite_formula_encodes (x y : Fin 8) :
    (testEqualityFormula tests : Formula (Fin 1) (Fin 1) (Fin 2) 2).Holds
      source (twoVariables x y) ↔ encode x = encode y := by
  change (behavior source x [] 0 = behavior source y [] 0 ∧
    (behavior source x [0] 0 = behavior source y [0] 0 ∧ ¬ False)) ↔ encode x = encode y
  revert x y; decide

def separatingWord (x y : Fin 4) : List (Fin 1) :=
  if x.val%2 = y.val%2 then [0] else []

theorem target_separates : ∀ x y : Fin 4, x ≠ y →
    behavior target x (separatingWord x y) 0 ≠ behavior target y (separatingWord x y) 0 := by
  decide

theorem exact_behavior (x y : Fin 8) : ObsEq source x y ↔ encode x = encode y := by
  apply separated_encoding_exact transport
  intro a b h
  exact ⟨separatingWord a b,0,target_separates a b h⟩

theorem finite_formula_defines_all_behavior (x y : Fin 8) :
    (testEqualityFormula tests : Formula (Fin 1) (Fin 1) (Fin 2) 2).Holds
      source (twoVariables x y) ↔ ObsEq source x y :=
  (finite_formula_encodes x y).trans (exact_behavior x y).symm

end Komorebi.LogicalResolution.Small
