module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.EchelonComputed09
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
open Komorebi.ModelTheory Komorebi.ModelTheory.Standard
set_option maxRecDepth 100000
set_option maxHeartbeats 16000000
abbrev c108_R := ZMod (2^5)
def c108_A : Fin 1 → Mat c108_R 6 6 := ![![![2, 29, 20, 13, 9, 8], ![29, 13, 18, 27, 27, 26], ![18, 28, 13, 11, 16, 31], ![5, 27, 2, 29, 9, 26], ![5, 8, 8, 4, 5, 6], ![7, 10, 26, 15, 8, 3]]]
def c108_O : Mat c108_R 2 6 := ![![31, 20, 26, 31, 24, 4], ![5, 27, 25, 8, 27, 1]]
def c108_result : List (Test 1 2) := [([], 0), ([], 1), ([0], 0), ([0], 1), ([0,0], 0), ([0,0], 1)]
theorem c108_computed : fastPrimeDiscover 2 5 6
    (fun a => rowRight (c108_A a)) c108_O = some c108_result := by decide +kernel
theorem c108_code : FiniteCodeCertificate (linearSystem c108_A c108_O) c108_result :=
  fastPrimeDiscover_code 2 5 6 c108_A c108_O c108_result c108_computed

abbrev c109_R := ZMod (3^5)
def c109_A : Fin 2 → Mat c109_R 6 6 := ![![![224, 222, 200, 133, 150, 117], ![211, 27, 21, 16, 33, 38], ![49, 200, 26, 194, 114, 187], ![70, 139, 218, 132, 171, 192], ![238, 0, 168, 230, 229, 236], ![23, 70, 137, 144, 48, 203]], ![![90, 175, 5, 73, 67, 160], ![74, 133, 78, 68, 78, 162], ![63, 229, 178, 221, 54, 180], ![195, 221, 39, 206, 141, 168], ![64, 86, 71, 3, 86, 88], ![87, 215, 112, 35, 116, 178]]]
def c109_O : Mat c109_R 1 6 := ![![179, 134, 33, 180, 172, 25]]
def c109_result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0), ([1,1], 0), ([1,0,1], 0)]
theorem c109_computed : fastPrimeDiscover 3 5 6
    (fun a => rowRight (c109_A a)) c109_O = some c109_result := by decide +kernel
theorem c109_code : FiniteCodeCertificate (linearSystem c109_A c109_O) c109_result :=
  fastPrimeDiscover_code 3 5 6 c109_A c109_O c109_result c109_computed

abbrev c110_R := ZMod (5^5)
def c110_A : Fin 3 → Mat c110_R 6 6 := ![![![724, 1560, 885, 2546, 1128, 729], ![73, 2514, 710, 2659, 160, 1800], ![1038, 2447, 616, 2163, 2311, 2969], ![2970, 263, 1847, 961, 745, 1890], ![2447, 1128, 1684, 1877, 612, 2102], ![790, 470, 1208, 114, 2390, 1720]], ![![2979, 2844, 2145, 2544, 2434, 782], ![2981, 1543, 154, 1441, 1023, 43], ![2014, 2649, 2887, 1530, 1998, 405], ![188, 1504, 1199, 381, 945, 1093], ![1804, 2691, 2080, 478, 1283, 777], ![2434, 940, 2908, 2156, 277, 2431]], ![![2327, 1915, 1476, 2667, 62, 2263], ![995, 76, 1216, 1433, 2644, 551], ![2062, 772, 15, 1719, 3080, 3121], ![663, 2382, 1743, 773, 2452, 1376], ![959, 144, 2650, 886, 2594, 1100], ![1779, 1359, 651, 244, 1473, 2482]]]
def c110_O : Mat c110_R 2 6 := ![![1423, 806, 1109, 737, 2988, 2679], ![1430, 2147, 226, 542, 925, 1357]]
def c110_result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0), ([0], 1), ([0,0], 0)]
theorem c110_computed : fastPrimeDiscover 5 5 6
    (fun a => rowRight (c110_A a)) c110_O = some c110_result := by decide +kernel
theorem c110_code : FiniteCodeCertificate (linearSystem c110_A c110_O) c110_result :=
  fastPrimeDiscover_code 5 5 6 c110_A c110_O c110_result c110_computed

abbrev c111_R := ZMod (2^1)
def c111_A : Fin 1 → Mat c111_R 1 1 := ![![![1]]]
def c111_O : Mat c111_R 1 1 := ![![0]]
def c111_result : List (Test 1 1) := []
theorem c111_computed : fastPrimeDiscover 2 1 1
    (fun a => rowRight (c111_A a)) c111_O = some c111_result := by decide +kernel
theorem c111_code : FiniteCodeCertificate (linearSystem c111_A c111_O) c111_result :=
  fastPrimeDiscover_code 2 1 1 c111_A c111_O c111_result c111_computed

abbrev c112_R := ZMod (3^1)
def c112_A : Fin 2 → Mat c112_R 1 1 := ![![![1]], ![![0]]]
def c112_O : Mat c112_R 2 1 := ![![0], ![0]]
def c112_result : List (Test 2 2) := []
theorem c112_computed : fastPrimeDiscover 3 1 1
    (fun a => rowRight (c112_A a)) c112_O = some c112_result := by decide +kernel
theorem c112_code : FiniteCodeCertificate (linearSystem c112_A c112_O) c112_result :=
  fastPrimeDiscover_code 3 1 1 c112_A c112_O c112_result c112_computed

abbrev c113_R := ZMod (5^1)
def c113_A : Fin 3 → Mat c113_R 1 1 := ![![![4]], ![![4]], ![![4]]]
def c113_O : Mat c113_R 1 1 := ![![0]]
def c113_result : List (Test 3 1) := []
theorem c113_computed : fastPrimeDiscover 5 1 1
    (fun a => rowRight (c113_A a)) c113_O = some c113_result := by decide +kernel
theorem c113_code : FiniteCodeCertificate (linearSystem c113_A c113_O) c113_result :=
  fastPrimeDiscover_code 5 1 1 c113_A c113_O c113_result c113_computed

abbrev c114_R := ZMod (2^2)
def c114_A : Fin 1 → Mat c114_R 1 1 := ![![![3]]]
def c114_O : Mat c114_R 2 1 := ![![2], ![1]]
def c114_result : List (Test 1 2) := [([], 0), ([], 1)]
theorem c114_computed : fastPrimeDiscover 2 2 1
    (fun a => rowRight (c114_A a)) c114_O = some c114_result := by decide +kernel
theorem c114_code : FiniteCodeCertificate (linearSystem c114_A c114_O) c114_result :=
  fastPrimeDiscover_code 2 2 1 c114_A c114_O c114_result c114_computed

abbrev c115_R := ZMod (3^2)
def c115_A : Fin 2 → Mat c115_R 1 1 := ![![![0]], ![![1]]]
def c115_O : Mat c115_R 1 1 := ![![2]]
def c115_result : List (Test 2 1) := [([], 0)]
theorem c115_computed : fastPrimeDiscover 3 2 1
    (fun a => rowRight (c115_A a)) c115_O = some c115_result := by decide +kernel
theorem c115_code : FiniteCodeCertificate (linearSystem c115_A c115_O) c115_result :=
  fastPrimeDiscover_code 3 2 1 c115_A c115_O c115_result c115_computed

abbrev c116_R := ZMod (5^2)
def c116_A : Fin 3 → Mat c116_R 1 1 := ![![![1]], ![![10]], ![![16]]]
def c116_O : Mat c116_R 2 1 := ![![12], ![1]]
def c116_result : List (Test 3 2) := [([], 0)]
theorem c116_computed : fastPrimeDiscover 5 2 1
    (fun a => rowRight (c116_A a)) c116_O = some c116_result := by decide +kernel
theorem c116_code : FiniteCodeCertificate (linearSystem c116_A c116_O) c116_result :=
  fastPrimeDiscover_code 5 2 1 c116_A c116_O c116_result c116_computed

abbrev c117_R := ZMod (2^3)
def c117_A : Fin 1 → Mat c117_R 1 1 := ![![![2]]]
def c117_O : Mat c117_R 1 1 := ![![5]]
def c117_result : List (Test 1 1) := [([], 0)]
theorem c117_computed : fastPrimeDiscover 2 3 1
    (fun a => rowRight (c117_A a)) c117_O = some c117_result := by decide +kernel
theorem c117_code : FiniteCodeCertificate (linearSystem c117_A c117_O) c117_result :=
  fastPrimeDiscover_code 2 3 1 c117_A c117_O c117_result c117_computed

abbrev c118_R := ZMod (3^3)
def c118_A : Fin 2 → Mat c118_R 1 1 := ![![![13]], ![![25]]]
def c118_O : Mat c118_R 2 1 := ![![20], ![11]]
def c118_result : List (Test 2 2) := [([], 0)]
theorem c118_computed : fastPrimeDiscover 3 3 1
    (fun a => rowRight (c118_A a)) c118_O = some c118_result := by decide +kernel
theorem c118_code : FiniteCodeCertificate (linearSystem c118_A c118_O) c118_result :=
  fastPrimeDiscover_code 3 3 1 c118_A c118_O c118_result c118_computed

abbrev c119_R := ZMod (5^3)
def c119_A : Fin 3 → Mat c119_R 1 1 := ![![![60]], ![![100]], ![![84]]]
def c119_O : Mat c119_R 1 1 := ![![75]]
def c119_result : List (Test 3 1) := [([], 0)]
theorem c119_computed : fastPrimeDiscover 5 3 1
    (fun a => rowRight (c119_A a)) c119_O = some c119_result := by decide +kernel
theorem c119_code : FiniteCodeCertificate (linearSystem c119_A c119_O) c119_result :=
  fastPrimeDiscover_code 5 3 1 c119_A c119_O c119_result c119_computed

end Komorebi.EchelonRegression.EchelonComputed09
