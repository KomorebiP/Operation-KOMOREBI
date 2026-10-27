import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 833e6465ad2e7a6861ac632f49185fe8caee595c4b8baf3cc8092a2650a9b025
   Canonical certificate JSON SHA256: 214f9b0175f1c704b5f51b7086dc372a3aef817e5555bdd9e00da831938d9aa4
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom171
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 8
def actions : Fin 1 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 8 (((([[[6, 3, 5, 4, 6, 2], [4, 1, 2, 6, 0, 1], [7, 2, 5, 7, 4, 0], [6, 3, 4, 1, 3, 0], [7, 1, 4, 0, 0, 5], [6, 4, 4, 1, 2, 7]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 8 ((([[0, 3, 3, 3, 6, 7], [0, 6, 0, 6, 2, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 8 (([0, 3, 3, 3, 6, 7] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 8 (([0, 6, 0, 6, 2, 2] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 8 (([7, 4, 5, 1, 3, 2] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 8 (([6, 2, 4, 4, 6, 6] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row3 row1_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 8 (([4, 1, 4, 2, 5, 7] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row2 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row2 row4 row2_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 8 (([1, 4, 2, 3, 4, 3] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row4 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0] 0 row4 row5 row4_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 8 (([4, 4, 7, 0, 5, 7] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row5 (actions 0) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [0, 0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0, 0] 0 row5 row6 row5_sound row6_local x
def data : CertificateData R 6 6 1 2 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 8 ((([[0, 1, 1, 1, 2, 5], [1, 0, 7, 3, 5, 2], [0, 0, 1, 3, 1, 6], [0, 0, 0, 1, 0, 5], [0, 0, 0, 0, 4, 2], [0, 0, 0, 0, 2, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 8 (((([[[4, 5, 0, 0, 0, 0], [7, 0, 1, 0, 0, 0], [4, 4, 5, 1, 0, 0], [7, 4, 5, 4, 3, 1], [4, 0, 4, 2, 2, 0], [2, 6, 4, 0, 2, 1]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 8 ((([[3, 0, 0, 0, 0, 0], [6, 0, 2, 2, 3, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([0], 1), ([0, 0], 0), ([0, 0, 0], 0), ([0, 0, 0, 0], 0)] : List (List (Fin 1) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 8 ((([[3, 0, 0, 0, 0, 0, 0], [4, 0, 7, 0, 0, 0, 0], [3, 0, 4, 0, 7, 0, 0], [5, 0, 3, 0, 1, 7, 0], [2, 3, 6, 0, 0, 6, 0], [2, 7, 3, 0, 4, 7, 3]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 8 ((([[0, 3, 3, 3, 6, 7], [0, 6, 0, 6, 2, 2], [7, 4, 5, 1, 3, 2], [6, 2, 4, 4, 6, 6], [4, 1, 4, 2, 5, 7], [1, 4, 2, 3, 4, 3], [4, 4, 7, 0, 5, 7]] : List (List Nat)).getD i.val []).getD j.val 0)
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
  weights := fun i => Fin.ofNat 8 (([1, 1, 1, 1, 2, 2] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 8 ((([[0, 1, 1, 2, 6, 6], [1, 0, 7, 2, 7, 1], [0, 0, 1, 5, 1, 5], [0, 0, 0, 1, 3, 2], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 1, 6]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 8 ((([[0, 1, 1, 1, 2, 5], [1, 0, 7, 3, 5, 2], [0, 0, 1, 3, 1, 6], [0, 0, 0, 1, 0, 5], [0, 0, 0, 0, 2, 1], [0, 0, 0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 1) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 8 ((([[0, 1, 0, 0, 0, 0], [0, 7, 1, 0, 0, 0], [0, 4, 4, 0, 0, 0], [0, 1, 5, 0, 1, 0], [4, 4, 4, 0, 0, 0], [0, 0, 4, 4, 0, 0], [4, 2, 2, 4, 2, 4]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom171
