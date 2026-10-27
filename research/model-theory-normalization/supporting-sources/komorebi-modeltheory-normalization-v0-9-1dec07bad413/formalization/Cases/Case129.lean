module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: bdcd81a73bea16595b87ae18478892a37033bfbbc23c80a839d7f20bed226b61
   Canonical certificate JSON SHA256: 76bac50827fc214961868926f0fecf7f1ddde98f0f756742130294a1f5462658
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic129
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 4
def actions : Fin 1 → Mat R 2 2 :=
  fun a i j => Fin.ofNat 4 (((([[[0, 2], [1, 3]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 2 := fun i j => Fin.ofNat 4 ((([[3, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 2 := fun i => Fin.ofNat 4 (([3, 1] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 2) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 2 := fun i => Fin.ofNat 4 (([1, 1] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 2) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def data : CertificateData R 2 2 1 1 2 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 4 ((([[1, 3], [0, 2]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 4 (((([[[3, 1], [2, 0]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 4 ((([[3, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0)] : List (List (Fin 1) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 4 ((([[3, 0], [1, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 2 2 := fun i j => Fin.ofNat 4 ((([[3, 1], [1, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.elim0 i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 2) (w : List (Fin 1)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 2) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 2 2 where
  width := by decide
  weights := fun i => Fin.ofNat 4 (([1, 2] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 4 ((([[1, 1], [0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 4 ((([[1, 3], [0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 2) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 1) (Fin 1) R)
    (encode : Vec R 2 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 2 2 := fun i j => Fin.ofNat 4 ((([[1, 0], [1, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 2) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 1) (Fin 1)) := [([], 0), ([0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 1) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 2) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 2, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 2) R)).Definable
      (observationLanguage (Fin 1) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 1) (Fin 1) R n) (env : Fin n → Vec R 2) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 2) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 2) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 2) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic129
