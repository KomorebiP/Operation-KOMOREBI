import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 9d17dfdbb30bb1db0fcf7b2b273b60df0d4fd864ff0ed417ac28ea2829be748a
   Canonical certificate JSON SHA256: 5b20650eb5c1e74c4d4228103105709feb3331b58f791a3a1e3994b76bc5cbc4
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom085
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 81
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 81 (((([[[57, 35, 22, 33, 57, 75], [0, 10, 70, 69, 35, 58], [77, 52, 8, 19, 62, 65], [73, 28, 12, 12, 53, 42], [27, 54, 39, 54, 65, 45], [36, 45, 80, 11, 60, 55]], [[70, 22, 13, 58, 73, 9], [51, 22, 57, 80, 51, 44], [16, 48, 28, 5, 30, 13], [5, 32, 39, 39, 8, 55], [23, 65, 32, 31, 9, 44], [68, 1, 73, 37, 18, 19]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 81 ((([[15, 22, 30, 60, 51, 51], [78, 3, 10, 57, 17, 53]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 81 (([15, 22, 30, 60, 51, 51] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 81 (([78, 3, 10, 57, 17, 53] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 81 (([66, 43, 70, 57, 80, 64] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 81 (([60, 7, 21, 2, 33, 68] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 81 (([80, 79, 60, 53, 3, 31] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 81 (([9, 60, 1, 48, 15, 22] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 1) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [1] 1 :=
  observed_row_prepend actions observations 1 [] 1 row1 row5 row1_sound row5_local x
def data : CertificateData R 6 6 2 2 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 81 ((([[78, 1, 75, 69, 6, 6], [6, 0, 1, 12, 26, 62], [72, 0, 0, 69, 12, 1], [9, 0, 0, 1, 6, 0], [1, 0, 0, 0, 24, 0], [0, 0, 0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 81 (((([[[13, 37, 2, 0, 0, 0], [13, 18, 31, 5, 20, 0], [42, 53, 9, 32, 30, 38], [19, 72, 54, 78, 76, 80], [35, 34, 52, 21, 75, 79], [54, 39, 57, 27, 63, 14]], [[4, 36, 74, 77, 0, 0], [48, 64, 8, 18, 39, 37], [37, 13, 74, 28, 20, 31], [53, 18, 19, 18, 23, 17], [43, 67, 55, 40, 79, 29], [65, 17, 58, 7, 8, 29]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 81 ((([[22, 0, 0, 0, 0, 0], [3, 28, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)] : List (List (Fin 2) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 81 ((([[70, 0, 0, 0, 0, 0], [33, 55, 0, 0, 0, 0], [28, 76, 35, 0, 0, 0], [75, 38, 40, 23, 0, 0], [53, 50, 67, 55, 23, 0], [58, 69, 14, 39, 48, 19]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 81 ((([[15, 22, 30, 60, 51, 51], [78, 3, 10, 57, 17, 53], [66, 43, 70, 57, 80, 64], [60, 7, 21, 2, 33, 68], [80, 79, 60, 53, 3, 31], [9, 60, 1, 48, 15, 22]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 2)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 81 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 81 ((([[0, 0, 0, 0, 1, 57], [1, 6, 27, 21, 21, 18], [0, 1, 19, 54, 3, 79], [0, 0, 0, 1, 72, 48], [0, 0, 0, 0, 0, 1], [0, 0, 1, 12, 63, 24]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 81 ((([[78, 1, 75, 69, 6, 6], [6, 0, 1, 12, 26, 62], [72, 0, 0, 69, 12, 1], [9, 0, 0, 1, 6, 0], [1, 0, 0, 0, 24, 0], [0, 0, 0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 81 ((([[1, 0, 0, 0, 0, 0], [1, 3, 0, 0, 0, 0], [1, 48, 75, 0, 0, 0], [0, 21, 54, 1, 0, 12], [0, 36, 70, 75, 1, 78], [57, 18, 79, 48, 1, 24]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom085
