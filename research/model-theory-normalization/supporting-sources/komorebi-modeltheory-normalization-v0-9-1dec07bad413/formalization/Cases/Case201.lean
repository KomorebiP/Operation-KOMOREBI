module
public import MatrixRowWitnesses
public import MatrixSmith
public import MatrixLogicalWitnesses

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 300cb0e53191750f91aae081fe98db1ada2ff311e6932955e656ba8a815ca0af
   Canonical certificate JSON SHA256: 28c10817335eabcebcb258d6c3f80d247f0e2ac4626b22a65897212b68b7bb61
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.Logic201
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 65536
def actions : Fin 2 → Mat R 8 8 :=
  fun a i j => Fin.ofNat 65536 (((([[[17698, 7962, 49699, 37320, 23412, 6538, 39824, 34395], [23464, 37603, 20556, 32118, 60325, 50701, 6345, 63146], [7061, 60025, 48800, 57289, 7901, 57423, 17450, 21611], [57954, 1463, 43061, 61981, 12327, 24535, 55220, 20222], [9538, 34330, 18991, 25859, 64489, 51532, 7482, 17514], [8262, 4689, 20524, 11331, 58729, 9597, 8879, 16991], [38245, 65480, 12079, 48575, 41217, 13059, 11905, 14025], [40555, 32470, 51819, 35275, 34452, 61245, 54300, 32399]], [[45667, 60993, 42044, 24680, 13027, 39737, 34859, 3988], [10393, 29683, 38554, 51204, 39690, 4755, 35121, 61378], [63427, 47581, 32082, 32486, 44031, 34935, 29965, 8363], [27479, 23039, 1777, 57316, 32532, 42871, 30241, 7992], [35244, 37369, 1342, 167, 21177, 50423, 62217, 51013], [29874, 59333, 42924, 46108, 58455, 35340, 60778, 27268], [52594, 11868, 27092, 9501, 44582, 25499, 5486, 41184], [1304, 20195, 44643, 12867, 63107, 13759, 28318, 26332]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 8 := fun i j => Fin.ofNat 65536 ((([[7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 8 := fun i => Fin.ofNat 65536 (([7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 8) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 8 := fun i => Fin.ofNat 65536 (([40244, 36259, 3534, 13185, 54629, 54745, 26715, 36451] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 8) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def data : CertificateData R 8 2 2 1 2 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 65536 ((([[3400, 1, 12750, 27359, 45835, 37043, 61289, 53825], [4, 0, 60924, 65052, 26428, 63008, 43136, 28160]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 65536 (((([[[60441, 9909], [40640, 5097]], [[3, 0], [58736, 5]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 65536 ((([[48923, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0)] : List (List (Fin 2) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 65536 ((([[33555, 0], [48305, 6055]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 2 8 := fun i j => Fin.ofNat 65536 ((([[7832, 48923, 62138, 42629, 5929, 53217, 38675, 43995], [40244, 36259, 3534, 13185, 54629, 54745, 26715, 36451]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.elim0 i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 8) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 8) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 8 2 where
  width := by decide
  weights := fun i => Fin.ofNat 65536 (([1, 4] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 65536 ((([[0, 1, 50305, 49273, 58929, 49784, 54752, 58496], [1, 62136, 64746, 19993, 4653, 42381, 35223, 27071], [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 65536 ((([[3400, 1, 12750, 27359, 45835, 37043, 61289, 53825], [1, 0, 15231, 16263, 6607, 15752, 10784, 7040], [0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 2) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 8 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 2 8 := fun i j => Fin.ofNat 65536 ((([[1, 0, 0, 0, 0, 0, 0, 0], [1, 62136, 0, 0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 2) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i

open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge

def discoveredTests : List (ObservationTest (Fin 2) (Fin 1)) := [([], 0), ([0], 0)]
theorem test_list_checked : discoveredTests = matrixTests data := by decide

def discoveredFormula : (observationLanguage (Fin 2) (Fin 1) R).Formula (Fin 2) :=
  guardedCodeFormula discoveredTests

theorem discovered_formula_isQF : discoveredFormula.IsQF :=
  guardedCodeFormula_isQF discoveredTests

theorem discovered_formula_exact (e : Fin 2 → TaggedCarrier (Vec R 8) R) :
    taggedRealize (sourceSystem data) discoveredFormula e ↔
      ∃ env : Fin 2 → Vec R 8, e = (fun i => Sum.inl (env i)) ∧
        mv data.encoding (env 0) = mv data.encoding (env 1) := by
  change taggedRealize (sourceSystem data) (guardedCodeFormula discoveredTests) e ↔ _
  rw [test_list_checked]
  exact matrixCodeFormula_semantics data valid e

theorem discovered_encoding_definable :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 8) R)).Definable
      (observationLanguage (Fin 2) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

theorem discovered_image_preserves_queries {n : Nat}
    (f : ObsFO (Fin 2) (Fin 1) R n) (env : Fin n → Vec R 8) :
    standardRealize (sourceSystem data) (toMathlib f) env ↔
      standardRealize (imageSystem data valid) (toMathlib f)
        (fun i => (imageTransport data valid).encode (env i)) :=
  matrix_image_preserves_formulas data valid f env

theorem discovered_class_formula (y : EncodedImage data) (x : Vec R 8) :
    standardRealize (sourceSystem data) (matrixFiberFormula data y.val) (fun _ => x) ↔
      mv data.encoding x = y.val :=
  matrixFiberFormula_states data valid y x

theorem discovered_terms_code_kernel (x y : Vec R 8) :
    matrixLogicalCode data (fun _ => Sum.inl x) = matrixLogicalCode data (fun _ => Sum.inl y) ↔
      mv data.encoding x = mv data.encoding y := matrixLogicalCode_exact data valid x y

theorem discovered_growth_formula (i : Fin 2) :
    standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => fun _ => 0) ∧
    ¬ standardRealize (sourceSystem data)
      (toMathlib (.test (n := 1) (0,(data.tests i).1) (data.tests i).2 (0 : R))) (fun _ => growthDeltas i) :=
  growth_formula_distinguishes data witnessedRows growthDeltas rows_sound growth_checked i

end Komorebi.Representation.Symbolic.Logic201
