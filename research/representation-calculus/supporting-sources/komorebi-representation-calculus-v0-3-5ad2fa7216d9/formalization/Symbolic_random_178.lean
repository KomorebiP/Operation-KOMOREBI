import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 8d3b3339f90d72f95652702c3ac1cb867632a1387a6431430dff636d23bf82ed
   Canonical certificate JSON SHA256: 5a430afa9676c93f9536aacb4a04f38711cac326f8a8f1c607e09618fb62fbe3
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom178
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 243
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 243 (((([[[242, 109, 5, 6, 147, 34], [147, 58, 207, 197, 156, 219], [142, 172, 72, 188, 195, 173], [99, 209, 29, 163, 85, 3], [123, 122, 208, 228, 2, 39], [241, 118, 23, 199, 115, 20]], [[226, 231, 182, 184, 127, 210], [135, 157, 143, 221, 174, 164], [174, 87, 27, 36, 135, 32], [48, 182, 0, 231, 100, 12], [114, 22, 46, 185, 157, 91], [118, 211, 135, 156, 131, 76]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 243 ((([[171, 184, 158, 224, 142, 55]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 243 (([171, 184, 158, 224, 142, 55] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 243 (([150, 28, 136, 39, 221, 78] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 243 (([235, 94, 84, 142, 116, 50] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 243 (([220, 147, 107, 4, 55, 101] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row1 (actions 0) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row3 row1_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 243 (([171, 78, 25, 144, 215, 126] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 1) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 243 (([34, 232, 187, 8, 49, 215] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row2 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0, 1] 0 :=
  observed_row_prepend actions observations 0 [1] 0 row2 row5 row2_sound row5_local x
def data : CertificateData R 6 6 2 1 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 243 ((([[63, 1, 125, 128, 220, 205], [111, 0, 1, 41, 221, 94], [1, 0, 0, 234, 116, 66], [0, 0, 0, 60, 1, 231], [0, 0, 0, 1, 0, 233], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 243 (((([[[16, 230, 0, 0, 0, 0], [88, 66, 233, 164, 0, 0], [242, 0, 185, 58, 227, 214], [68, 219, 93, 45, 224, 3], [1, 160, 35, 119, 212, 133], [118, 96, 133, 205, 188, 33]], [[19, 103, 175, 0, 0, 0], [52, 135, 55, 192, 56, 0], [5, 195, 61, 86, 91, 67], [148, 95, 177, 239, 158, 51], [16, 52, 107, 40, 101, 92], [211, 4, 232, 30, 2, 76]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 243 ((([[184, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([0, 0], 0), ([1, 0], 0), ([0, 1], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 243 ((([[70, 0, 0, 0, 0, 0], [217, 32, 0, 0, 0, 0], [166, 220, 49, 0, 0, 0], [66, 193, 83, 178, 0, 0], [77, 208, 27, 84, 70, 0], [40, 35, 95, 168, 196, 124]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 243 ((([[171, 184, 158, 224, 142, 55], [150, 28, 136, 39, 221, 78], [235, 94, 84, 142, 116, 50], [220, 147, 107, 4, 55, 101], [171, 78, 25, 144, 215, 126], [34, 232, 187, 8, 49, 215]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
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
  change := fun i j => Fin.ofNat 243 ((([[0, 0, 1, 127, 165, 192], [1, 118, 204, 96, 101, 0], [0, 1, 132, 19, 7, 240], [0, 0, 0, 0, 1, 10], [0, 0, 0, 1, 183, 141], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 243 ((([[63, 1, 125, 128, 220, 205], [111, 0, 1, 41, 221, 94], [1, 0, 0, 234, 116, 66], [0, 0, 0, 60, 1, 231], [0, 0, 0, 1, 0, 233], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 243 ((([[1, 0, 0, 0, 0, 0], [1, 180, 0, 0, 0, 0], [1, 204, 132, 0, 0, 0], [9, 29, 175, 1, 0, 0], [165, 101, 7, 1, 183, 0], [192, 0, 240, 10, 141, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom178
