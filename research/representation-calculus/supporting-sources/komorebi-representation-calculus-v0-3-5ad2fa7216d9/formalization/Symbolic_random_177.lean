import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: a3464b87c1722e6687060aecebfa418c2dec8088f1792dc76b260673691a839b
   Canonical certificate JSON SHA256: a891d6c5dbae32d8b058dd12843c1491bd5e5493bf2e5a7ed869dbbbe6ac38e4
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom177
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 32
def actions : Fin 1 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 32 (((([[[27, 8, 24, 27, 3, 0], [29, 18, 26, 18, 29, 18], [3, 21, 12, 22, 10, 6], [31, 15, 4, 28, 11, 23], [19, 24, 14, 31, 26, 31], [25, 11, 17, 25, 15, 7]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 32 ((([[11, 13, 19, 21, 3, 26], [10, 14, 5, 3, 31, 16]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 32 (([11, 13, 19, 21, 3, 26] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 32 (([10, 14, 5, 3, 31, 16] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 32 (([9, 18, 22, 8, 19, 18] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 32 (([13, 26, 6, 29, 29, 16] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row3 row1_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 32 (([2, 0, 16, 10, 21, 11] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row2 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row2 row4 row2_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 32 (([29, 21, 30, 22, 22, 6] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row3 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0, 0] 1 :=
  observed_row_prepend actions observations 0 [0] 1 row3 row5 row3_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 32 (([30, 7, 25, 12, 27, 30] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row4 (actions 0) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0] 0 row4 row6 row4_sound row6_local x
def data : CertificateData R 6 6 1 2 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 32 ((([[1, 7, 25, 31, 9, 14], [0, 24, 1, 7, 15, 12], [0, 1, 0, 26, 5, 8], [0, 0, 0, 1, 14, 14], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 32 (((([[[27, 31, 17, 0, 0, 0], [29, 1, 23, 7, 0, 0], [10, 22, 18, 9, 25, 0], [7, 7, 0, 2, 5, 20], [12, 19, 7, 9, 31, 5], [25, 0, 28, 26, 22, 7]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 32 ((([[11, 0, 0, 0, 0, 0], [10, 11, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([0], 1), ([0, 0], 0), ([0, 0], 1), ([0, 0, 0], 0)] : List (List (Fin 1) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 32 ((([[3, 0, 0, 0, 0, 0, 0], [6, 3, 0, 0, 0, 0, 0], [5, 19, 19, 0, 0, 0, 0], [16, 24, 7, 5, 0, 0, 0], [20, 16, 16, 22, 11, 0, 0], [25, 16, 20, 29, 7, 0, 23]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 32 ((([[11, 13, 19, 21, 3, 26], [10, 14, 5, 3, 31, 16], [9, 18, 22, 8, 19, 18], [13, 26, 6, 29, 29, 16], [2, 0, 16, 10, 21, 11], [29, 21, 30, 22, 22, 6], [30, 7, 25, 12, 27, 30]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.cases (row6_sound) (fun i7 => Fin.elim0 i7) i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 1)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 32 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 32 ((([[1, 7, 17, 22, 5, 29], [0, 0, 1, 6, 7, 29], [0, 1, 8, 9, 11, 11], [0, 0, 0, 1, 18, 0], [0, 0, 0, 0, 1, 31], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 32 ((([[1, 7, 25, 31, 9, 14], [0, 24, 1, 7, 15, 12], [0, 1, 0, 26, 5, 8], [0, 0, 0, 1, 14, 14], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 1) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 32 ((([[1, 0, 0, 0, 0, 0], [25, 1, 0, 0, 0, 0], [17, 1, 8, 0, 0, 0], [22, 6, 9, 1, 0, 0], [5, 7, 11, 18, 1, 0], [29, 29, 11, 0, 31, 1], [8, 8, 24, 0, 24, 8]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom177
