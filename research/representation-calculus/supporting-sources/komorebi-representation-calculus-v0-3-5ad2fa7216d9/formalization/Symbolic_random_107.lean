import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: f7212a7c578d38bb9199b6652143b075fbc2f45f090694e789902c899f5cacfa
   Canonical certificate JSON SHA256: 029e0233de1eafc64d1089cdc1a87e618b581692277dcb9335dc47986f2d597f
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom107
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 5
def actions : Fin 3 → Mat R 2 2 :=
  fun a i j => Fin.ofNat 5 (((([[[0, 1], [2, 0]], [[3, 2], [2, 2]], [[3, 3], [3, 0]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 2 := fun i j => Fin.ofNat 5 ((([[0, 4], [4, 4]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 2 := fun i => Fin.ofNat 5 (([0, 4] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 2) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 2 := fun i => Fin.ofNat 5 (([4, 4] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 2) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def data : CertificateData R 2 2 3 2 2 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 5 ((([[0, 1], [1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 5 (((([[[0, 2], [1, 0]], [[2, 2], [2, 3]], [[0, 3], [3, 3]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 5 ((([[4, 0], [4, 4]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 5 ((([[4, 0], [1, 4]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 2 2 := fun i j => Fin.ofNat 5 ((([[0, 4], [4, 4]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.elim0 i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 2) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 2) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 2 2 where
  width := by decide
  weights := fun i => Fin.ofNat 5 (([1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 5 ((([[0, 1], [1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 5 ((([[0, 1], [1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 2) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 2 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 2 2 := fun i j => Fin.ofNat 5 ((([[0, 1], [1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 2) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom107
