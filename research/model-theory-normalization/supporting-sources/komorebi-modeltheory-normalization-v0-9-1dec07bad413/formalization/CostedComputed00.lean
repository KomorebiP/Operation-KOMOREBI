module
public import CostedBounds
@[expose] public section
namespace Komorebi.CostedRegression.Batch00
open Komorebi.Costed Komorebi.Discovery
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev c000_R := ZMod (2^4)
def c000_A : Fin 1 → Mat c000_R 8 8 := ![![![0, 1, 0, 0, 0, 0, 0, 0], ![0, 0, 1, 0, 0, 0, 0, 0], ![0, 0, 0, 1, 0, 0, 0, 0], ![0, 0, 0, 0, 1, 0, 0, 0], ![0, 0, 0, 0, 0, 1, 0, 0], ![0, 0, 0, 0, 0, 0, 1, 0], ![0, 0, 0, 0, 0, 0, 0, 1], ![0, 0, 0, 0, 0, 0, 0, 0]]]
def c000_O : Mat c000_R 1 8 := ![![1, 0, 0, 0, 0, 0, 0, 0]]
def c000_result : List (Test 1 1) := [([], 0), ([0], 0), ([0, 0], 0), ([0, 0, 0], 0), ([0, 0, 0, 0], 0), ([0, 0, 0, 0, 0], 0), ([0, 0, 0, 0, 0, 0], 0), ([0, 0, 0, 0, 0, 0, 0], 0)]
theorem c000_computed : discoverEval 2 4 8 c000_A c000_O =
    (some c000_result, 8765) := by decide +kernel
theorem c000_all_words : FiniteCodeCertificate (linearSystem c000_A c000_O) c000_result :=
  discoverEval_code 2 4 8 c000_A c000_O c000_result
    (congrArg Prod.fst c000_computed)
abbrev c001_R := ZMod (2^2)
def c001_A : Fin 2 → Mat c001_R 4 4 := ![![![3, 2, 0, 2], ![1, 2, 3, 1], ![1, 2, 1, 3], ![3, 3, 3, 0]], ![![2, 0, 0, 0], ![1, 0, 2, 1], ![2, 0, 0, 2], ![2, 3, 2, 2]]]
def c001_O : Mat c001_R 1 4 := ![![3, 0, 0, 0]]
def c001_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c001_computed : discoverEval 2 2 4 c001_A c001_O =
    (some c001_result, 557) := by decide +kernel
theorem c001_all_words : FiniteCodeCertificate (linearSystem c001_A c001_O) c001_result :=
  discoverEval_code 2 2 4 c001_A c001_O c001_result
    (congrArg Prod.fst c001_computed)
abbrev c002_R := ZMod (2^2)
def c002_A : Fin 2 → Mat c002_R 6 6 := ![![![1, 2, 3, 0, 0, 1], ![3, 0, 2, 1, 1, 1], ![0, 2, 2, 1, 1, 1], ![0, 1, 2, 2, 3, 1], ![1, 2, 0, 2, 1, 0], ![0, 0, 2, 0, 0, 3]], ![![1, 0, 1, 2, 0, 1], ![2, 3, 2, 3, 1, 1], ![2, 0, 0, 3, 1, 1], ![3, 1, 3, 1, 2, 0], ![1, 3, 3, 3, 2, 0], ![0, 0, 0, 0, 2, 2]]]
def c002_O : Mat c002_R 1 6 := ![![2, 2, 0, 0, 2, 1]]
def c002_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c002_computed : discoverEval 2 2 6 c002_A c002_O =
    (some c002_result, 1220) := by decide +kernel
theorem c002_all_words : FiniteCodeCertificate (linearSystem c002_A c002_O) c002_result :=
  discoverEval_code 2 2 6 c002_A c002_O c002_result
    (congrArg Prod.fst c002_computed)
abbrev c003_R := ZMod (2^3)
def c003_A : Fin 2 → Mat c003_R 4 4 := ![![![4, 1, 2, 5], ![7, 6, 1, 2], ![3, 5, 4, 0], ![4, 2, 4, 3]], ![![5, 7, 1, 2], ![1, 6, 7, 0], ![7, 5, 4, 2], ![0, 4, 2, 2]]]
def c003_O : Mat c003_R 1 4 := ![![2, 0, 6, 5]]
def c003_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c003_computed : discoverEval 2 3 4 c003_A c003_O =
    (some c003_result, 613) := by decide +kernel
theorem c003_all_words : FiniteCodeCertificate (linearSystem c003_A c003_O) c003_result :=
  discoverEval_code 2 3 4 c003_A c003_O c003_result
    (congrArg Prod.fst c003_computed)
abbrev c004_R := ZMod (2^3)
def c004_A : Fin 2 → Mat c004_R 6 6 := ![![![1, 3, 5, 6, 1, 6], ![4, 4, 1, 2, 3, 5], ![6, 4, 6, 0, 0, 5], ![0, 3, 7, 0, 5, 3], ![0, 0, 0, 6, 3, 1], ![4, 7, 4, 2, 7, 7]], ![![3, 3, 0, 3, 0, 2], ![6, 3, 6, 5, 0, 2], ![5, 5, 6, 2, 0, 1], ![7, 1, 7, 1, 1, 4], ![2, 1, 6, 0, 7, 2], ![7, 2, 6, 5, 6, 1]]]
def c004_O : Mat c004_R 1 6 := ![![4, 1, 3, 4, 6, 1]]
def c004_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c004_computed : discoverEval 2 3 6 c004_A c004_O =
    (some c004_result, 1291) := by decide +kernel
theorem c004_all_words : FiniteCodeCertificate (linearSystem c004_A c004_O) c004_result :=
  discoverEval_code 2 3 6 c004_A c004_O c004_result
    (congrArg Prod.fst c004_computed)
abbrev c005_R := ZMod (2^5)
def c005_A : Fin 2 → Mat c005_R 4 4 := ![![![30, 8, 13, 31], ![6, 21, 0, 1], ![22, 24, 31, 8], ![3, 28, 31, 9]], ![![27, 14, 23, 9], ![24, 18, 17, 27], ![18, 4, 15, 30], ![25, 6, 11, 12]]]
def c005_O : Mat c005_R 1 4 := ![![27, 7, 11, 7]]
def c005_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c005_computed : discoverEval 2 5 4 c005_A c005_O =
    (some c005_result, 669) := by decide +kernel
theorem c005_all_words : FiniteCodeCertificate (linearSystem c005_A c005_O) c005_result :=
  discoverEval_code 2 5 4 c005_A c005_O c005_result
    (congrArg Prod.fst c005_computed)
abbrev c006_R := ZMod (2^5)
def c006_A : Fin 2 → Mat c006_R 6 6 := ![![![7, 1, 3, 30, 26, 12], ![14, 0, 21, 17, 5, 24], ![26, 11, 24, 15, 20, 19], ![16, 3, 19, 14, 28, 19], ![12, 26, 25, 26, 13, 7], ![8, 19, 15, 14, 0, 7]], ![![9, 5, 8, 10, 20, 20], ![23, 15, 31, 8, 29, 7], ![21, 5, 31, 15, 0, 17], ![24, 17, 30, 0, 18, 22], ![28, 9, 12, 2, 4, 8], ![25, 15, 26, 14, 14, 8]]]
def c006_O : Mat c006_R 1 6 := ![![13, 18, 20, 28, 0, 27]]
def c006_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c006_computed : discoverEval 2 5 6 c006_A c006_O =
    (some c006_result, 1332) := by decide +kernel
theorem c006_all_words : FiniteCodeCertificate (linearSystem c006_A c006_O) c006_result :=
  discoverEval_code 2 5 6 c006_A c006_O c006_result
    (congrArg Prod.fst c006_computed)
abbrev c007_R := ZMod (3^2)
def c007_A : Fin 2 → Mat c007_R 4 4 := ![![![0, 0, 7, 6], ![8, 4, 5, 8], ![8, 3, 6, 5], ![7, 6, 1, 2]], ![![5, 0, 8, 0], ![3, 5, 4, 1], ![3, 6, 8, 6], ![6, 6, 5, 7]]]
def c007_O : Mat c007_R 1 4 := ![![6, 2, 0, 5]]
def c007_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c007_computed : discoverEval 3 2 4 c007_A c007_O =
    (some c007_result, 606) := by decide +kernel
theorem c007_all_words : FiniteCodeCertificate (linearSystem c007_A c007_O) c007_result :=
  discoverEval_code 3 2 4 c007_A c007_O c007_result
    (congrArg Prod.fst c007_computed)
abbrev c008_R := ZMod (3^2)
def c008_A : Fin 2 → Mat c008_R 6 6 := ![![![6, 1, 1, 2, 4, 0], ![7, 7, 3, 2, 2, 3], ![4, 0, 4, 5, 8, 6], ![7, 8, 3, 8, 2, 4], ![2, 8, 4, 3, 6, 1], ![3, 5, 1, 5, 6, 0]], ![![3, 6, 2, 3, 2, 3], ![7, 2, 2, 3, 5, 3], ![6, 8, 0, 1, 2, 4], ![0, 2, 7, 4, 5, 0], ![0, 8, 7, 2, 2, 1], ![0, 4, 5, 7, 1, 8]]]
def c008_O : Mat c008_R 1 6 := ![![5, 7, 0, 4, 3, 7]]
def c008_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c008_computed : discoverEval 3 2 6 c008_A c008_O =
    (some c008_result, 1311) := by decide +kernel
theorem c008_all_words : FiniteCodeCertificate (linearSystem c008_A c008_O) c008_result :=
  discoverEval_code 3 2 6 c008_A c008_O c008_result
    (congrArg Prod.fst c008_computed)
abbrev c009_R := ZMod (3^3)
def c009_A : Fin 2 → Mat c009_R 4 4 := ![![![6, 5, 10, 1], ![22, 10, 26, 13], ![0, 15, 1, 15], ![20, 12, 4, 24]], ![![12, 0, 10, 12], ![7, 16, 7, 17], ![0, 12, 11, 21], ![26, 12, 23, 8]]]
def c009_O : Mat c009_R 1 4 := ![![18, 12, 1, 21]]
def c009_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c009_computed : discoverEval 3 3 4 c009_A c009_O =
    (some c009_result, 627) := by decide +kernel
theorem c009_all_words : FiniteCodeCertificate (linearSystem c009_A c009_O) c009_result :=
  discoverEval_code 3 3 4 c009_A c009_O c009_result
    (congrArg Prod.fst c009_computed)
abbrev c010_R := ZMod (3^3)
def c010_A : Fin 2 → Mat c010_R 6 6 := ![![![0, 8, 10, 19, 2, 8], ![23, 24, 3, 15, 20, 1], ![1, 2, 13, 13, 24, 25], ![13, 26, 0, 17, 24, 9], ![5, 20, 20, 2, 9, 25], ![12, 0, 23, 14, 0, 14]], ![![19, 17, 1, 22, 13, 1], ![25, 22, 23, 10, 26, 11], ![26, 7, 18, 16, 26, 20], ![8, 17, 25, 25, 24, 1], ![14, 3, 22, 20, 0, 16], ![10, 12, 14, 24, 1, 17]]]
def c010_O : Mat c010_R 1 6 := ![![24, 17, 7, 14, 13, 23]]
def c010_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c010_computed : discoverEval 3 3 6 c010_A c010_O =
    (some c010_result, 1339) := by decide +kernel
theorem c010_all_words : FiniteCodeCertificate (linearSystem c010_A c010_O) c010_result :=
  discoverEval_code 3 3 6 c010_A c010_O c010_result
    (congrArg Prod.fst c010_computed)
abbrev c011_R := ZMod (3^5)
def c011_A : Fin 2 → Mat c011_R 4 4 := ![![![199, 37, 95, 215], ![58, 147, 109, 227], ![74, 21, 172, 53], ![154, 128, 52, 81]], ![![51, 210, 126, 119], ![71, 171, 220, 167], ![148, 158, 173, 93], ![210, 19, 62, 104]]]
def c011_O : Mat c011_R 1 4 := ![![202, 236, 238, 71]]
def c011_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c011_computed : discoverEval 3 5 4 c011_A c011_O =
    (some c011_result, 669) := by decide +kernel
theorem c011_all_words : FiniteCodeCertificate (linearSystem c011_A c011_O) c011_result :=
  discoverEval_code 3 5 4 c011_A c011_O c011_result
    (congrArg Prod.fst c011_computed)
end Komorebi.CostedRegression.Batch00
