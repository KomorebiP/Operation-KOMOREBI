module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 464feda35dd11044dcdaf252614f994828b4086a03a516a75f05b040ef704a1b
   Canonical certificate JSON SHA256: f9648c23e4fc76e3412584d32d656242010d43d90828461584e17f6c4a6c99fa
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic107
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 625
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 625 (((([[[77, 439, 412, 410, 606, 239], [396, 89, 51, 94, 573, 290], [340, 167, 288, 569, 315, 448], [550, 80, 25, 398, 150, 495], [577, 338, 287, 225, 337, 207], [441, 308, 184, 119, 141, 111]], [[348, 157, 144, 109, 325, 590], [380, 464, 610, 482, 377, 38], [545, 515, 225, 59, 505, 80], [614, 560, 497, 438, 127, 19], [274, 333, 100, 90, 593, 222], [21, 434, 596, 341, 218, 16]], [[165, 427, 489, 136, 195, 230], [115, 173, 394, 535, 150, 342], [194, 330, 208, 577, 582, 402], [423, 71, 414, 177, 607, 177], [433, 135, 182, 55, 287, 595], [550, 498, 592, 170, 73, 69]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 6 := fun i j => Fin.ofNat 625 ((([[377, 601, 552, 440, 45, 153]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 625 (([377, 601, 552, 440, 45, 153] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 625 (([143, 585, 143, 479, 78, 162] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 625 (([494, 120, 91, 411, 31, 226] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 625 (([38, 621, 14, 176, 468, 618] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 625 (([564, 178, 354, 582, 386, 374] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 625 (([129, 183, 157, 558, 388, 174] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 1) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row1 row5 row1_sound row5_local x
def row6 : Vec R 6 := fun i => Fin.ofNat 625 (([353, 296, 442, 297, 76, 317] : List Nat).getD i.val 0)
theorem row6_local : ∀ i, row6 i = rm row1 (actions 2) i := by decide
theorem row6_sound (x : Vec R 6) : dot row6 x = behavior source x [2, 0] 0 :=
  observed_row_prepend actions observations 2 [0] 0 row1 row6 row1_sound row6_local x
def data : CertificateData R 6 6 3 1 7 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 625 ((([[1, 363, 401, 220, 335, 264], [0, 1, 300, 444, 148, 35], [0, 0, 1, 302, 221, 290], [0, 0, 0, 1, 471, 501], [0, 0, 0, 0, 1, 20], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 625 (((([[[259, 338, 0, 0, 0, 0], [552, 512, 265, 548, 365, 395], [597, 384, 28, 333, 499, 19], [133, 307, 78, 618, 586, 38], [22, 387, 295, 597, 254, 222], [441, 225, 218, 488, 455, 254]], [[497, 274, 486, 0, 0, 0], [283, 349, 5, 433, 279, 0], [117, 367, 117, 218, 461, 294], [189, 605, 154, 86, 3, 595], [69, 216, 176, 174, 270, 527], [21, 311, 125, 512, 253, 140]], [[519, 101, 588, 113, 0, 0], [86, 14, 580, 392, 595, 319], [8, 623, 155, 304, 545, 165], [541, 521, 112, 209, 198, 283], [183, 541, 89, 488, 232, 415], [550, 223, 17, 24, 258, 575]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 625 ((([[377, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0), ([1, 0], 0), ([2, 0], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 625 ((([[63, 0, 0, 0, 0, 0, 0], [316, 76, 0, 0, 0, 0, 0], [430, 541, 58, 0, 0, 0, 0], [194, 607, 467, 526, 0, 0, 0], [90, 360, 485, 73, 0, 119, 0], [515, 223, 534, 106, 0, 405, 204]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 7 6 := fun i j => Fin.ofNat 625 ((([[377, 601, 552, 440, 45, 153], [143, 585, 143, 479, 78, 162], [494, 120, 91, 411, 31, 226], [38, 621, 14, 176, 468, 618], [564, 178, 354, 582, 386, 374], [129, 183, 157, 558, 388, 174], [353, 296, 442, 297, 76, 317]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.cases (row6_sound) (fun i7 => Fin.elim0 i7) i6) i5) i4) i3) i2) i1) i0
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
  change := fun i j => Fin.ofNat 625 ((([[1, 262, 374, 504, 226, 82], [0, 1, 325, 156, 176, 289], [0, 0, 1, 323, 146, 592], [0, 0, 0, 1, 154, 169], [0, 0, 0, 0, 1, 605], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 625 ((([[1, 363, 401, 220, 335, 264], [0, 1, 300, 444, 148, 35], [0, 0, 1, 302, 221, 290], [0, 0, 0, 1, 471, 501], [0, 0, 0, 0, 1, 20], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 7 6 := fun i j => Fin.ofNat 625 ((([[1, 0, 0, 0, 0, 0], [262, 1, 0, 0, 0, 0], [374, 325, 1, 0, 0, 0], [504, 156, 323, 1, 0, 0], [226, 176, 146, 154, 1, 0], [125, 125, 125, 500, 125, 0], [250, 500, 250, 500, 0, 125]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 7) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 3) (Fin 1)) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0), ([1, 0], 0), ([2, 0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 3) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 6) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 6, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 6) R)).Definable
      (observationLanguage (Fin 3) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 3) (Fin 1) R n) (env : Fin n → Vec R 6) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 6) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 6) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 7) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic107
