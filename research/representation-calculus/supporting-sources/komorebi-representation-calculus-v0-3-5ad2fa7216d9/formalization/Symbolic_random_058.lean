import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 5b7f61a4a9816ec00ee293c1a7faaf8274214400292e141d2a3d4ac51b165fba
   Canonical certificate JSON SHA256: 18d0a552b9f0d804e59d117cc8d84780b121dd30f6d9ea5f5afc2e41b8dcb546
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom058
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 243
def actions : Fin 2 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 243 (((([[[96, 129, 204, 234], [194, 196, 159, 228], [178, 201, 118, 143], [12, 26, 131, 234]], [[66, 22, 62, 139], [217, 167, 237, 211], [120, 101, 225, 199], [203, 203, 6, 98]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 4 := fun i j => Fin.ofNat 243 ((([[206, 231, 30, 207]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 243 (([206, 231, 30, 207] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 243 (([0, 156, 60, 24] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 243 (([237, 194, 181, 113] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 243 (([165, 6, 36, 192] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row3 row1_sound row3_local x
def row4 : Vec R 4 := fun i => Fin.ofNat 243 (([164, 24, 173, 140] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row2 (actions 0) i := by decide
theorem row4_sound (x : Vec R 4) : dot row4 x = behavior source x [0, 1] 0 :=
  observed_row_prepend actions observations 0 [1] 0 row2 row4 row2_sound row4_local x
def row5 : Vec R 4 := fun i => Fin.ofNat 243 (([96, 100, 15, 199] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row2 (actions 1) i := by decide
theorem row5_sound (x : Vec R 4) : dot row5 x = behavior source x [1, 1] 0 :=
  observed_row_prepend actions observations 1 [1] 0 row2 row5 row2_sound row5_local x
def data : CertificateData R 4 4 2 1 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 243 ((([[1, 66, 78, 198], [0, 1, 74, 127], [0, 0, 1, 112], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 243 (((([[[0, 114, 225, 42], [67, 99, 97, 180], [64, 104, 158, 28], [12, 206, 232, 144]], [[33, 76, 0, 0], [129, 122, 17, 238], [14, 43, 25, 142], [203, 170, 23, 133]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 243 ((([[206, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([0, 1], 0), ([1, 1], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 243 ((([[197, 0, 0, 0, 0, 0], [231, 0, 236, 0, 0, 0], [7, 0, 27, 0, 170, 0], [148, 0, 215, 0, 92, 50]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 4 := fun i j => Fin.ofNat 243 ((([[206, 231, 30, 207], [0, 156, 60, 24], [237, 194, 181, 113], [165, 6, 36, 192], [164, 24, 173, 140], [96, 100, 15, 199]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 4) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 4) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 4 4 where
  width := by decide
  weights := fun i => Fin.ofNat 243 (([1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 243 ((([[1, 177, 189, 138], [0, 1, 169, 142], [0, 0, 1, 131], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 243 ((([[1, 66, 78, 198], [0, 1, 74, 127], [0, 0, 1, 112], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 4 := fun i j => Fin.ofNat 243 ((([[1, 0, 0, 0], [177, 1, 0, 0], [0, 81, 0, 0], [90, 229, 1, 210], [0, 162, 0, 81], [0, 81, 162, 81]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom058
