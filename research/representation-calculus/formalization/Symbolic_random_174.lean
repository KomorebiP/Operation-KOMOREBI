module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 46dc52193ad5d9de39a4512d49ac23335ce8b725af6a4ec07de4476ea7300b4b
   Canonical certificate JSON SHA256: 0ac15b79e1f2fc158549c903e7bb2750a0cd54908ee45813145f5e6d05e2f1eb
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom174
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 16
def actions : Fin 1 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 16 (((([[[5, 9, 3, 7, 10, 3], [1, 14, 1, 8, 1, 10], [14, 9, 14, 10, 13, 1], [8, 1, 8, 14, 12, 12], [14, 14, 2, 12, 7, 13], [15, 15, 8, 7, 13, 3]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 16 ((([[15, 4, 1, 3, 9, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 16 (([15, 4, 1, 3, 9, 2] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 16 (([1, 7, 9, 7, 4, 5] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 16 (([5, 6, 0, 14, 7, 9] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row1 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row2 row1_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 16 (([8, 8, 11, 10, 6, 9] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row2 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0] 0 row2 row3 row2_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 16 (([5, 0, 14, 9, 14, 4] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row3 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0, 0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0, 0] 0 row3 row4 row3_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 16 (([5, 4, 7, 1, 10, 11] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row4 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0, 0, 0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0, 0, 0] 0 row4 row5 row4_sound row5_local x
def data : CertificateData R 6 6 1 1 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 16 ((([[1, 12, 15, 13, 7, 14], [0, 1, 14, 14, 7, 5], [0, 0, 1, 9, 14, 9], [0, 0, 0, 1, 4, 10], [0, 0, 0, 0, 1, 5], [0, 0, 0, 0, 0, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 16 (((([[[15, 5, 0, 0, 0, 0], [2, 15, 11, 0, 0, 0], [1, 1, 13, 15, 0, 0], [6, 7, 4, 0, 7, 0], [9, 13, 13, 15, 12, 3], [14, 6, 10, 10, 10, 2]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 16 ((([[15, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([0, 0], 0), ([0, 0, 0], 0), ([0, 0, 0, 0], 0), ([0, 0, 0, 0, 0], 0)] : List (List (Fin 1) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 16 ((([[15, 0, 0, 0, 0, 0], [3, 3, 0, 0, 0, 0], [15, 2, 9, 0, 0, 0], [5, 14, 3, 7, 0, 0], [3, 8, 6, 5, 1, 0], [0, 0, 10, 11, 3, 11]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 16 ((([[15, 4, 1, 3, 9, 2], [1, 7, 9, 7, 4, 5], [5, 6, 0, 14, 7, 9], [8, 8, 11, 10, 6, 9], [5, 0, 14, 9, 14, 4], [5, 4, 7, 1, 10, 11]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 1)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 16 (([1, 1, 1, 1, 1, 2] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 16 ((([[1, 4, 9, 10, 7, 6], [0, 1, 2, 0, 13, 8], [0, 0, 1, 7, 6, 3], [0, 0, 0, 1, 12, 10], [0, 0, 0, 0, 1, 11], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 16 ((([[1, 12, 15, 13, 7, 14], [0, 1, 14, 14, 7, 5], [0, 0, 1, 9, 14, 9], [0, 0, 0, 1, 4, 10], [0, 0, 0, 0, 1, 5], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 1) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 16 ((([[1, 0, 0, 0, 0, 0], [4, 1, 0, 0, 0, 0], [9, 2, 1, 0, 0, 0], [10, 0, 7, 1, 0, 0], [7, 13, 6, 12, 1, 0], [6, 8, 3, 10, 11, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom174
