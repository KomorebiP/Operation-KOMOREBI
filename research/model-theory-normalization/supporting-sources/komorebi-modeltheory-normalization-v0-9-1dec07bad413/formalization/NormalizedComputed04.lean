module
public import NormalizedDiscovery
@[expose] public section
namespace Komorebi.NormalizedRegression.NormalizedComputed04
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c048_R := ZMod (2^5)
def c048_A : Fin 1 → Mat c048_R 2 2 := ![![![23, 0], ![13, 18]]]
def c048_O : Mat c048_R 2 2 := ![![0, 1], ![15, 19]]
def c048_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c048_computed : normalizedPrimeDiscover 2 5 2
    (fun a => rowRight (c048_A a)) c048_O = some c048_result := by decide +kernel
theorem c048_code : FiniteCodeCertificate (linearSystem c048_A c048_O) c048_result :=
  normalizedPrimeDiscover_code 2 5 2 c048_A c048_O c048_result c048_computed

abbrev c049_R := ZMod (3^5)
def c049_A : Fin 2 → Mat c049_R 2 2 := ![![![227, 25], ![108, 55]], ![![206, 55], ![85, 197]]]
def c049_O : Mat c049_R 1 2 := ![![162, 0]]
def c049_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c049_computed : normalizedPrimeDiscover 3 5 2
    (fun a => rowRight (c049_A a)) c049_O = some c049_result := by decide +kernel
theorem c049_code : FiniteCodeCertificate (linearSystem c049_A c049_O) c049_result :=
  normalizedPrimeDiscover_code 3 5 2 c049_A c049_O c049_result c049_computed

abbrev c050_R := ZMod (5^5)
def c050_A : Fin 3 → Mat c050_R 2 2 := ![![![805, 472], ![3032, 359]], ![![2615, 469], ![2949, 110]], ![![1617, 1101], ![2979, 2199]]]
def c050_O : Mat c050_R 2 2 := ![![2612, 2325], ![435, 42]]
def c050_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c050_computed : normalizedPrimeDiscover 5 5 2
    (fun a => rowRight (c050_A a)) c050_O = some c050_result := by decide +kernel
theorem c050_code : FiniteCodeCertificate (linearSystem c050_A c050_O) c050_result :=
  normalizedPrimeDiscover_code 5 5 2 c050_A c050_O c050_result c050_computed

abbrev c051_R := ZMod (2^1)
def c051_A : Fin 1 → Mat c051_R 3 3 := ![![![1, 0, 1], ![0, 1, 0], ![0, 1, 1]]]
def c051_O : Mat c051_R 1 3 := ![![0, 1, 1]]
def c051_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c051_computed : normalizedPrimeDiscover 2 1 3
    (fun a => rowRight (c051_A a)) c051_O = some c051_result := by decide +kernel
theorem c051_code : FiniteCodeCertificate (linearSystem c051_A c051_O) c051_result :=
  normalizedPrimeDiscover_code 2 1 3 c051_A c051_O c051_result c051_computed

abbrev c052_R := ZMod (3^1)
def c052_A : Fin 2 → Mat c052_R 3 3 := ![![![2, 0, 1], ![1, 2, 2], ![2, 1, 0]], ![![0, 0, 0], ![1, 1, 2], ![1, 0, 1]]]
def c052_O : Mat c052_R 2 3 := ![![0, 0, 1], ![1, 0, 2]]
def c052_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c052_computed : normalizedPrimeDiscover 3 1 3
    (fun a => rowRight (c052_A a)) c052_O = some c052_result := by decide +kernel
theorem c052_code : FiniteCodeCertificate (linearSystem c052_A c052_O) c052_result :=
  normalizedPrimeDiscover_code 3 1 3 c052_A c052_O c052_result c052_computed

abbrev c053_R := ZMod (5^1)
def c053_A : Fin 3 → Mat c053_R 3 3 := ![![![0, 3, 0], ![3, 1, 2], ![3, 3, 4]], ![![3, 3, 3], ![1, 0, 3], ![3, 4, 0]], ![![1, 4, 3], ![3, 2, 2], ![4, 2, 3]]]
def c053_O : Mat c053_R 1 3 := ![![1, 2, 0]]
def c053_result : List (Test 3 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c053_computed : normalizedPrimeDiscover 5 1 3
    (fun a => rowRight (c053_A a)) c053_O = some c053_result := by decide +kernel
theorem c053_code : FiniteCodeCertificate (linearSystem c053_A c053_O) c053_result :=
  normalizedPrimeDiscover_code 5 1 3 c053_A c053_O c053_result c053_computed

abbrev c054_R := ZMod (2^2)
def c054_A : Fin 1 → Mat c054_R 3 3 := ![![![1, 0, 2], ![1, 1, 1], ![0, 1, 3]]]
def c054_O : Mat c054_R 2 3 := ![![0, 1, 1], ![2, 2, 0]]
def c054_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0)]
theorem c054_computed : normalizedPrimeDiscover 2 2 3
    (fun a => rowRight (c054_A a)) c054_O = some c054_result := by decide +kernel
theorem c054_code : FiniteCodeCertificate (linearSystem c054_A c054_O) c054_result :=
  normalizedPrimeDiscover_code 2 2 3 c054_A c054_O c054_result c054_computed

abbrev c055_R := ZMod (3^2)
def c055_A : Fin 2 → Mat c055_R 3 3 := ![![![5, 4, 5], ![0, 1, 5], ![7, 0, 3]], ![![3, 2, 5], ![5, 3, 3], ![4, 4, 8]]]
def c055_O : Mat c055_R 1 3 := ![![2, 1, 6]]
def c055_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c055_computed : normalizedPrimeDiscover 3 2 3
    (fun a => rowRight (c055_A a)) c055_O = some c055_result := by decide +kernel
theorem c055_code : FiniteCodeCertificate (linearSystem c055_A c055_O) c055_result :=
  normalizedPrimeDiscover_code 3 2 3 c055_A c055_O c055_result c055_computed

abbrev c056_R := ZMod (5^2)
def c056_A : Fin 3 → Mat c056_R 3 3 := ![![![20, 20, 9], ![17, 9, 4], ![5, 7, 18]], ![![20, 23, 3], ![24, 6, 22], ![8, 8, 1]], ![![14, 13, 8], ![14, 24, 8], ![11, 15, 24]]]
def c056_O : Mat c056_R 2 3 := ![![5, 10, 20], ![0, 20, 5]]
def c056_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0)]
theorem c056_computed : normalizedPrimeDiscover 5 2 3
    (fun a => rowRight (c056_A a)) c056_O = some c056_result := by decide +kernel
theorem c056_code : FiniteCodeCertificate (linearSystem c056_A c056_O) c056_result :=
  normalizedPrimeDiscover_code 5 2 3 c056_A c056_O c056_result c056_computed

abbrev c057_R := ZMod (2^3)
def c057_A : Fin 1 → Mat c057_R 3 3 := ![![![3, 0, 4], ![3, 7, 3], ![2, 5, 6]]]
def c057_O : Mat c057_R 1 3 := ![![0, 6, 5]]
def c057_result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0)]
theorem c057_computed : normalizedPrimeDiscover 2 3 3
    (fun a => rowRight (c057_A a)) c057_O = some c057_result := by decide +kernel
theorem c057_code : FiniteCodeCertificate (linearSystem c057_A c057_O) c057_result :=
  normalizedPrimeDiscover_code 2 3 3 c057_A c057_O c057_result c057_computed

abbrev c058_R := ZMod (3^3)
def c058_A : Fin 2 → Mat c058_R 3 3 := ![![![23, 16, 24], ![20, 19, 17], ![11, 21, 2]], ![![26, 6, 21], ![13, 25, 16], ![3, 10, 14]]]
def c058_O : Mat c058_R 2 3 := ![![20, 25, 26], ![2, 15, 14]]
def c058_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c058_computed : normalizedPrimeDiscover 3 3 3
    (fun a => rowRight (c058_A a)) c058_O = some c058_result := by decide +kernel
theorem c058_code : FiniteCodeCertificate (linearSystem c058_A c058_O) c058_result :=
  normalizedPrimeDiscover_code 3 3 3 c058_A c058_O c058_result c058_computed

abbrev c059_R := ZMod (5^3)
def c059_A : Fin 3 → Mat c059_R 3 3 := ![![![18, 14, 51], ![35, 91, 21], ![104, 16, 39]], ![![35, 111, 1], ![82, 58, 68], ![22, 85, 107]], ![![86, 36, 8], ![94, 45, 23], ![55, 13, 20]]]
def c059_O : Mat c059_R 1 3 := ![![83, 54, 59]]
def c059_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c059_computed : normalizedPrimeDiscover 5 3 3
    (fun a => rowRight (c059_A a)) c059_O = some c059_result := by decide +kernel
theorem c059_code : FiniteCodeCertificate (linearSystem c059_A c059_O) c059_result :=
  normalizedPrimeDiscover_code 5 3 3 c059_A c059_O c059_result c059_computed

end Komorebi.NormalizedRegression.NormalizedComputed04
