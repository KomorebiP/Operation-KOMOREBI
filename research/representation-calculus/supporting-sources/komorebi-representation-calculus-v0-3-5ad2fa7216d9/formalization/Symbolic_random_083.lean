import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 3f44dd77bf0fe5c391f350503672d728dcc3be88655666e17d3b64ee0c69868b
   Canonical certificate JSON SHA256: 4321a9be3e3576190674046e25ab3e9be8d57980288f5be7d35ba17c5ac9ead5
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom083
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 125
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 125 (((([[[68, 99, 104, 107, 33, 11], [97, 106, 110, 103, 17, 96], [51, 57, 47, 103, 82, 66], [58, 15, 85, 59, 95, 81], [3, 67, 122, 121, 98, 120], [91, 39, 122, 45, 6, 50]], [[119, 124, 124, 6, 103, 71], [82, 53, 82, 119, 82, 30], [27, 56, 41, 104, 13, 68], [69, 112, 12, 58, 21, 78], [106, 79, 40, 32, 49, 55], [17, 78, 96, 104, 68, 96]], [[61, 117, 70, 90, 4, 119], [112, 51, 77, 83, 59, 72], [55, 37, 109, 105, 68, 21], [26, 24, 80, 9, 79, 55], [9, 52, 88, 62, 41, 55], [124, 110, 122, 64, 60, 17]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 125 ((([[43, 20, 70, 92, 82, 15], [6, 1, 112, 77, 90, 28]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 125 (([43, 20, 70, 92, 82, 15] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 125 (([6, 1, 112, 77, 90, 28] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 125 (([6, 76, 116, 21, 115, 55] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 125 (([67, 14, 41, 63, 74, 39] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 125 (([78, 13, 86, 2, 17, 102] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 125 (([1, 111, 64, 99, 77, 116] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row5 row1_sound row5_local x
def data : CertificateData R 6 6 3 2 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 125 ((([[1, 15, 115, 69, 124, 105], [0, 1, 102, 8, 86, 18], [0, 0, 1, 61, 50, 63], [0, 0, 0, 110, 1, 49], [0, 0, 0, 1, 0, 45], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 125 (((([[[67, 52, 78, 0, 0, 0], [34, 119, 99, 27, 115, 124], [97, 74, 65, 13, 32, 93], [92, 123, 74, 31, 60, 100], [28, 100, 30, 43, 42, 79], [91, 49, 34, 58, 45, 104]], [[19, 38, 1, 69, 0, 0], [60, 84, 60, 100, 93, 121], [107, 22, 22, 18, 38, 15], [29, 36, 57, 24, 102, 39], [84, 112, 123, 8, 38, 86], [17, 73, 70, 57, 57, 104]], [[121, 101, 35, 104, 82, 0], [61, 54, 76, 100, 72, 10], [28, 111, 33, 49, 63, 69], [70, 32, 52, 14, 15, 0], [106, 9, 87, 11, 111, 13], [124, 0, 112, 84, 61, 80]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 125 ((([[43, 0, 0, 0, 0, 0], [6, 36, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 125 ((([[32, 0, 0, 0, 0, 0], [78, 66, 0, 0, 0, 0], [100, 81, 119, 0, 0, 0], [12, 44, 49, 53, 0, 0], [61, 89, 102, 9, 101, 0], [109, 46, 6, 91, 115, 59]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 125 ((([[43, 20, 70, 92, 82, 15], [6, 1, 112, 77, 90, 28], [6, 76, 116, 21, 115, 55], [67, 14, 41, 63, 74, 39], [78, 13, 86, 2, 17, 102], [1, 111, 64, 99, 77, 116]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 125 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 125 ((([[1, 110, 40, 41, 101, 91], [0, 1, 23, 14, 49, 17], [0, 0, 1, 75, 64, 7], [0, 0, 0, 0, 1, 80], [0, 0, 0, 1, 15, 26], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 125 ((([[1, 15, 115, 69, 124, 105], [0, 1, 102, 8, 86, 18], [0, 0, 1, 61, 50, 63], [0, 0, 0, 110, 1, 49], [0, 0, 0, 1, 0, 45], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 125 ((([[1, 0, 0, 0, 0, 0], [110, 1, 0, 0, 0, 0], [40, 23, 1, 0, 0, 0], [111, 89, 64, 1, 0, 0], [101, 49, 64, 1, 15, 0], [91, 17, 7, 80, 26, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom083
