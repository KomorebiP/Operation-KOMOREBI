module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch03
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev c036_R := ZMod (2^1)
def c036_A : Fin 1 → Mat c036_R 2 2 := ![![![0, 0], ![1, 1]]]
def c036_O : Mat c036_R 2 2 := ![![1, 1], ![1, 0]]
def c036_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c036_computed : discoverEval 2 1 2 c036_A c036_O =
    (some c036_result, 143) := by decide +kernel
theorem c036_all_words : FiniteCodeCertificate (linearSystem c036_A c036_O) c036_result :=
  discoverEval_code 2 1 2 c036_A c036_O c036_result
    (congrArg Prod.fst c036_computed)
abbrev c037_R := ZMod (3^1)
def c037_A : Fin 2 → Mat c037_R 2 2 := ![![![2, 2], ![0, 1]], ![![2, 0], ![0, 0]]]
def c037_O : Mat c037_R 1 2 := ![![1, 2]]
def c037_result : List (Test 2 1) := [([], 0), ([1], 0)]
theorem c037_computed : discoverEval 3 1 2 c037_A c037_O =
    (some c037_result, 214) := by decide +kernel
theorem c037_all_words : FiniteCodeCertificate (linearSystem c037_A c037_O) c037_result :=
  discoverEval_code 3 1 2 c037_A c037_O c037_result
    (congrArg Prod.fst c037_computed)
abbrev c038_R := ZMod (5^1)
def c038_A : Fin 3 → Mat c038_R 2 2 := ![![![4, 2], ![0, 3]], ![![1, 2], ![2, 3]], ![![0, 0], ![3, 0]]]
def c038_O : Mat c038_R 2 2 := ![![2, 2], ![2, 4]]
def c038_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c038_computed : discoverEval 5 1 2 c038_A c038_O =
    (some c038_result, 247) := by decide +kernel
theorem c038_all_words : FiniteCodeCertificate (linearSystem c038_A c038_O) c038_result :=
  discoverEval_code 5 1 2 c038_A c038_O c038_result
    (congrArg Prod.fst c038_computed)
abbrev c039_R := ZMod (2^2)
def c039_A : Fin 1 → Mat c039_R 2 2 := ![![![0, 0], ![3, 0]]]
def c039_O : Mat c039_R 1 2 := ![![2, 1]]
def c039_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c039_computed : discoverEval 2 2 2 c039_A c039_O =
    (some c039_result, 163) := by decide +kernel
theorem c039_all_words : FiniteCodeCertificate (linearSystem c039_A c039_O) c039_result :=
  discoverEval_code 2 2 2 c039_A c039_O c039_result
    (congrArg Prod.fst c039_computed)
abbrev c040_R := ZMod (3^2)
def c040_A : Fin 2 → Mat c040_R 2 2 := ![![![8, 0], ![6, 2]], ![![7, 3], ![5, 5]]]
def c040_O : Mat c040_R 2 2 := ![![6, 1], ![5, 5]]
def c040_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c040_computed : discoverEval 3 2 2 c040_A c040_O =
    (some c040_result, 225) := by decide +kernel
theorem c040_all_words : FiniteCodeCertificate (linearSystem c040_A c040_O) c040_result :=
  discoverEval_code 3 2 2 c040_A c040_O c040_result
    (congrArg Prod.fst c040_computed)
abbrev c041_R := ZMod (5^2)
def c041_A : Fin 3 → Mat c041_R 2 2 := ![![![21, 3], ![13, 1]], ![![21, 22], ![11, 16]], ![![18, 4], ![17, 19]]]
def c041_O : Mat c041_R 1 2 := ![![8, 1]]
def c041_result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem c041_computed : discoverEval 5 2 2 c041_A c041_O =
    (some c041_result, 281) := by decide +kernel
theorem c041_all_words : FiniteCodeCertificate (linearSystem c041_A c041_O) c041_result :=
  discoverEval_code 5 2 2 c041_A c041_O c041_result
    (congrArg Prod.fst c041_computed)
abbrev c042_R := ZMod (2^3)
def c042_A : Fin 1 → Mat c042_R 2 2 := ![![![7, 4], ![5, 2]]]
def c042_O : Mat c042_R 2 2 := ![![0, 4], ![4, 0]]
def c042_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c042_computed : discoverEval 2 3 2 c042_A c042_O =
    (some c042_result, 129) := by decide +kernel
theorem c042_all_words : FiniteCodeCertificate (linearSystem c042_A c042_O) c042_result :=
  discoverEval_code 2 3 2 c042_A c042_O c042_result
    (congrArg Prod.fst c042_computed)
abbrev c043_R := ZMod (3^3)
def c043_A : Fin 2 → Mat c043_R 2 2 := ![![![6, 1], ![8, 26]], ![![1, 11], ![8, 0]]]
def c043_O : Mat c043_R 1 2 := ![![14, 8]]
def c043_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c043_computed : discoverEval 3 3 2 c043_A c043_O =
    (some c043_result, 235) := by decide +kernel
theorem c043_all_words : FiniteCodeCertificate (linearSystem c043_A c043_O) c043_result :=
  discoverEval_code 3 3 2 c043_A c043_O c043_result
    (congrArg Prod.fst c043_computed)
abbrev c044_R := ZMod (5^3)
def c044_A : Fin 3 → Mat c044_R 2 2 := ![![![27, 1], ![74, 15]], ![![67, 57], ![34, 72]], ![![25, 49], ![41, 54]]]
def c044_O : Mat c044_R 2 2 := ![![114, 44], ![56, 15]]
def c044_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c044_computed : discoverEval 5 3 2 c044_A c044_O =
    (some c044_result, 296) := by decide +kernel
theorem c044_all_words : FiniteCodeCertificate (linearSystem c044_A c044_O) c044_result :=
  discoverEval_code 5 3 2 c044_A c044_O c044_result
    (congrArg Prod.fst c044_computed)
abbrev c045_R := ZMod (2^4)
def c045_A : Fin 1 → Mat c045_R 2 2 := ![![![2, 4], ![8, 4]]]
def c045_O : Mat c045_R 1 2 := ![![6, 11]]
def c045_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c045_computed : discoverEval 2 4 2 c045_A c045_O =
    (some c045_result, 175) := by decide +kernel
theorem c045_all_words : FiniteCodeCertificate (linearSystem c045_A c045_O) c045_result :=
  discoverEval_code 2 4 2 c045_A c045_O c045_result
    (congrArg Prod.fst c045_computed)
abbrev c046_R := ZMod (3^4)
def c046_A : Fin 2 → Mat c046_R 2 2 := ![![![51, 16], ![32, 34]], ![![41, 76], ![31, 9]]]
def c046_O : Mat c046_R 2 2 := ![![33, 46], ![31, 40]]
def c046_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c046_computed : discoverEval 3 4 2 c046_A c046_O =
    (some c046_result, 260) := by decide +kernel
theorem c046_all_words : FiniteCodeCertificate (linearSystem c046_A c046_O) c046_result :=
  discoverEval_code 3 4 2 c046_A c046_O c046_result
    (congrArg Prod.fst c046_computed)
abbrev c047_R := ZMod (5^4)
def c047_A : Fin 3 → Mat c047_R 2 2 := ![![![200, 67], ![241, 486]], ![![100, 72], ![366, 595]], ![![613, 261], ![168, 390]]]
def c047_O : Mat c047_R 1 2 := ![![0, 0]]
def c047_result : List (Test 3 1) := []
theorem c047_computed : discoverEval 5 4 2 c047_A c047_O =
    (some c047_result, 13) := by decide +kernel
theorem c047_all_words : FiniteCodeCertificate (linearSystem c047_A c047_O) c047_result :=
  discoverEval_code 5 4 2 c047_A c047_O c047_result
    (congrArg Prod.fst c047_computed)
end Komorebi.CostedRegression.Batch03
