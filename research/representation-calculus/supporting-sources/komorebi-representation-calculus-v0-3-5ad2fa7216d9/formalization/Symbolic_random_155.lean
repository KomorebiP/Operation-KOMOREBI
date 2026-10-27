import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 5a3e8228d9c59c82935a26769fb1e0dc1c23924f6c1954a4ee52d2992babf9eb
   Canonical certificate JSON SHA256: 233028dd3f55099b0e5401d56f62c1907f561493234566f7fb7ef91806c7cafb
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom155
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 25
def actions : Fin 3 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 25 (((([[[8, 3, 20, 15, 0], [10, 17, 7, 17, 23], [23, 14, 8, 4, 4], [18, 10, 21, 8, 2], [17, 4, 18, 8, 13]], [[22, 14, 5, 15, 8], [5, 15, 1, 4, 20], [24, 12, 23, 2, 21], [10, 9, 5, 18, 21], [11, 16, 16, 22, 23]], [[10, 24, 10, 3, 23], [0, 6, 22, 11, 3], [21, 15, 20, 0, 11], [9, 14, 20, 21, 9], [2, 13, 10, 2, 8]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 5 := fun i j => Fin.ofNat 25 ((([[14, 15, 6, 2, 19], [11, 22, 22, 4, 19]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 25 (([14, 15, 6, 2, 19] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 25 (([11, 22, 22, 4, 19] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 25 (([9, 2, 17, 7, 20] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 25 (([6, 15, 12, 11, 17] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 25 (([22, 16, 20, 12, 3] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def data : CertificateData R 5 5 3 2 5 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 25 ((([[1, 10, 4, 18, 21], [0, 1, 19, 13, 24], [0, 0, 1, 13, 6], [0, 0, 0, 1, 22], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 25 (((([[[6, 8, 2, 0, 0], [14, 19, 22, 4, 17], [9, 3, 21, 7, 17], [17, 3, 17, 18, 11], [17, 9, 4, 8, 15]], [[4, 20, 12, 11, 0], [5, 19, 6, 14, 14], [20, 0, 4, 6, 6], [2, 16, 20, 23, 0], [11, 6, 8, 17, 1]], [[23, 14, 22, 1, 4], [14, 20, 16, 12, 12], [0, 0, 15, 15, 6], [3, 20, 23, 2, 10], [2, 18, 10, 2, 5]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 25 ((([[14, 0, 0, 0, 0], [11, 12, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 25 ((([[9, 0, 0, 0, 0], [23, 23, 0, 0, 0], [6, 8, 17, 0, 0], [12, 4, 11, 19, 0], [13, 12, 10, 14, 21]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 5 5 := fun i j => Fin.ofNat 25 ((([[14, 15, 6, 2, 19], [11, 22, 22, 4, 19], [9, 2, 17, 7, 20], [6, 15, 12, 11, 17], [22, 16, 20, 12, 3]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.elim0 i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 25 (([1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 25 ((([[1, 15, 11, 19, 10], [0, 1, 6, 9, 17], [0, 0, 1, 12, 5], [0, 0, 0, 1, 3], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 25 ((([[1, 10, 4, 18, 21], [0, 1, 19, 13, 24], [0, 0, 1, 13, 6], [0, 0, 0, 1, 22], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 5 5 := fun i j => Fin.ofNat 25 ((([[1, 0, 0, 0, 0], [15, 1, 0, 0, 0], [11, 6, 1, 0, 0], [19, 9, 12, 1, 0], [10, 17, 5, 3, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 5) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom155
