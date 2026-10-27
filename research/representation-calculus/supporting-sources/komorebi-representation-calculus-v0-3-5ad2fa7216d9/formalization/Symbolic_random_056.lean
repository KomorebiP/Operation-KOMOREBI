import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 298def308389ae3ef2e83c24fff82a93cba74c2061855363b7fa169d522b203b
   Canonical certificate JSON SHA256: 0634ac0c4ee4e4e57c8552ec6ee4e290b573920a3ba7d475f5517fe3551dffa1
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom056
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 625
def actions : Fin 3 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 625 (((([[[299, 527, 250, 441], [451, 406, 318, 302], [234, 59, 177, 312], [469, 250, 252, 243]], [[395, 164, 160, 582], [136, 189, 328, 150], [406, 53, 261, 547], [64, 432, 561, 139]], [[531, 303, 385, 393], [417, 43, 51, 304], [74, 386, 27, 527], [43, 437, 313, 578]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 4 := fun i j => Fin.ofNat 625 ((([[375, 0, 250, 250]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 625 (([375, 0, 250, 250] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 625 (([375, 500, 375, 375] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 625 (([0, 250, 500, 375] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 625 (([250, 0, 0, 500] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def data : CertificateData R 4 4 3 1 4 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 625 ((([[125, 0, 500, 500], [0, 125, 500, 500], [0, 0, 125, 0], [0, 0, 0, 125]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 625 (((([[[1, 3, 0, 0], [3, 2, 4, 2], [4, 4, 0, 0], [4, 0, 1, 2]], [[0, 4, 2, 0], [1, 4, 1, 4], [1, 3, 0, 1], [4, 2, 2, 0]], [[4, 0, 4, 2], [0, 0, 1, 4], [4, 1, 2, 2], [3, 2, 3, 3]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 625 ((([[3, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 625 ((([[417, 0, 0, 0], [156, 469, 0, 0], [313, 312, 1, 0], [415, 1, 623, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 4 4 := fun i j => Fin.ofNat 625 ((([[375, 0, 250, 250], [375, 500, 375, 375], [0, 250, 500, 375], [250, 0, 0, 500]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.elim0 i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 4) (w : List (Fin 3)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 4) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 4 4 where
  width := by decide
  weights := fun i => Fin.ofNat 625 (([125, 125, 125, 125] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 625 ((([[1, 0, 621, 621], [0, 1, 621, 621], [0, 0, 1, 0], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 625 ((([[1, 0, 4, 4], [0, 1, 4, 4], [0, 0, 1, 0], [0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 4 4 := fun i j => Fin.ofNat 625 ((([[1, 0, 0, 0], [0, 1, 0, 0], [621, 621, 1, 0], [621, 621, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 4) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom056
