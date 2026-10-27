import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 96b67f9879368135be40b935e3468e64b58b8d3aecce5dcd7cbc7232da9c0a06
   Canonical certificate JSON SHA256: 5929fdfba10987d5391084b6224a01c9cd646d4e3b3c15b468da1920dd89f400
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom130
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 81
def actions : Fin 2 → Mat R 3 3 :=
  fun a i j => Fin.ofNat 81 (((([[[16, 31, 53], [25, 49, 2], [47, 75, 50]], [[9, 31, 44], [80, 80, 67], [11, 26, 6]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 3 := fun i j => Fin.ofNat 81 ((([[0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def data : CertificateData R 3 0 2 1 0 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 81 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 81 (((([[], []] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 81 ((([[]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => Fin.elim0 i
  combinations := fun i j => Fin.ofNat 81 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 0 3 := fun i j => Fin.ofNat 81 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.elim0 i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 3) (w : List (Fin 2)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 3) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 3 0 where
  width := by decide
  weights := fun i => Fin.ofNat 81 (([] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 81 ((([[1, 0, 0], [0, 1, 0], [0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 81 ((([[1, 0, 0], [0, 1, 0], [0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 0) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 2) (Fin 1) R)
    (encode : Vec R 3 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 0 3 := fun i j => Fin.ofNat 81 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 0) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom130
