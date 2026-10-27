import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: a78f443dfad9eb51bf4a39a97d94f2913fff09c513c621e26b8c719e9218bdec
   Canonical certificate JSON SHA256: 1028fd32477ccd6bb4094a0299544ef3c66bf428ab2683d8096c89ce93f9c1a5
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom038
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 125
def actions : Fin 3 → Mat R 3 3 :=
  fun a i j => Fin.ofNat 125 (((([[[18, 14, 51], [35, 91, 21], [104, 16, 39]], [[35, 111, 1], [82, 58, 68], [22, 85, 107]], [[86, 36, 8], [94, 45, 23], [55, 13, 20]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 3 := fun i j => Fin.ofNat 125 ((([[83, 54, 59]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 3 := fun i => Fin.ofNat 125 (([83, 54, 59] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 3) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 3 := fun i => Fin.ofNat 125 (([20, 20, 43] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 3) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 3 := fun i => Fin.ofNat 125 (([6, 110, 68] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 3) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def data : CertificateData R 3 3 3 1 3 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 125 ((([[1, 88, 73], [0, 95, 1], [0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 125 (((([[[65, 1, 0], [54, 92, 44], [35, 91, 116]], [[107, 110, 54], [62, 41, 119], [82, 82, 52]], [[123, 13, 11], [110, 50, 108], [94, 36, 103]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 125 ((([[83, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 125 ((([[122, 0, 0], [70, 122, 0], [74, 20, 118]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 3 3 := fun i j => Fin.ofNat 125 ((([[83, 54, 59], [20, 20, 43], [6, 110, 68]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.elim0 i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 3) (w : List (Fin 3)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 3) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 3 3 where
  width := by decide
  weights := fun i => Fin.ofNat 125 (([1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 125 ((([[1, 52, 97], [0, 0, 1], [0, 1, 30]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 125 ((([[1, 88, 73], [0, 95, 1], [0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 3) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 3 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 3 3 := fun i j => Fin.ofNat 125 ((([[1, 0, 0], [37, 1, 0], [97, 1, 30]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 3) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom038
