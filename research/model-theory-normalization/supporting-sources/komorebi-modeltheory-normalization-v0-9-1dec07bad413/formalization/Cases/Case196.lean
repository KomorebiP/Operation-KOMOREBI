module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: d221a341a59fc717d5fe8ad6dc176c7f5ce74984a60ecd23aadd1a9f0cba4e95
   Canonical certificate JSON SHA256: f68f192cce532860010dc83bc51dee5a092d194f6038ff6d6a42b21013d0f7cf
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic196
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 81
def actions : Fin 2 → Mat R 6 6 :=
  fun a i j => Fin.ofNat 81 (((([[[8, 19, 44, 66, 42, 8], [21, 68, 61, 80, 63, 50], [42, 67, 13, 43, 30, 70], [79, 23, 37, 29, 17, 80], [30, 33, 27, 67, 73, 47], [68, 3, 45, 46, 22, 50]], [[53, 76, 44, 41, 10, 52], [34, 31, 8, 12, 32, 71], [76, 54, 7, 69, 25, 39], [28, 40, 40, 26, 72, 1], [26, 76, 44, 65, 35, 28], [47, 68, 67, 26, 57, 33]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 6 := fun i j => Fin.ofNat 81 ((([[27, 27, 0, 27, 0, 27], [0, 0, 0, 27, 27, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 6 := fun i => Fin.ofNat 81 (([27, 27, 0, 27, 0, 27] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 6) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 6 := fun i => Fin.ofNat 81 (([0, 0, 0, 27, 27, 0] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 6) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 6 := fun i => Fin.ofNat 81 (([54, 54, 27, 54, 0, 54] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 6) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 6 := fun i => Fin.ofNat 81 (([0, 54, 0, 0, 0, 27] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 6) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 6 := fun i => Fin.ofNat 81 (([27, 54, 27, 0, 0, 27] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 6) : dot row4 x = behavior source x [0] 1 :=
  observed_row_prepend actions observations 0 [] 1 row1 row4 row1_sound row4_local x
def row5 : Vec R 6 := fun i => Fin.ofNat 81 (([27, 27, 27, 0, 27, 54] : List Nat).getD i.val 0)
theorem row5_local : ∀ i, row5 i = rm row2 (actions 1) i := by decide
theorem row5_sound (x : Vec R 6) : dot row5 x = behavior source x [1, 0] 0 :=
  observed_row_prepend actions observations 1 [0] 0 row2 row5 row2_sound row5_local x
def data : CertificateData R 6 6 2 2 6 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 81 ((([[27, 27, 0, 27, 0, 27], [0, 0, 0, 27, 27, 0], [0, 0, 27, 0, 0, 0], [0, 27, 0, 0, 0, 54], [0, 0, 0, 0, 27, 27], [0, 0, 0, 0, 0, 27]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 81 (((([[[2, 0, 1, 0, 0, 0], [1, 2, 1, 1, 1, 0], [0, 1, 1, 1, 2, 0], [1, 0, 1, 1, 2, 1], [2, 0, 0, 1, 2, 1], [2, 2, 0, 1, 2, 2]], [[0, 0, 0, 2, 0, 0], [0, 1, 0, 2, 1, 0], [1, 2, 1, 2, 2, 2], [2, 2, 1, 0, 0, 0], [1, 0, 0, 2, 2, 0], [2, 0, 1, 0, 0, 1]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 81 ((([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1, 0], 0)] : List (List (Fin 2) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 81 ((([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [79, 0, 1, 0, 0, 0], [0, 0, 0, 41, 0, 0], [1, 79, 80, 40, 1, 0], [40, 1, 41, 41, 80, 41]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 6 6 := fun i j => Fin.ofNat 81 ((([[27, 27, 0, 27, 0, 27], [0, 0, 0, 27, 27, 0], [54, 54, 27, 54, 0, 54], [0, 54, 0, 0, 0, 27], [27, 54, 27, 0, 0, 27], [27, 27, 27, 0, 27, 54]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.cases (row5_sound) (fun i6 => Fin.elim0 i6) i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 6) (w : List (Fin 2)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 6) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 6 6 where
  width := by decide
  weights := fun i => Fin.ofNat 81 (([27, 27, 27, 27, 27, 27] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 81 ((([[1, 80, 0, 80, 1, 0], [0, 0, 0, 1, 0, 79], [0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 80, 1], [0, 0, 0, 0, 1, 80], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 81 ((([[1, 1, 0, 1, 0, 1], [0, 0, 0, 1, 1, 0], [0, 0, 1, 0, 0, 0], [0, 1, 0, 0, 0, 2], [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 6) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 2) R)
    (encode : Vec R 6 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 6 6 := fun i j => Fin.ofNat 81 ((([[1, 0, 0, 0, 0, 0], [80, 0, 0, 1, 0, 0], [0, 0, 1, 0, 0, 0], [80, 1, 0, 0, 0, 0], [1, 0, 0, 80, 1, 0], [0, 79, 0, 1, 80, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 6) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 2) (Fin 2)) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1, 0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 2) (Fin 2) R).Formula (Fin 2) :=
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
      (observationLanguage (Fin 2) (Fin 2) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 2) (Fin 2) R n) (env : Fin n → Vec R 6) :
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

end Komorebi.Representation.Symbolic.Logic196
