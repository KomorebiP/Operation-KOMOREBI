import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 1ffc9ea9aa6868a452ffd5c5cb017deaa2fa9540bfa92e3a3f232b125cf43bf6
   Canonical certificate JSON SHA256: 0977e755f337dac9dfab7e66950333c4932ca246928c1751e6ae29755f72af3d
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom053
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 125
def actions : Fin 3 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 125 (((([[[122, 32, 47, 33], [15, 16, 4, 91], [81, 96, 28, 33], [0, 107, 7, 111]], [[19, 62, 92, 116], [56, 67, 116, 89], [89, 50, 99, 79], [12, 78, 75, 119]], [[48, 106, 46, 6], [56, 113, 122, 95], [40, 16, 104, 121], [21, 82, 16, 58]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 4 := fun i j => Fin.ofNat 125 ((([[104, 94, 58, 17], [44, 98, 58, 7]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 125 (([104, 94, 58, 17] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 125 (([44, 98, 58, 7] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 125 (([46, 94, 7, 37] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 125 (([106, 97, 114, 35] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def data : CertificateData R 4 4 3 2 4 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 125 ((([[1, 61, 27, 23], [0, 1, 80, 80], [0, 0, 25, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 125 (((([[[99, 22, 116, 0], [120, 61, 96, 34], [25, 107, 51, 72], [81, 30, 20, 66]], [[114, 89, 48, 43], [11, 11, 46, 84], [112, 121, 88, 21], [89, 121, 102, 91]], [[27, 45, 56, 60], [61, 107, 77, 90], [21, 76, 20, 94], [40, 76, 121, 44]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 125 ((([[104, 0, 0, 0], [44, 39, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 125 ((([[119, 0, 0, 0], [26, 109, 0, 0], [67, 72, 84, 0], [53, 101, 101, 58]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 4 4 := fun i j => Fin.ofNat 125 ((([[104, 94, 58, 17], [44, 98, 58, 7], [46, 94, 7, 37], [106, 97, 114, 35]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.elim0 i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 4) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 4) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 4 4 where
  width := by decide
  weights := fun i => Fin.ofNat 125 (([1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 125 ((([[1, 64, 107, 53], [0, 1, 45, 45], [0, 0, 0, 1], [0, 0, 1, 100]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 125 ((([[1, 61, 27, 23], [0, 1, 80, 80], [0, 0, 25, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 4 4 := fun i j => Fin.ofNat 125 ((([[1, 0, 0, 0], [64, 1, 0, 0], [103, 45, 1, 0], [53, 45, 1, 100]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 4) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom053
