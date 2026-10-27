module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 47cc0afff56aa41167e93e8e2d2db05da4b742b758e4e794f15158b72fd57d74
   Canonical certificate JSON SHA256: 304c1a3ade79dd39fe3fd433013725a7928dba4bf35124e0077c9b5bc00c43ae
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic093
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 32
def actions : Fin 1 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 32 (((([[[10, 4, 17, 24, 20], [21, 6, 5, 17, 26], [18, 25, 23, 19, 26], [16, 4, 3, 11, 6], [28, 30, 21, 1, 17]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 5 := fun i j => Fin.ofNat 32 ((([[22, 7, 30, 3, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 32 (([22, 7, 30, 3, 2] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 32 (([19, 24, 30, 4, 14] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 32 (([26, 30, 31, 20, 30] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row1 (actions 0) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row2 row1_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 32 (([16, 23, 11, 21, 16] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row2 (actions 0) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0] 0 row2 row3 row2_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 32 (([25, 17, 15, 15, 2] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row3 (actions 0) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [0, 0, 0, 0] 0 :=
  observed_row_prepend actions observations 0 [0, 0, 0] 0 row3 row4 row3_sound row4_local x
def data : CertificateData R 5 5 1 1 5 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 32 ((([[26, 1, 18, 5, 14], [1, 0, 26, 4, 10], [0, 0, 1, 10, 2], [0, 0, 0, 0, 8], [0, 0, 0, 8, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 32 (((([[[8, 5, 0, 0, 0], [10, 18, 29, 0, 0], [29, 24, 5, 1, 0], [16, 0, 8, 3, 1], [0, 0, 24, 0, 1]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 32 ((([[7, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([0, 0], 0), ([0, 0, 0], 0), ([0, 0, 0, 0], 0)] : List (List (Fin 1) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 32 ((([[23, 0, 0, 0, 0], [8, 11, 0, 0, 0], [18, 10, 7, 0, 0], [31, 24, 11, 11, 0], [23, 7, 3, 14, 11]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 5 5 := fun i j => Fin.ofNat 32 ((([[22, 7, 30, 3, 2], [19, 24, 30, 4, 14], [26, 30, 31, 20, 30], [16, 23, 11, 21, 16], [25, 17, 15, 15, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.elim0 i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 1)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 32 (([1, 1, 1, 8, 8] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 32 ((([[0, 1, 6, 10, 0], [1, 6, 18, 18, 15], [0, 0, 1, 30, 22], [0, 0, 0, 0, 1], [0, 0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 32 ((([[26, 1, 18, 5, 14], [1, 0, 26, 4, 10], [0, 0, 1, 10, 2], [0, 0, 0, 0, 1], [0, 0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 1) (Fin 1) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 5 5 := fun i j => Fin.ofNat 32 ((([[1, 0, 0, 0, 0], [1, 6, 0, 0, 0], [6, 18, 1, 0, 0], [10, 18, 30, 0, 1], [0, 15, 22, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 5) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 1) (Fin 1)) := [([], 0), ([0], 0), ([0, 0], 0), ([0, 0, 0], 0), ([0, 0, 0, 0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 1) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 5) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 5, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 5) R)).Definable
      (observationLanguage (Fin 1) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 1) (Fin 1) R n) (env : Fin n → Vec R 5) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 5) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 5) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 5) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic093
