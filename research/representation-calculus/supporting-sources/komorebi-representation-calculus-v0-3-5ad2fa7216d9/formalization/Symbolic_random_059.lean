import MatrixRowWitnesses
import MatrixSmith

/- Automatically generated untrusted source. Every accepted identity is kernel checked.
   Canonical input JSON SHA256: 5f00b3ca2dc7428d8cf979b5f0d8a4d70b51d247bfb86ae71c34cd5cc0526d0c
   Canonical certificate JSON SHA256: 6376b0aafc7791e6575e5ebaa181ddda686a9ea430a90388b09d124ab10dc62d
   Source states are finite vectors, never an enumerated state table. -/
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
namespace Komorebi.Representation.Symbolic.CaseRandom059
open Komorebi.Representation
open Komorebi.Representation.Matrix
abbrev R := Fin 3125
def actions : Fin 3 → Mat R 4 4 :=
  fun a i j => Fin.ofNat 3125 (((([[[2781, 4, 2809, 2360], [2840, 1576, 1793, 2417], [2471, 666, 20, 859], [1063, 1901, 1256, 2242]], [[401, 2351, 497, 2498], [246, 1266, 2326, 221], [1341, 125, 2490, 2472], [1753, 2328, 2560, 2227]], [[906, 3001, 682, 563], [11, 1251, 1314, 1325], [1536, 2787, 1181, 2031], [1688, 1888, 1751, 619]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
def observations : Mat R 2 4 := fun i j => Fin.ofNat 3125 ((([[34, 872, 752, 1288], [2123, 3020, 2824, 1286]] : List (List Nat)).getD i.val []).getD j.val 0)
def source := linearSystem actions observations
def row0 : Vec R 4 := fun i => Fin.ofNat 3125 (([34, 872, 752, 1288] : List Nat).getD i.val 0)
theorem row0_local : ∀ i, row0 i = observations 0 i := by decide
theorem row0_sound (x : Vec R 4) : dot row0 x = behavior source x [] 0 :=
  observed_row_base actions observations 0 row0 row0_local x
def row1 : Vec R 4 := fun i => Fin.ofNat 3125 (([2123, 3020, 2824, 1286] : List Nat).getD i.val 0)
theorem row1_local : ∀ i, row1 i = observations 1 i := by decide
theorem row1_sound (x : Vec R 4) : dot row1 x = behavior source x [] 1 :=
  observed_row_base actions observations 1 row1 row1_local x
def row2 : Vec R 4 := fun i => Fin.ofNat 3125 (([1495, 1853, 1145, 2778] : List Nat).getD i.val 0)
theorem row2_local : ∀ i, row2 i = rm row0 (actions 0) i := by decide
theorem row2_sound (x : Vec R 4) : dot row2 x = behavior source x [0] 0 :=
  observed_row_prepend actions observations 0 [] 0 row0 row2 row0_sound row2_local x
def row3 : Vec R 4 := fun i => Fin.ofNat 3125 (([692, 1350, 2430, 1839] : List Nat).getD i.val 0)
theorem row3_local : ∀ i, row3 i = rm row0 (actions 1) i := by decide
theorem row3_sound (x : Vec R 4) : dot row3 x = behavior source x [1] 0 :=
  observed_row_prepend actions observations 1 [] 0 row0 row3 row0_sound row3_local x
def data : CertificateData R 4 4 3 2 4 where
  actions := actions
  observations := observations
  encoding := fun i j => Fin.ofNat 3125 ((([[1, 2783, 2228, 957], [0, 1, 105, 700], [0, 0, 1665, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  transitions := fun a i j => Fin.ofNat 3125 (((([[[1055, 3052, 1657, 0], [145, 1796, 422, 73], [2778, 1492, 1406, 647], [2471, 1998, 12, 2362]], [[388, 2221, 2255, 401], [2526, 1633, 1949, 1923], [143, 3109, 1831, 1621], [1341, 2497, 2485, 2532]], [[393, 817, 1238, 1235], [2266, 2958, 2468, 1311], [2878, 1519, 2188, 292], [1536, 3099, 279, 1543]]] : List (List (List Nat))).getD a.val []).getD i.val []).getD j.val 0)
  decoder := fun i j => Fin.ofNat 3125 ((([[34, 0, 0, 0], [2123, 961, 0, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
  tests := fun i => ([([], 0), ([], 1), ([0], 0), ([1], 0)] : List (List (Fin 3) × Fin 2)).getD i.val ([], 0)
  combinations := fun i j => Fin.ofNat 3125 ((([[2114, 0, 0, 0], [523, 891, 0, 0], [712, 2474, 1527, 0], [125, 869, 1240, 2764]] : List (List Nat)).getD i.val []).getD j.val 0)
def witnessedRows : Mat R 4 4 := fun i j => Fin.ofNat 3125 ((([[34, 872, 752, 1288], [2123, 3020, 2824, 1286], [1495, 1853, 1145, 2778], [692, 1350, 2430, 1839]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem rows_sound : ∀ i x, dot (witnessedRows i) x = behavior (sourceSystem data) x (data.tests i).1 (data.tests i).2 :=
  fun i0 => Fin.cases (row0_sound) (fun i1 => Fin.cases (row1_sound) (fun i2 => Fin.cases (row2_sound) (fun i3 => Fin.cases (row3_sound) (fun i4 => Fin.elim0 i4) i3) i2) i1) i0
theorem local_equations :
    (∀ a i j, mm data.encoding (data.actions a) i j = mm (data.transitions a) data.encoding i j) ∧
    (∀ j i, data.observations j i = mm data.decoder data.encoding j i) ∧
    (∀ i j, data.encoding i j = mm data.combinations witnessedRows i j) := by decide
theorem valid : Valid data := valid_from_rows data witnessedRows rows_sound local_equations.1 local_equations.2.1 local_equations.2.2
theorem all_states_all_words (x : Vec R 4) (w : List (Fin 3)) (j : Fin 2) :
    behavior (sourceSystem data) x w j = behavior (targetSystem data) (mv data.encoding x) w j :=
  matrix_all_words data valid x w j
theorem exact_behavior (x y : Vec R 4) :
    ObsEq (sourceSystem data) x y ↔ mv data.encoding x = mv data.encoding y :=
  matrix_behavior_exact data valid x y
def smith : SmithData R 4 4 where
  width := by decide
  weights := fun i => Fin.ofNat 3125 (([1, 1, 1, 1] : List Nat).getD i.val 0)
  change := fun i j => Fin.ofNat 3125 ((([[1, 342, 268, 17], [0, 1, 2425, 2895], [0, 0, 0, 1], [0, 0, 1, 1460]] : List (List Nat)).getD i.val []).getD j.val 0)
  inverse := fun i j => Fin.ofNat 3125 ((([[1, 2783, 2228, 957], [0, 1, 105, 700], [0, 0, 1665, 1], [0, 0, 1, 0]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem smith_checked : checkSmith data.encoding smith = true := by decide
theorem exact_image (y : Vec R 4) :
    (∃ x, mv data.encoding x = y) ↔ PrincipalCoordinates smith.weights y :=
  checked_smith_image data.encoding smith smith_checked y
theorem every_competitor_contains_image {Z : Type} (U : System Z (Fin 3) (Fin 2) R)
    (encode : Vec R 4 → Z)
    (h : ∀ x w j, behavior (sourceSystem data) x w j = behavior U (encode x) w j) :
    ∃ f : EncodedImage data → Z, ∀ y z, f y = f z → y = z :=
  image_minimal_semantic_encoding data valid U encode h
def growthDeltas : Mat R 4 4 := fun i j => Fin.ofNat 3125 ((([[1, 0, 0, 0], [342, 1, 0, 0], [2487, 3020, 1, 0], [17, 2895, 1, 1460]] : List (List Nat)).getD i.val []).getD j.val 0)
theorem growth_checked : ∀ i, (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = 0) ∧ dot (witnessedRows i) (growthDeltas i) ≠ 0 := by decide
theorem growth_really_distinguishes (i : Fin 4) :
    (∀ j, j.val < i.val → dot (witnessedRows j) (growthDeltas i) = dot (witnessedRows j) (fun _ => 0)) ∧
    ¬ ObsEq (sourceSystem data) (growthDeltas i) (fun _ => 0) :=
  witnessed_growth_excludes_merge data witnessedRows growthDeltas rows_sound growth_checked i
end Komorebi.Representation.Symbolic.CaseRandom059
