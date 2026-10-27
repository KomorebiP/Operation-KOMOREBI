import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 54de12d6cef65adba99aa0aadbea31969c8c9bd1b43c72400577b5add47247f2
   Canonical certificate JSON SHA256: 6e639c28417e51377bfde6318afc2ad2a320bff895375a7e349e6ba07c2ec6a0
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom140
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 25
def actions : Fin 3 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 25 (((([[[2, 17, 14, 23], [24, 22, 13, 7], [21, 1, 9, 10], [10, 13, 19, 21]], [[8, 8, 0, 21], [17, 7, 10, 12], [21, 19, 8, 22], [19, 10, 4, 24]], [[11, 20, 8, 1], [2, 11, 19, 0], [10, 13, 21, 22], [2, 3, 6, 23]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 4 := fun i j => Fin.ofNat 25 ((([[20, 0, 5, 5]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 25 (([20, 0, 5, 5] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 25 (([20, 10, 20, 15] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 25 (([10, 5, 10, 0] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 25 (([5, 5, 20, 20] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def data : CertificateData R 4 4 3 1 4 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 25 ((([[5, 0, 20, 20], [0, 5, 20, 5], [0, 0, 0, 5], [0, 0, 5, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 25 (((([[[1, 3, 0, 0], [3, 4, 2, 0], [0, 3, 3, 2], [1, 1, 0, 1]], [[3, 4, 4, 0], [0, 3, 1, 4], [4, 0, 3, 3], [1, 4, 4, 3]], [[4, 4, 1, 4], [4, 1, 4, 4], [2, 3, 2, 1], [0, 3, 4, 4]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 25 ((([[4, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 25 ((([[19, 0, 0, 0], [12, 13, 0, 0], [0, 12, 1, 0], [19, 14, 21, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 4 4 := fun i j => Fin.ofNat 25 ((([[20, 0, 5, 5], [20, 10, 20, 15], [10, 5, 10, 0], [5, 5, 20, 20]] : List (List Nat)).getD i.val []).getD j.val 0)
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
  weights := fun i => Fin.ofNat 25 (([5, 5, 5, 5] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 25 ((([[1, 0, 21, 21], [0, 1, 24, 21], [0, 0, 0, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 25 ((([[1, 0, 4, 4], [0, 1, 4, 1], [0, 0, 0, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 4 4 := fun i j => Fin.ofNat 25 ((([[1, 0, 0, 0], [0, 1, 0, 0], [21, 24, 0, 1], [21, 21, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 4) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom140
