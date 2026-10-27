module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 2dc720281d959e04673c298ad9d895d017f469a37c63376ef9361ef402712839
   Canonical certificate JSON SHA256: 879322ece1b30a9966d84709615fb17a4f0ab4c90b0038962e37d54901eb9bb0
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom160
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 81
def actions : Fin 2 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 81 (((([[[67, 35, 20, 56, 25], [1, 1, 58, 54, 33], [42, 48, 80, 17, 7], [19, 54, 20, 20, 60], [39, 2, 29, 55, 65]], [[11, 57, 23, 51, 3], [23, 77, 48, 66, 33], [11, 4, 13, 43, 50], [8, 0, 66, 28, 26], [21, 42, 48, 55, 21]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 5 := fun i j => Fin.ofNat 81 ((([[30, 60, 25, 52, 17]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 81 (([30, 60, 25, 52, 17] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 81 (([73, 49, 80, 30, 2] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 81 (([4, 16, 43, 46, 7] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 81 (([38, 49, 20, 56, 19] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row3 row1_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 81 (([14, 76, 19, 7, 16] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 1) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row4 row1_sound row4_local x
def data : CertificateData R 5 5 2 1 5 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 81 ((([[66, 51, 1, 28, 59], [67, 1, 0, 67, 16], [48, 0, 0, 1, 62], [1, 0, 0, 0, 58], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 81 (((([[[68, 4, 0, 0, 0], [43, 77, 68, 67, 0], [24, 67, 66, 57, 21], [1, 19, 1, 51, 7], [29, 62, 30, 64, 52]], [[73, 49, 50, 0, 0], [56, 11, 46, 13, 5], [15, 39, 18, 44, 21], [53, 33, 32, 59, 17], [48, 24, 19, 3, 70]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 81 ((([[25, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([1, 0], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 81 ((([[13, 0, 0, 0, 0], [22, 64, 0, 0, 0], [68, 28, 44, 0, 0], [11, 12, 17, 7, 0], [59, 24, 9, 79, 29]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 5 5 := fun i j => Fin.ofNat 81 ((([[30, 60, 25, 52, 17], [73, 49, 80, 30, 2], [4, 16, 43, 46, 7], [38, 49, 20, 56, 19], [14, 76, 19, 7, 16]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.elim0 i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 81 (([1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 81 ((([[0, 0, 0, 1, 23], [0, 1, 14, 71, 20], [1, 30, 68, 6, 0], [0, 0, 1, 33, 49], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 81 ((([[66, 51, 1, 28, 59], [67, 1, 0, 67, 16], [48, 0, 0, 1, 62], [1, 0, 0, 0, 58], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 5 5 := fun i j => Fin.ofNat 81 ((([[1, 0, 0, 0, 0], [0, 1, 30, 0, 0], [1, 14, 30, 0, 0], [1, 71, 6, 33, 0], [23, 20, 0, 49, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 5) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom160
