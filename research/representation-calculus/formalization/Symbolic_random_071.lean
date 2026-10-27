module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 3d99584f5d299f99e2f76f4faac512bdd4a68c6dc02be3d6d7e9474cd5091d37
   Canonical certificate JSON SHA256: a9a47bd8eccd2f3d179d7820102c461f852de85b1e4bff2e45ab54b52fd8aa95
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom071
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 625
def actions : Fin 3 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 625 (((([[[229, 287, 50, 317, 544], [192, 326, 502, 259, 466], [239, 6, 59, 596, 134], [283, 460, 37, 549, 29], [545, 154, 354, 501, 561]], [[228, 153, 350, 589, 583], [308, 252, 467, 249, 140], [445, 375, 621, 543, 346], [512, 323, 353, 27, 602], [400, 76, 346, 528, 58]], [[82, 101, 106, 233, 309], [387, 35, 357, 162, 203], [619, 6, 428, 317, 154], [236, 163, 175, 392, 141], [253, 283, 491, 528, 194]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 5 := fun i j => Fin.ofNat 625 ((([[467, 203, 247, 46, 165], [354, 10, 202, 138, 248]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 625 (([467, 203, 247, 46, 165] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 625 (([354, 10, 202, 138, 248] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 625 (([395, 134, 566, 122, 18] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 625 (([342, 130, 591, 593, 280] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 625 (([474, 572, 504, 148, 171] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def row5 : Vec R 5 := fun i => Fin.ofNat 625 (([478, 242, 36, 210, 559] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 0) i := by decide
theorem row5_sound (x : Vec R 5) : dot row5 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row5 row1_sound row5_local x
def data : CertificateData R 5 5 3 2 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 625 ((([[1, 509, 216, 63, 620], [0, 1, 412, 339, 507], [0, 0, 1, 472, 405], [0, 0, 0, 1, 394], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 625 (((([[[310, 437, 619, 0, 0], [287, 108, 343, 590, 236], [165, 511, 346, 68, 228], [13, 144, 502, 114, 519], [545, 249, 46, 43, 221]], [[251, 381, 260, 362, 0], [16, 262, 8, 337, 529], [359, 255, 388, 554, 74], [612, 9, 152, 333, 439], [400, 226, 209, 66, 577]], [[622, 218, 544, 238, 180], [565, 535, 620, 500, 163], [101, 148, 341, 444, 204], [543, 278, 555, 513, 199], [253, 256, 371, 193, 370]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 625 ((([[467, 0, 0, 0, 0], [354, 449, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 625 ((([[178, 0, 0, 0, 0, 0], [287, 174, 0, 0, 0, 0], [204, 173, 387, 0, 0, 0], [255, 473, 240, 294, 0, 0], [286, 184, 486, 515, 0, 59]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 5 := fun i j => Fin.ofNat 625 ((([[467, 203, 247, 46, 165], [354, 10, 202, 138, 248], [395, 134, 566, 122, 18], [342, 130, 591, 593, 280], [474, 572, 504, 148, 171], [478, 242, 36, 210, 559]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 625 (([1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 625 ((([[1, 116, 117, 389, 542], [0, 1, 213, 375, 478], [0, 0, 1, 153, 563], [0, 0, 0, 1, 231], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 625 ((([[1, 509, 216, 63, 620], [0, 1, 412, 339, 507], [0, 0, 1, 472, 405], [0, 0, 0, 1, 394], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 5 := fun i j => Fin.ofNat 625 ((([[1, 0, 0, 0, 0], [116, 1, 0, 0, 0], [117, 213, 1, 0, 0], [389, 375, 153, 1, 0], [542, 478, 563, 231, 1], [250, 375, 375, 125, 125]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom071
