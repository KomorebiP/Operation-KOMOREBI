import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 38353ca5829f641930b94f4594a5a02bf0152bb71e2fb82f4ef6c1f4c5881429
   Canonical certificate JSON SHA256: 534dfe38993a662972e66365f4a763b899222a99afd6ca3dbfe2eec6dbd8eeb7
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom088
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 243
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 243 (((([[[224, 222, 200, 133, 150, 117], [211, 27, 21, 16, 33, 38], [49, 200, 26, 194, 114, 187], [70, 139, 218, 132, 171, 192], [238, 0, 168, 230, 229, 236], [23, 70, 137, 144, 48, 203]], [[90, 175, 5, 73, 67, 160], [74, 133, 78, 68, 78, 162], [63, 229, 178, 221, 54, 180], [195, 221, 39, 206, 141, 168], [64, 86, 71, 3, 86, 88], [87, 215, 112, 35, 116, 178]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 243 ((([[179, 134, 33, 180, 172, 25]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 243 (([179, 134, 33, 180, 172, 25] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 243 (([168, 181, 225, 129, 211, 167] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 243 (([86, 11, 130, 146, 231, 166] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 243 (([6, 164, 181, 60, 109, 170] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row3 row1_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 243 (([135, 205, 169, 186, 162, 213] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 1) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 243 (([14, 29, 222, 219, 192, 133] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row2 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0, 1] 0 :=
  observed_row_prepend actions observations 0 [1] 0 row2 row5 row2_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 243 (([82, 212, 234, 164, 205, 108] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row2 (actions 1) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [1, 1] 0 :=
  observed_row_prepend actions observations 1 [1] 0 row2 row6 row2_sound row6_local x
def row7 : Vec R 6 := fun i => Fin.ofNat 243 (([121, 234, 185, 98, 4, 87] : List Nat).getD i.val 0)
theorem row7_local : ∀ i, row7 i = rm row5 (actions 1) i := by decide
theorem row7_sound (x : Vec R 6) : dot row7 x = behavior source x [1, 0, 1] 0 :=
  observed_row_prepend actions observations 1 [0, 1] 0 row5 row7 row5_sound row7_local x
def data : CertificateData R 6 6 2 1 8 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 243 ((([[1, 127, 102, 225, 134, 11], [0, 1, 45, 174, 187, 68], [0, 0, 1, 26, 236, 234], [0, 0, 0, 1, 78, 151], [0, 0, 0, 0, 1, 234], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 243 (((([[[210, 23, 0, 0, 0, 0], [159, 41, 70, 178, 0, 0], [239, 47, 120, 42, 98, 0], [237, 50, 52, 10, 38, 21], [31, 50, 84, 29, 171, 117], [23, 65, 212, 17, 35, 46]], [[67, 30, 38, 0, 0, 0], [48, 112, 73, 88, 30, 108], [14, 202, 104, 203, 49, 231], [99, 91, 34, 23, 59, 183], [10, 40, 131, 194, 64, 193], [87, 101, 58, 15, 154, 15]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 243 ((([[179, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([1, 0], 0), ([0, 1], 0), ([1, 1], 0), ([1, 0, 1], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 243 ((([[224, 0, 0, 0, 0, 0, 0, 0], [15, 52, 0, 0, 0, 0, 0, 0], [92, 138, 121, 0, 0, 0, 0, 0], [163, 241, 149, 145, 0, 0, 0, 0], [55, 36, 150, 93, 0, 212, 0, 0], [15, 78, 76, 73, 0, 13, 0, 206]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 8 6 := fun i j => Fin.ofNat 243 ((([[179, 134, 33, 180, 172, 25], [168, 181, 225, 129, 211, 167], [86, 11, 130, 146, 231, 166], [6, 164, 181, 60, 109, 170], [135, 205, 169, 186, 162, 213], [14, 29, 222, 219, 192, 133], [82, 212, 234, 164, 205, 108], [121, 234, 185, 98, 4, 87]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.cases (row6_sound) (fun i7 => Fin.cases (row7_sound) (fun i8 => Fin.elim0 i8) i7) i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 243 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 243 ((([[1, 116, 24, 108, 50, 30], [0, 1, 198, 24, 56, 52], [0, 0, 1, 217, 91, 137], [0, 0, 0, 1, 165, 119], [0, 0, 0, 0, 1, 9], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 243 ((([[1, 127, 102, 225, 134, 11], [0, 1, 45, 174, 187, 68], [0, 0, 1, 26, 236, 234], [0, 0, 0, 1, 78, 151], [0, 0, 0, 0, 1, 234], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 8 6 := fun i j => Fin.ofNat 243 ((([[1, 0, 0, 0, 0, 0], [116, 1, 0, 0, 0, 0], [24, 198, 1, 0, 0, 0], [108, 24, 217, 1, 0, 0], [50, 56, 91, 165, 1, 0], [162, 162, 81, 0, 81, 0], [27, 225, 18, 99, 81, 9], [0, 81, 162, 162, 0, 81]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 8) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom088
