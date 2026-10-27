module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch02
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev c024_R := ZMod (2^2)
def c024_A : Fin 1 → Mat c024_R 1 1 := ![![![0]]]
def c024_O : Mat c024_R 2 1 := ![![1], ![1]]
def c024_result : List (Test 1 2) := [([], 0)]
theorem c024_computed : discoverEval 2 2 1 c024_A c024_O =
    (some c024_result, 34) := by decide +kernel
theorem c024_all_words : FiniteCodeCertificate (linearSystem c024_A c024_O) c024_result :=
  discoverEval_code 2 2 1 c024_A c024_O c024_result
    (congrArg Prod.fst c024_computed)
abbrev c025_R := ZMod (3^2)
def c025_A : Fin 2 → Mat c025_R 1 1 := ![![![6]], ![![0]]]
def c025_O : Mat c025_R 1 1 := ![![4]]
def c025_result : List (Test 2 1) := [([], 0)]
theorem c025_computed : discoverEval 3 2 1 c025_A c025_O =
    (some c025_result, 43) := by decide +kernel
theorem c025_all_words : FiniteCodeCertificate (linearSystem c025_A c025_O) c025_result :=
  discoverEval_code 3 2 1 c025_A c025_O c025_result
    (congrArg Prod.fst c025_computed)
abbrev c026_R := ZMod (5^2)
def c026_A : Fin 3 → Mat c026_R 1 1 := ![![![2]], ![![9]], ![![11]]]
def c026_O : Mat c026_R 2 1 := ![![21], ![17]]
def c026_result : List (Test 3 2) := [([], 0)]
theorem c026_computed : discoverEval 5 2 1 c026_A c026_O =
    (some c026_result, 62) := by decide +kernel
theorem c026_all_words : FiniteCodeCertificate (linearSystem c026_A c026_O) c026_result :=
  discoverEval_code 5 2 1 c026_A c026_O c026_result
    (congrArg Prod.fst c026_computed)
abbrev c027_R := ZMod (2^3)
def c027_A : Fin 1 → Mat c027_R 1 1 := ![![![5]]]
def c027_O : Mat c027_R 1 1 := ![![1]]
def c027_result : List (Test 1 1) := [([], 0)]
theorem c027_computed : discoverEval 2 3 1 c027_A c027_O =
    (some c027_result, 29) := by decide +kernel
theorem c027_all_words : FiniteCodeCertificate (linearSystem c027_A c027_O) c027_result :=
  discoverEval_code 2 3 1 c027_A c027_O c027_result
    (congrArg Prod.fst c027_computed)
abbrev c028_R := ZMod (3^3)
def c028_A : Fin 2 → Mat c028_R 1 1 := ![![![7]], ![![4]]]
def c028_O : Mat c028_R 2 1 := ![![18], ![9]]
def c028_result : List (Test 2 2) := [([], 0)]
theorem c028_computed : discoverEval 3 3 1 c028_A c028_O =
    (some c028_result, 48) := by decide +kernel
theorem c028_all_words : FiniteCodeCertificate (linearSystem c028_A c028_O) c028_result :=
  discoverEval_code 3 3 1 c028_A c028_O c028_result
    (congrArg Prod.fst c028_computed)
abbrev c029_R := ZMod (5^3)
def c029_A : Fin 3 → Mat c029_R 1 1 := ![![![121]], ![![45]], ![![80]]]
def c029_O : Mat c029_R 1 1 := ![![29]]
def c029_result : List (Test 3 1) := [([], 0)]
theorem c029_computed : discoverEval 5 3 1 c029_A c029_O =
    (some c029_result, 64) := by decide +kernel
theorem c029_all_words : FiniteCodeCertificate (linearSystem c029_A c029_O) c029_result :=
  discoverEval_code 5 3 1 c029_A c029_O c029_result
    (congrArg Prod.fst c029_computed)
abbrev c030_R := ZMod (2^4)
def c030_A : Fin 1 → Mat c030_R 1 1 := ![![![8]]]
def c030_O : Mat c030_R 2 1 := ![![3], ![4]]
def c030_result : List (Test 1 2) := [([], 0)]
theorem c030_computed : discoverEval 2 4 1 c030_A c030_O =
    (some c030_result, 41) := by decide +kernel
theorem c030_all_words : FiniteCodeCertificate (linearSystem c030_A c030_O) c030_result :=
  discoverEval_code 2 4 1 c030_A c030_O c030_result
    (congrArg Prod.fst c030_computed)
abbrev c031_R := ZMod (3^4)
def c031_A : Fin 2 → Mat c031_R 1 1 := ![![![11]], ![![54]]]
def c031_O : Mat c031_R 1 1 := ![![7]]
def c031_result : List (Test 2 1) := [([], 0)]
theorem c031_computed : discoverEval 3 4 1 c031_A c031_O =
    (some c031_result, 57) := by decide +kernel
theorem c031_all_words : FiniteCodeCertificate (linearSystem c031_A c031_O) c031_result :=
  discoverEval_code 3 4 1 c031_A c031_O c031_result
    (congrArg Prod.fst c031_computed)
abbrev c032_R := ZMod (5^4)
def c032_A : Fin 3 → Mat c032_R 1 1 := ![![![502]], ![![153]], ![![537]]]
def c032_O : Mat c032_R 2 1 := ![![327], ![292]]
def c032_result : List (Test 3 2) := [([], 0)]
theorem c032_computed : discoverEval 5 4 1 c032_A c032_O =
    (some c032_result, 97) := by decide +kernel
theorem c032_all_words : FiniteCodeCertificate (linearSystem c032_A c032_O) c032_result :=
  discoverEval_code 5 4 1 c032_A c032_O c032_result
    (congrArg Prod.fst c032_computed)
abbrev c033_R := ZMod (2^5)
def c033_A : Fin 1 → Mat c033_R 1 1 := ![![![3]]]
def c033_O : Mat c033_R 1 1 := ![![7]]
def c033_result : List (Test 1 1) := [([], 0)]
theorem c033_computed : discoverEval 2 5 1 c033_A c033_O =
    (some c033_result, 50) := by decide +kernel
theorem c033_all_words : FiniteCodeCertificate (linearSystem c033_A c033_O) c033_result :=
  discoverEval_code 2 5 1 c033_A c033_O c033_result
    (congrArg Prod.fst c033_computed)
abbrev c034_R := ZMod (3^5)
def c034_A : Fin 2 → Mat c034_R 1 1 := ![![![104]], ![![102]]]
def c034_O : Mat c034_R 2 1 := ![![0], ![0]]
def c034_result : List (Test 2 2) := []
theorem c034_computed : discoverEval 3 5 1 c034_A c034_O =
    (some c034_result, 10) := by decide +kernel
theorem c034_all_words : FiniteCodeCertificate (linearSystem c034_A c034_O) c034_result :=
  discoverEval_code 3 5 1 c034_A c034_O c034_result
    (congrArg Prod.fst c034_computed)
abbrev c035_R := ZMod (5^5)
def c035_A : Fin 3 → Mat c035_R 1 1 := ![![![227]], ![![1859]], ![![2070]]]
def c035_O : Mat c035_R 1 1 := ![![625]]
def c035_result : List (Test 3 1) := [([], 0)]
theorem c035_computed : discoverEval 5 5 1 c035_A c035_O =
    (some c035_result, 43) := by decide +kernel
theorem c035_all_words : FiniteCodeCertificate (linearSystem c035_A c035_O) c035_result :=
  discoverEval_code 5 5 1 c035_A c035_O c035_result
    (congrArg Prod.fst c035_computed)
end Komorebi.CostedRegression.Batch02
