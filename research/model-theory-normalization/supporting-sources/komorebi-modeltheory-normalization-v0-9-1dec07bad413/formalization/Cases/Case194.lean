module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 19e9144370850d4462bd1b45c715be347e7697ecc8300ae0a4b7f046f3a48265
   Canonical certificate JSON SHA256: c1123cd2d9f8896007fed8497e1fc2c2aeb96e9b77da1b68fe4e5669b3d240fe
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic194
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 125
def actions : Fin 3 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 125 (((([[[24, 66, 28, 73, 108, 90], [88, 90, 116, 100, 34, 69], [4, 63, 8, 79, 3, 42], [19, 81, 62, 56, 16, 50], [105, 67, 122, 7, 104, 0], [112, 18, 67, 52, 10, 41]], [[64, 109, 99, 36, 122, 10], [5, 97, 70, 31, 41, 118], [116, 58, 122, 55, 93, 104], [52, 4, 30, 30, 8, 93], [48, 94, 6, 6, 10, 91], [80, 43, 58, 0, 16, 118]], [[54, 18, 65, 34, 111, 78], [47, 7, 119, 5, 48, 88], [24, 110, 95, 37, 29, 82], [98, 124, 89, 103, 55, 2], [49, 113, 120, 15, 88, 55], [102, 15, 3, 109, 77, 50]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 125 ((([[86, 71, 44, 98, 62, 37], [97, 24, 77, 0, 105, 85]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 125 (([86, 71, 44, 98, 62, 37] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 125 (([97, 24, 77, 0, 105, 85] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 125 (([4, 96, 115, 75, 95, 29] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 125 (([120, 124, 60, 29, 116, 61] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 125 (([78, 98, 117, 89, 50, 20] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row0 (actions 2) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row4 row0_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 125 (([43, 103, 121, 94, 43, 105] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row1 (actions 0) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row5 row1_sound row5_local x
def data : CertificateData R 6 6 3 2 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 125 ((([[1, 11, 79, 68, 117, 92], [0, 1, 2, 72, 58, 98], [0, 0, 105, 1, 4, 35], [0, 0, 1, 0, 60, 7], [0, 0, 0, 0, 1, 86], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 125 (((([[[64, 82, 69, 0, 0, 0], [30, 118, 6, 2, 81, 7], [29, 25, 52, 59, 6, 28], [88, 116, 27, 28, 1, 13], [112, 8, 37, 10, 23, 95], [112, 36, 94, 27, 72, 38]], [[45, 114, 71, 97, 0, 0], [105, 12, 20, 87, 45, 99], [99, 11, 55, 26, 122, 97], [56, 8, 31, 68, 85, 83], [53, 84, 104, 94, 7, 106], [80, 38, 74, 17, 11, 4]], [[123, 90, 80, 75, 119, 0], [114, 50, 70, 15, 48, 40], [9, 52, 7, 99, 110, 10], [53, 37, 57, 70, 73, 92], [71, 122, 27, 65, 69, 33], [102, 18, 2, 74, 26, 78]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 125 ((([[86, 0, 0, 0, 0, 0], [97, 82, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 125 ((([[16, 0, 0, 0, 0, 0], [39, 93, 0, 0, 0, 0], [62, 96, 89, 0, 0, 0], [56, 6, 123, 53, 0, 0], [23, 0, 120, 100, 39, 0], [28, 9, 77, 42, 13, 49]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 125 ((([[86, 71, 44, 98, 62, 37], [97, 24, 77, 0, 105, 85], [4, 96, 115, 75, 95, 29], [120, 124, 60, 29, 116, 61], [78, 98, 117, 89, 50, 20], [43, 103, 121, 94, 43, 105]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 125 (([1, 1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 125 ((([[1, 114, 99, 48, 120, 115], [0, 1, 53, 58, 0, 16], [0, 0, 0, 1, 65, 28], [0, 0, 1, 20, 46, 119], [0, 0, 0, 0, 1, 39], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 125 ((([[1, 11, 79, 68, 117, 92], [0, 1, 2, 72, 58, 98], [0, 0, 105, 1, 4, 35], [0, 0, 1, 0, 60, 7], [0, 0, 0, 0, 1, 86], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 125 ((([[1, 0, 0, 0, 0, 0], [114, 1, 0, 0, 0, 0], [68, 123, 1, 0, 0, 0], [48, 58, 1, 20, 0, 0], [120, 0, 65, 46, 1, 0], [115, 16, 28, 119, 39, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 3) (Fin 2)) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 3) (Fin 2) R).Formula (Fin 2) :=
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
      (observationLanguage (Fin 3) (Fin 2) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 3) (Fin 2) R n) (env : Fin n → Vec R 6) :
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

theorem discovered_growth_formula (i : Fin 6) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic194
