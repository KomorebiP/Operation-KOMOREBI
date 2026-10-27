module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 7e73bc30cbbe457fabdd978d6df50ef570df0f53155abca94bcc298d7046e276
   Canonical certificate JSON SHA256: c87eb70f136f98def3c7a9ebf7cb13f25637c140e2bf2ea75fa5239c8f317992
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseHiddenP2R5D6
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 32
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 32 (((([[[7, 1, 3, 30, 26, 12], [14, 0, 21, 17, 5, 24], [26, 11, 24, 15, 20, 19], [16, 3, 19, 14, 28, 19], [12, 26, 25, 26, 13, 7], [8, 19, 15, 14, 0, 7]], [[9, 5, 8, 10, 20, 20], [23, 15, 31, 8, 29, 7], [21, 5, 31, 15, 0, 17], [24, 17, 30, 0, 18, 22], [28, 9, 12, 2, 4, 8], [25, 15, 26, 14, 14, 8]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 32 ((([[13, 18, 20, 28, 0, 27]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 32 (([13, 18, 20, 28, 0, 27] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 32 (([23, 30, 10, 6, 12, 25] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def data : CertificateData R 6 2 2 1 2 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 32 ((([[1, 26, 4, 12, 0, 7], [0, 24, 2, 30, 20, 8]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 32 (((([[[19, 3], [20, 15]], [[2, 0], [26, 1]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 32 ((([[13, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 32 ((([[5, 0], [11, 23]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 2 6 := fun i j => Fin.ofNat 32 ((([[13, 18, 20, 28, 0, 27], [23, 30, 10, 6, 12, 25]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.elim0 i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 2 where
  width := by decide
  weights := fun i => Fin.ofNat 32 (([1, 2] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 32 ((([[1, 28, 22, 16, 8, 9], [0, 0, 1, 0, 0, 0], [0, 1, 20, 17, 22, 28], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 32 ((([[1, 26, 4, 12, 0, 7], [0, 12, 1, 15, 10, 4], [0, 1, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 2) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 2 6 := fun i j => Fin.ofNat 32 ((([[1, 0, 0, 0, 0, 0], [6, 1, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 2) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseHiddenP2R5D6
