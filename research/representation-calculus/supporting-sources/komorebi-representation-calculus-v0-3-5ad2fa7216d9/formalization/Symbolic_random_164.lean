import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: cddce289e8ee2081c20d9cc78ca3d666f040e2730df8479383b7558f7c18d15a
   Canonical certificate JSON SHA256: 03b5b1aafc0909c978af40db4c9ea72472178f6476dc3f459b9830d65761feb9
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom164
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 5 5 :=
  fun a i j => Fin.ofNat 3125 (((([[[1331, 1876, 1173, 1684, 1937], [556, 1499, 2714, 2283, 447], [2803, 664, 2344, 1296, 1713], [1422, 841, 2661, 2983, 3011], [340, 110, 1368, 2398, 1549]], [[697, 1148, 1073, 245, 517], [26, 521, 2207, 1239, 2122], [360, 1178, 355, 1939, 2263], [1484, 2820, 1204, 2834, 2234], [2608, 78, 445, 267, 2914]], [[1649, 1259, 339, 2615, 1617], [2869, 2745, 1957, 2747, 870], [2567, 2842, 1321, 2954, 1983], [2180, 2801, 2172, 2718, 1193], [2544, 1971, 1024, 1694, 839]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 1 5 := fun i j => Fin.ofNat 3125 ((([[1490, 937, 878, 624, 1892]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 5 := fun i => Fin.ofNat 3125 (([1490, 937, 878, 624, 1892] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 5) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 5 := fun i => Fin.ofNat 3125 (([2054, 74, 665, 252, 2930] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = rm row0 (actions 0) i := by decide
theorem row1_sound (x : Vec R 5) : dot row1 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row1 row0_sound row1_local x
def row2 : Vec R 5 := fun i => Fin.ofNat 3125 (([1824, 2737, 2905, 2015, 2862] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 1) i := by decide
theorem row2_sound (x : Vec R 5) : dot row2 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 5 := fun i => Fin.ofNat 3125 (([782, 1457, 768, 2481, 539] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 2) i := by decide
theorem row3_sound (x : Vec R 5) : dot row3 x = behavior source x [2] 0 :=
  observed_row_prepend actions observations 2 [] 0 row0 row3 row0_sound row3_local x
def row4 : Vec R 5 := fun i => Fin.ofNat 3125 (([2932, 2522, 875, 1949, 1288] : List Nat).getD i.val 0)
theorem row4_local : ∀ i, row4 i = rm row1 (actions 0) i := by decide
theorem row4_sound (x : Vec R 5) : dot row4 x = behavior source x [0, 0] 0 :=
  observed_row_prepend actions observations 0 [0] 0 row1 row4 row1_sound row4_local x
def data : CertificateData R 5 5 3 1 5 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[145, 1, 2619, 2502, 1216], [1, 0, 591, 2096, 479], [0, 0, 1, 519, 2223], [0, 0, 0, 1, 1495], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[477, 2352, 0, 0, 0], [351, 381, 2890, 1317, 2147], [423, 931, 784, 1109, 2995], [2791, 1902, 1610, 1479, 1842], [110, 15, 1288, 2266, 335]], [[2651, 82, 2759, 0, 0], [1678, 1718, 97, 2024, 1964], [652, 1725, 3028, 1015, 3005], [680, 1844, 2005, 1270, 2118], [78, 673, 1545, 2023, 1779]], [[2086, 966, 3074, 1974, 0], [2136, 7, 737, 2836, 204], [594, 44, 1376, 2427, 2529], [2571, 1415, 838, 1844, 473], [1971, 1124, 2816, 2844, 834]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[937, 0, 0, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([0], 0), ([1], 0), ([2], 0), ([0, 0], 0)] : List (List (Fin 3) × Fin 1)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[2498, 0, 0, 0, 0], [1877, 3049, 0, 0, 0], [1557, 1998, 847, 0, 0], [3028, 2036, 853, 2702, 0], [2072, 1083, 2677, 1453, 3042]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 5 5 := fun i j => Fin.ofNat 3125 ((([[1490, 937, 878, 624, 1892], [2054, 74, 665, 252, 2930], [1824, 2737, 2905, 2015, 2862], [782, 1457, 768, 2481, 539], [2932, 2522, 875, 1949, 1288]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.cases (row4_sound) (fun i5 => Fin.elim0 i5) i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 5) (w : List (Fin 3)) (j : Fin 1) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 5) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 5 5 where
  width := by decide
  weights := fun i => Fin.ofNat 3125 (([1, 1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 3125 ((([[0, 1, 2534, 1508, 2604], [1, 2980, 1826, 599, 1036], [0, 0, 1, 2606, 1807], [0, 0, 0, 1, 1630], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[145, 1, 2619, 2502, 1216], [1, 0, 591, 2096, 479], [0, 0, 1, 519, 2223], [0, 0, 0, 1, 1495], [0, 0, 0, 0, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 5) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 1) R)
    (encode : Vec R 5 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 5 5 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0, 0], [1, 2980, 0, 0, 0], [2534, 1826, 1, 0, 0], [1508, 599, 2606, 1, 0], [2604, 1036, 1807, 1630, 1]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 5) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom164
