module
public import NormalizedDiscovery
@[expose] public section
namespace Komorebi.NormalizedRegression.NormalizedComputed11
open Komorebi.Discovery Komorebi.Discovery.NormalizedBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c132_R := ZMod (2^3)
def c132_A : Fin 1 → Mat c132_R 2 2 := ![![![2, 6], ![1, 2]]]
def c132_O : Mat c132_R 2 2 := ![![0, 7], ![1, 2]]
def c132_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c132_computed : normalizedPrimeDiscover 2 3 2
    (fun a => rowRight (c132_A a)) c132_O = some c132_result := by decide +kernel
theorem c132_code : FiniteCodeCertificate (linearSystem c132_A c132_O) c132_result :=
  normalizedPrimeDiscover_code 2 3 2 c132_A c132_O c132_result c132_computed

abbrev c133_R := ZMod (3^3)
def c133_A : Fin 2 → Mat c133_R 2 2 := ![![![8, 19], ![16, 11]], ![![23, 7], ![3, 6]]]
def c133_O : Mat c133_R 1 2 := ![![0, 18]]
def c133_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c133_computed : normalizedPrimeDiscover 3 3 2
    (fun a => rowRight (c133_A a)) c133_O = some c133_result := by decide +kernel
theorem c133_code : FiniteCodeCertificate (linearSystem c133_A c133_O) c133_result :=
  normalizedPrimeDiscover_code 3 3 2 c133_A c133_O c133_result c133_computed

abbrev c134_R := ZMod (5^3)
def c134_A : Fin 3 → Mat c134_R 2 2 := ![![![117, 9], ![41, 14]], ![![20, 38], ![115, 7]], ![![68, 12], ![18, 83]]]
def c134_O : Mat c134_R 2 2 := ![![77, 74], ![33, 2]]
def c134_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c134_computed : normalizedPrimeDiscover 5 3 2
    (fun a => rowRight (c134_A a)) c134_O = some c134_result := by decide +kernel
theorem c134_code : FiniteCodeCertificate (linearSystem c134_A c134_O) c134_result :=
  normalizedPrimeDiscover_code 5 3 2 c134_A c134_O c134_result c134_computed

abbrev c135_R := ZMod (2^4)
def c135_A : Fin 1 → Mat c135_R 2 2 := ![![![9, 13], ![3, 8]]]
def c135_O : Mat c135_R 1 2 := ![![14, 10]]
def c135_result : List (Test 1 1) := [([], 0), ([0], 0)]
theorem c135_computed : normalizedPrimeDiscover 2 4 2
    (fun a => rowRight (c135_A a)) c135_O = some c135_result := by decide +kernel
theorem c135_code : FiniteCodeCertificate (linearSystem c135_A c135_O) c135_result :=
  normalizedPrimeDiscover_code 2 4 2 c135_A c135_O c135_result c135_computed

abbrev c136_R := ZMod (3^4)
def c136_A : Fin 2 → Mat c136_R 2 2 := ![![![2, 68], ![7, 64]], ![![56, 27], ![31, 42]]]
def c136_O : Mat c136_R 2 2 := ![![75, 9], ![78, 50]]
def c136_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 1)]
theorem c136_computed : normalizedPrimeDiscover 3 4 2
    (fun a => rowRight (c136_A a)) c136_O = some c136_result := by decide +kernel
theorem c136_code : FiniteCodeCertificate (linearSystem c136_A c136_O) c136_result :=
  normalizedPrimeDiscover_code 3 4 2 c136_A c136_O c136_result c136_computed

abbrev c137_R := ZMod (5^4)
def c137_A : Fin 3 → Mat c137_R 2 2 := ![![![160, 259], ![36, 470]], ![![112, 271], ![302, 184]], ![![600, 11], ![332, 216]]]
def c137_O : Mat c137_R 1 2 := ![![323, 376]]
def c137_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c137_computed : normalizedPrimeDiscover 5 4 2
    (fun a => rowRight (c137_A a)) c137_O = some c137_result := by decide +kernel
theorem c137_code : FiniteCodeCertificate (linearSystem c137_A c137_O) c137_result :=
  normalizedPrimeDiscover_code 5 4 2 c137_A c137_O c137_result c137_computed

abbrev c138_R := ZMod (2^5)
def c138_A : Fin 1 → Mat c138_R 2 2 := ![![![18, 26], ![8, 27]]]
def c138_O : Mat c138_R 2 2 := ![![0, 0], ![0, 0]]
def c138_result : List (Test 1 2) := []
theorem c138_computed : normalizedPrimeDiscover 2 5 2
    (fun a => rowRight (c138_A a)) c138_O = some c138_result := by decide +kernel
theorem c138_code : FiniteCodeCertificate (linearSystem c138_A c138_O) c138_result :=
  normalizedPrimeDiscover_code 2 5 2 c138_A c138_O c138_result c138_computed

abbrev c139_R := ZMod (3^5)
def c139_A : Fin 2 → Mat c139_R 2 2 := ![![![109, 100], ![137, 233]], ![![17, 239], ![10, 206]]]
def c139_O : Mat c139_R 1 2 := ![![65, 238]]
def c139_result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem c139_computed : normalizedPrimeDiscover 3 5 2
    (fun a => rowRight (c139_A a)) c139_O = some c139_result := by decide +kernel
theorem c139_code : FiniteCodeCertificate (linearSystem c139_A c139_O) c139_result :=
  normalizedPrimeDiscover_code 3 5 2 c139_A c139_O c139_result c139_computed

abbrev c140_R := ZMod (5^5)
def c140_A : Fin 3 → Mat c140_R 2 2 := ![![![2270, 2895], ![999, 1360]], ![![2693, 1881], ![1839, 1588]], ![![1611, 1262], ![2592, 864]]]
def c140_O : Mat c140_R 2 2 := ![![1250, 1250], ![2500, 0]]
def c140_result : List (Test 3 2) := [([], 0), ([], 1)]
theorem c140_computed : normalizedPrimeDiscover 5 5 2
    (fun a => rowRight (c140_A a)) c140_O = some c140_result := by decide +kernel
theorem c140_code : FiniteCodeCertificate (linearSystem c140_A c140_O) c140_result :=
  normalizedPrimeDiscover_code 5 5 2 c140_A c140_O c140_result c140_computed

abbrev c141_R := ZMod (2^1)
def c141_A : Fin 1 → Mat c141_R 3 3 := ![![![0, 0, 1], ![1, 1, 1], ![1, 1, 1]]]
def c141_O : Mat c141_R 1 3 := ![![0, 1, 1]]
def c141_result : List (Test 1 1) := [([], 0)]
theorem c141_computed : normalizedPrimeDiscover 2 1 3
    (fun a => rowRight (c141_A a)) c141_O = some c141_result := by decide +kernel
theorem c141_code : FiniteCodeCertificate (linearSystem c141_A c141_O) c141_result :=
  normalizedPrimeDiscover_code 2 1 3 c141_A c141_O c141_result c141_computed

abbrev c142_R := ZMod (3^1)
def c142_A : Fin 2 → Mat c142_R 3 3 := ![![![1, 1, 0], ![2, 1, 2], ![2, 2, 2]], ![![0, 0, 1], ![2, 1, 1], ![1, 2, 1]]]
def c142_O : Mat c142_R 2 3 := ![![1, 2, 1], ![2, 0, 2]]
def c142_result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem c142_computed : normalizedPrimeDiscover 3 1 3
    (fun a => rowRight (c142_A a)) c142_O = some c142_result := by decide +kernel
theorem c142_code : FiniteCodeCertificate (linearSystem c142_A c142_O) c142_result :=
  normalizedPrimeDiscover_code 3 1 3 c142_A c142_O c142_result c142_computed

abbrev c143_R := ZMod (5^1)
def c143_A : Fin 3 → Mat c143_R 3 3 := ![![![3, 0, 3], ![0, 1, 4], ![3, 3, 4]], ![![0, 0, 4], ![4, 4, 2], ![0, 4, 4]], ![![2, 1, 4], ![0, 1, 1], ![0, 3, 0]]]
def c143_O : Mat c143_R 1 3 := ![![2, 4, 1]]
def c143_result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0)]
theorem c143_computed : normalizedPrimeDiscover 5 1 3
    (fun a => rowRight (c143_A a)) c143_O = some c143_result := by decide +kernel
theorem c143_code : FiniteCodeCertificate (linearSystem c143_A c143_O) c143_result :=
  normalizedPrimeDiscover_code 5 1 3 c143_A c143_O c143_result c143_computed

end Komorebi.NormalizedRegression.NormalizedComputed11
