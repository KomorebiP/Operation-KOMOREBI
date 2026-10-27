module
public import MatrixRowWitnesses
public import MatrixSmith

@[expose] public section

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 237b7b8adcc79f5e22ee4d6eb005da1a7c45f51fc527c67109502ea880d7a95c
   Canonical certificate JSON SHA256: 52d376201d6a5542a98575aa65704c0da9d80af3d9603ae88f126f497b31640d
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom065
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 25
def actions : Fin 3 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 25 (((([[[5, 8, 19, 5, 3], [22, 0, 0, 17, 0], [15, 1, 16, 11, 14], [13, 7, 4, 19, 1], [0, 3, 8, 13, 2]], [[12, 3, 11, 4, 10], [8, 19, 3, 22, 14], [4, 8, 3, 8, 21], [2, 14, 19, 9, 1], [24, 18, 7, 19, 0]], [[23, 21, 23, 0, 5], [21, 23, 17, 13, 18], [13, 23, 9, 9, 11], [10, 1, 15, 8, 18], [9, 17, 15, 24, 15]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 5 := fun i j => Fin.ofNat 25 ((([[0, 0, 0, 0, 0], [0, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def data : CertificateData R 5 0 3 2 0 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 25 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 25 (((([[], [], []] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 25 ((([[], []] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => Fin.elim0 i
  combinations := fun i j => Fin.ofNat 25 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 0 5 := fun i j => Fin.ofNat 25 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.elim0 i0
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
def smith : SmithData R 5 0 where
  width := by decide
  weights := fun i => Fin.ofNat 25 (([] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 25 ((([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 25 ((([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 0) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 0 5 := fun i j => Fin.ofNat 25 ((([] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 0) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom065
