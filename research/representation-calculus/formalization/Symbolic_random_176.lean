module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 8acf3c4cbe0ddf83c9f12785ec21a3070f9379e7717dbfbb4c22a1ed3528434e
   Canonical certificate JSON SHA256: 6cc6b46fd2877a352c3b91746c657299c8a9ca2d980be04ea1b7e6edb54c7171
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom176
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 625
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 625 (((([[[429, 206, 273, 402, 204, 349], [282, 379, 580, 539, 276, 265], [382, 104, 517, 231, 468, 18], [484, 523, 367, 118, 187, 596], [437, 365, 540, 560, 341, 274], [433, 86, 196, 433, 551, 393]], [[366, 34, 563, 282, 62, 163], [583, 449, 60, 491, 356, 580], [464, 239, 440, 181, 116, 138], [226, 306, 457, 151, 390, 418], [104, 295, 24, 536, 485, 70], [424, 248, 363, 585, 102, 357]], [[263, 161, 442, 343, 105, 225], [333, 425, 11, 474, 170, 561], [411, 355, 334, 334, 125, 145], [445, 145, 515, 334, 471, 455], [358, 432, 289, 359, 525, 174], [596, 128, 71, 584, 271, 63]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 625 ((([[134, 345, 136, 619, 577, 579]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 625 (([134, 345, 136, 619, 577, 579] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 625 (([430, 389, 481, 608, 243, 208] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 625 (([556, 186, 390, 130, 342, 295] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 625 (([3, 235, 94, 66, 478, 60] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 625 (([312, 602, 561, 280, 109, 7] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 625 (([98, 432, 12, 556, 256, 623] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 1) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row5 row1_sound row5_local x
def data : CertificateData R 6 6 3 1 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 625 ((([[1, 455, 29, 541, 578, 606], [0, 1, 374, 252, 27, 102], [0, 0, 1, 476, 396, 501], [0, 0, 0, 1, 337, 500], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 625 (((([[[395, 96, 0, 0, 0, 0], [458, 58, 395, 541, 314, 0], [126, 598, 564, 266, 482, 88], [503, 163, 423, 166, 144, 423], [245, 226, 357, 314, 365, 423], [433, 571, 335, 328, 414, 4]], [[284, 259, 358, 0, 0, 0], [252, 548, 198, 453, 248, 28], [398, 248, 45, 39, 590, 314], [399, 301, 275, 47, 97, 515], [528, 303, 503, 314, 341, 209], [424, 453, 520, 150, 79, 358]], [[42, 430, 528, 389, 0, 0], [395, 355, 527, 437, 448, 145], [95, 100, 334, 362, 499, 589], [341, 199, 343, 420, 557, 624], [329, 240, 434, 265, 485, 339], [596, 198, 610, 392, 523, 308]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 625 ((([[134, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0), ([1, 0], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 625 ((([[14, 0, 0, 0, 0, 0], [320, 534, 0, 0, 0, 0], [543, 518, 433, 0, 0, 0], [222, 384, 259, 376, 0, 0], [294, 496, 64, 431, 356, 0], [540, 548, 429, 278, 329, 153]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 625 ((([[134, 345, 136, 619, 577, 579], [430, 389, 481, 608, 243, 208], [556, 186, 390, 130, 342, 295], [3, 235, 94, 66, 478, 60], [312, 602, 561, 280, 109, 7], [98, 432, 12, 556, 256, 623]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 3)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 625 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 625 ((([[1, 170, 141, 128, 235, 303], [0, 1, 251, 272, 163, 484], [0, 0, 1, 149, 16, 608], [0, 0, 0, 1, 288, 462], [0, 0, 0, 0, 1, 624], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 625 ((([[1, 455, 29, 541, 578, 606], [0, 1, 374, 252, 27, 102], [0, 0, 1, 476, 396, 501], [0, 0, 0, 1, 337, 500], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 625 ((([[1, 0, 0, 0, 0, 0], [170, 1, 0, 0, 0, 0], [141, 251, 1, 0, 0, 0], [128, 272, 149, 1, 0, 0], [235, 163, 16, 288, 1, 0], [303, 484, 608, 462, 624, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom176
