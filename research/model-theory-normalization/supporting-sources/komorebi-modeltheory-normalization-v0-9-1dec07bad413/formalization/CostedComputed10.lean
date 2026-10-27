module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch10
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev c120_R := ZMod (2^4)
def c120_A : Fin 1 → Mat c120_R 1 1 := ![![![10]]]
def c120_O : Mat c120_R 2 1 := ![![3], ![7]]
def c120_result : List (Test 1 2) := [([], 0)]
theorem c120_computed : discoverEval 2 4 1 c120_A c120_O =
    (some c120_result, 41) := by decide +kernel
theorem c120_all_words : FiniteCodeCertificate (linearSystem c120_A c120_O) c120_result :=
  discoverEval_code 2 4 1 c120_A c120_O c120_result
    (congrArg Prod.fst c120_computed)
abbrev c121_R := ZMod (3^4)
def c121_A : Fin 2 → Mat c121_R 1 1 := ![![![61]], ![![12]]]
def c121_O : Mat c121_R 1 1 := ![![71]]
def c121_result : List (Test 2 1) := [([], 0)]
theorem c121_computed : discoverEval 3 4 1 c121_A c121_O =
    (some c121_result, 50) := by decide +kernel
theorem c121_all_words : FiniteCodeCertificate (linearSystem c121_A c121_O) c121_result :=
  discoverEval_code 3 4 1 c121_A c121_O c121_result
    (congrArg Prod.fst c121_computed)
abbrev c122_R := ZMod (5^4)
def c122_A : Fin 3 → Mat c122_R 1 1 := ![![![420]], ![![304]], ![![259]]]
def c122_O : Mat c122_R 2 1 := ![![617], ![181]]
def c122_result : List (Test 3 2) := [([], 0)]
theorem c122_computed : discoverEval 5 4 1 c122_A c122_O =
    (some c122_result, 62) := by decide +kernel
theorem c122_all_words : FiniteCodeCertificate (linearSystem c122_A c122_O) c122_result :=
  discoverEval_code 5 4 1 c122_A c122_O c122_result
    (congrArg Prod.fst c122_computed)
abbrev c123_R := ZMod (2^5)
def c123_A : Fin 1 → Mat c123_R 1 1 := ![![![5]]]
def c123_O : Mat c123_R 1 1 := ![![18]]
def c123_result : List (Test 1 1) := [([], 0)]
theorem c123_computed : discoverEval 2 5 1 c123_A c123_O =
    (some c123_result, 50) := by decide +kernel
theorem c123_all_words : FiniteCodeCertificate (linearSystem c123_A c123_O) c123_result :=
  discoverEval_code 2 5 1 c123_A c123_O c123_result
    (congrArg Prod.fst c123_computed)
abbrev c124_R := ZMod (3^5)
def c124_A : Fin 2 → Mat c124_R 1 1 := ![![![97]], ![![142]]]
def c124_O : Mat c124_R 2 1 := ![![171], ![39]]
def c124_result : List (Test 2 2) := [([], 0), ([], 1)]
theorem c124_computed : discoverEval 3 5 1 c124_A c124_O =
    (some c124_result, 114) := by decide +kernel
theorem c124_all_words : FiniteCodeCertificate (linearSystem c124_A c124_O) c124_result :=
  discoverEval_code 3 5 1 c124_A c124_O c124_result
    (congrArg Prod.fst c124_computed)
abbrev c125_R := ZMod (5^5)
def c125_A : Fin 3 → Mat c125_R 1 1 := ![![![2943]], ![![2010]], ![![2491]]]
def c125_O : Mat c125_R 1 1 := ![![0]]
def c125_result : List (Test 3 1) := []
theorem c125_computed : discoverEval 5 5 1 c125_A c125_O =
    (some c125_result, 5) := by decide +kernel
theorem c125_all_words : FiniteCodeCertificate (linearSystem c125_A c125_O) c125_result :=
  discoverEval_code 5 5 1 c125_A c125_O c125_result
    (congrArg Prod.fst c125_computed)
abbrev c126_R := ZMod (2^1)
def c126_A : Fin 1 → Mat c126_R 2 2 := ![![![0, 0], ![0, 1]]]
def c126_O : Mat c126_R 2 2 := ![![1, 1], ![1, 1]]
def c126_result : List (Test 1 2) := [([], 0), ([0], 0)]
theorem c126_computed : discoverEval 2 1 2 c126_A c126_O =
    (some c126_result, 144) := by decide +kernel
theorem c126_all_words : FiniteCodeCertificate (linearSystem c126_A c126_O) c126_result :=
  discoverEval_code 2 1 2 c126_A c126_O c126_result
    (congrArg Prod.fst c126_computed)
abbrev c127_R := ZMod (3^1)
def c127_A : Fin 2 → Mat c127_R 2 2 := ![![![1, 2], ![0, 1]], ![![1, 1], ![2, 1]]]
def c127_O : Mat c127_R 1 2 := ![![2, 2]]
def c127_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c127_computed : discoverEval 3 1 2 c127_A c127_O =
    (some c127_result, 214) := by decide +kernel
theorem c127_all_words : FiniteCodeCertificate (linearSystem c127_A c127_O) c127_result :=
  discoverEval_code 3 1 2 c127_A c127_O c127_result
    (congrArg Prod.fst c127_computed)
abbrev c128_R := ZMod (5^1)
def c128_A : Fin 3 → Mat c128_R 2 2 := ![![![0, 1], ![2, 0]], ![![3, 2], ![2, 2]], ![![3, 3], ![3, 0]]]
def c128_O : Mat c128_R 2 2 := ![![0, 4], ![4, 4]]
def c128_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c128_computed : discoverEval 5 1 2 c128_A c128_O =
    (some c128_result, 233) := by decide +kernel
theorem c128_all_words : FiniteCodeCertificate (linearSystem c128_A c128_O) c128_result :=
  discoverEval_code 5 1 2 c128_A c128_O c128_result
    (congrArg Prod.fst c128_computed)
abbrev c129_R := ZMod (2^2)
def c129_A : Fin 1 → Mat c129_R 2 2 := ![![![0, 2], ![1, 3]]]
def c129_O : Mat c129_R 1 2 := ![![3, 1]]
def c129_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c129_computed : discoverEval 2 2 2 c129_A c129_O =
    (some c129_result, 147) := by decide +kernel
theorem c129_all_words : FiniteCodeCertificate (linearSystem c129_A c129_O) c129_result :=
  discoverEval_code 2 2 2 c129_A c129_O c129_result
    (congrArg Prod.fst c129_computed)
abbrev c130_R := ZMod (3^2)
def c130_A : Fin 2 → Mat c130_R 2 2 := ![![![8, 7], ![3, 7]], ![![2, 0], ![8, 3]]]
def c130_O : Mat c130_R 2 2 := ![![1, 0], ![6, 6]]
def c130_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c130_computed : discoverEval 3 2 2 c130_A c130_O =
    (some c130_result, 306) := by decide +kernel
theorem c130_all_words : FiniteCodeCertificate (linearSystem c130_A c130_O) c130_result :=
  discoverEval_code 3 2 2 c130_A c130_O c130_result
    (congrArg Prod.fst c130_computed)
abbrev c131_R := ZMod (5^2)
def c131_A : Fin 3 → Mat c131_R 2 2 := ![![![6, 12], ![12, 5]], ![![13, 3], ![10, 22]], ![![2, 2], ![21, 19]]]
def c131_O : Mat c131_R 1 2 := ![![3, 17]]
def c131_result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem c131_computed : discoverEval 5 2 2 c131_A c131_O =
    (some c131_result, 274) := by decide +kernel
theorem c131_all_words : FiniteCodeCertificate (linearSystem c131_A c131_O) c131_result :=
  discoverEval_code 5 2 2 c131_A c131_O c131_result
    (congrArg Prod.fst c131_computed)
end Komorebi.CostedRegression.Batch10
